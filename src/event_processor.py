"""
事件处理模块
实现原子语义事件识别、复杂事件推理和事件关联分析
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from collections import defaultdict, deque
import threading
from queue import Queue

class EventProcessor:
    """事件处理器类"""
    
    def __init__(self, config_path: str = "config/service_config.json"):
        """
        初始化事件处理器
        
        Args:
            config_path: 服务配置文件路径
        """
        self.config = self._load_config(config_path)
        self.event_rules = self.config.get('event_processing', {}).get('complex_event_rules', [])
        
        # 事件存储和处理
        self.event_history = deque(maxlen=1000)  # 限制历史事件数量
        self.active_patterns = {}  # 活跃的事件模式
        self.complex_events = []  # 生成的复杂事件
        
        # 时间窗口管理
        self.time_windows = defaultdict(deque)  # 按时间窗口存储事件
        
        # 事件订阅
        self.subscribers = []
        
        # 状态管理
        self.sensor_states = {}  # 传感器状态跟踪
        self.location_states = {}  # 位置状态跟踪
        
        # 处理线程控制
        self.is_running = False
        self.event_queue = Queue()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def process_semantic_event(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        处理语义事件
        
        Args:
            event: 输入的语义事件
            
        Returns:
            生成的复杂事件列表
        """
        # 存储事件到历史记录
        self.event_history.append(event)
        
        # 更新传感器状态
        self._update_sensor_state(event)
        
        # 更新位置状态
        self._update_location_state(event)
        
        # 识别原子语义事件
        atomic_events = self._identify_atomic_events(event)
        
        # 复杂事件推理
        complex_events = self._perform_complex_reasoning(event)
        
        # 事件关联分析
        correlated_events = self._analyze_event_correlations(event)
        
        # 合并所有生成的复杂事件
        all_complex_events = atomic_events + complex_events + correlated_events
        
        # 通知订阅者
        for complex_event in all_complex_events:
            self._notify_subscribers(complex_event)
        
        return all_complex_events
    
    def _update_sensor_state(self, event: Dict[str, Any]):
        """更新传感器状态"""
        if event.get('eventType') == 'SensorReading':
            sensor_id = event.get('source', '')
            if 'data' in event and 'hasResult' in event['data']:
                value = event['data']['hasResult']['value']
                timestamp = event.get('timestamp', '')
                
                self.sensor_states[sensor_id] = {
                    'last_value': value,
                    'last_update': timestamp,
                    'trend': self._calculate_trend(sensor_id, value),
                    'status': 'normal'  # normal, warning, critical
                }
    
    def _calculate_trend(self, sensor_id: str, current_value: float) -> str:
        """计算传感器数值趋势"""
        if sensor_id not in self.sensor_states:
            return 'stable'
        
        last_value = self.sensor_states[sensor_id].get('last_value', current_value)
        
        if abs(current_value - last_value) < 0.1:
            return 'stable'
        elif current_value > last_value:
            return 'rising'
        else:
            return 'falling'
    
    def _update_location_state(self, event: Dict[str, Any]):
        """更新位置状态"""
        if 'semantics' in event and 'location' in event['semantics']:
            location = event['semantics']['location']
            timestamp = event.get('timestamp', '')
            
            if location not in self.location_states:
                self.location_states[location] = {
                    'sensors': set(),
                    'last_activity': timestamp,
                    'activity_level': 'normal',
                    'events_count': 0
                }
            
            self.location_states[location]['sensors'].add(event.get('source', ''))
            self.location_states[location]['last_activity'] = timestamp
            self.location_states[location]['events_count'] += 1
    
    def _identify_atomic_events(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """识别原子语义事件"""
        atomic_events = []
        
        # 阈值突破事件
        if event.get('eventType') == 'ThresholdExceeded':
            atomic_event = {
                'id': f"atomic_{event['id']}",
                'type': 'AtomicSemanticEvent',
                'eventType': 'ThresholdBreached',
                'source': event.get('source', ''),
                'timestamp': event.get('timestamp', ''),
                'severity': event.get('severity', 'medium'),
                'details': {
                    'threshold_type': event.get('threshold_type', ''),
                    'threshold_value': event.get('threshold_value', 0),
                    'actual_value': event.get('actual_value', 0),
                    'deviation': abs(event.get('actual_value', 0) - event.get('threshold_value', 0))
                }
            }
            atomic_events.append(atomic_event)
        
        # 异常检测事件  
        elif event.get('eventType') == 'AnomalyDetected':
            atomic_event = {
                'id': f"atomic_{event['id']}",
                'type': 'AtomicSemanticEvent',
                'eventType': 'AnomalyIdentified',
                'source': event.get('source', ''),
                'timestamp': event.get('timestamp', ''),
                'severity': event.get('severity', 'medium'),
                'details': {
                    'anomaly_type': 'statistical',
                    'description': event.get('description', '')
                }
            }
            atomic_events.append(atomic_event)
        
        # 状态变化事件
        elif event.get('eventType') == 'SensorReading':
            state_change = self._detect_state_change(event)
            if state_change:
                atomic_events.append(state_change)
        
        return atomic_events
    
    def _detect_state_change(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """检测状态变化"""
        sensor_id = event.get('source', '')
        if 'semantics' in event and 'value_interpretation' in event['semantics']:
            current_interpretation = event['semantics']['value_interpretation']
            
            # 检查是否有状态变化
            if sensor_id in self.sensor_states:
                last_state = self.sensor_states[sensor_id].get('last_interpretation', '')
                if last_state and last_state != current_interpretation:
                    return {
                        'id': f"state_change_{sensor_id}_{int(time.time())}",
                        'type': 'AtomicSemanticEvent',
                        'eventType': 'StateChange',
                        'source': sensor_id,
                        'timestamp': event.get('timestamp', ''),
                        'severity': 'low',
                        'details': {
                            'from_state': last_state,
                            'to_state': current_interpretation,
                            'location': event.get('semantics', {}).get('location', '')
                        }
                    }
            
            # 更新解释状态
            if sensor_id in self.sensor_states:
                self.sensor_states[sensor_id]['last_interpretation'] = current_interpretation
        
        return None
    
    def _perform_complex_reasoning(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """执行复杂事件推理"""
        complex_events = []
        
        # 遍历所有复杂事件规则
        for rule in self.event_rules:
            complex_event = self._evaluate_complex_rule(event, rule)
            if complex_event:
                complex_events.append(complex_event)
        
        return complex_events
    
    def _evaluate_complex_rule(self, event: Dict[str, Any], rule: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """评估复杂事件规则"""
        rule_name = rule.get('name', '')
        conditions = rule.get('conditions', [])
        
        # 检查当前事件是否触发规则
        if not self._check_rule_conditions(event, conditions):
            return None
        
        # 根据规则类型生成复杂事件
        if rule_name == 'fire_alarm':
            return self._generate_fire_alarm_event(event, rule)
        elif rule_name == 'comfort_control':
            return self._generate_comfort_control_event(event, rule)
        elif rule_name == 'energy_saving':
            return self._generate_energy_saving_event(event, rule)
        
        return None
    
    def _check_rule_conditions(self, event: Dict[str, Any], conditions: List[Dict[str, Any]]) -> bool:
        """检查规则条件"""
        current_sensor = event.get('source', '')
        current_time = datetime.fromisoformat(event.get('timestamp', ''))
        
        satisfied_conditions = 0
        
        for condition in conditions:
            sensor_key = condition.get('sensor', '')
            operator = condition.get('operator', '')
            threshold = condition.get('threshold', 0)
            duration = condition.get('duration', 0)
            
            # 检查当前事件是否满足条件
            if sensor_key in current_sensor:
                if 'data' in event and 'hasResult' in event['data']:
                    value = event['data']['hasResult']['value']
                    if self._evaluate_condition(value, operator, threshold):
                        satisfied_conditions += 1
                        continue
            
            # 检查历史数据中的其他传感器
            if self._check_historical_condition(sensor_key, operator, threshold, duration, current_time):
                satisfied_conditions += 1
        
        # 所有条件都满足才触发复杂事件
        return satisfied_conditions == len(conditions)
    
    def _evaluate_condition(self, value: float, operator: str, threshold: float) -> bool:
        """评估单个条件"""
        if operator == '>':
            return value > threshold
        elif operator == '<':
            return value < threshold
        elif operator == '>=':
            return value >= threshold
        elif operator == '<=':
            return value <= threshold
        elif operator == '==':
            return abs(value - threshold) < 0.01
        elif operator == '!=':
            return abs(value - threshold) >= 0.01
        
        return False
    
    def _check_historical_condition(self, sensor_key: str, operator: str, threshold: float, 
                                  duration: int, current_time: datetime) -> bool:
        """检查历史数据中的条件"""
        cutoff_time = current_time - timedelta(seconds=duration) if duration > 0 else current_time - timedelta(minutes=5)
        
        for historical_event in reversed(self.event_history):
            if sensor_key not in historical_event.get('source', ''):
                continue
            
            event_time = datetime.fromisoformat(historical_event.get('timestamp', ''))
            if event_time < cutoff_time:
                break
            
            if 'data' in historical_event and 'hasResult' in historical_event['data']:
                value = historical_event['data']['hasResult']['value']
                if self._evaluate_condition(value, operator, threshold):
                    return True
        
        return False
    
    def _generate_fire_alarm_event(self, event: Dict[str, Any], rule: Dict[str, Any]) -> Dict[str, Any]:
        """生成火灾报警复杂事件"""
        return {
            'id': f"fire_alarm_{int(time.time())}",
            'type': 'ComplexEvent',
            'eventType': 'FireAlarmTriggered',
            'priority': rule.get('priority', 'high'),
            'severity': 'critical',
            'timestamp': datetime.now().isoformat(),
            'source': 'EventProcessor',
            'trigger_event': event['id'],
            'details': {
                'description': '检测到火灾风险：烟雾和温度同时超标',
                'location': event.get('semantics', {}).get('location', ''),
                'recommended_actions': [
                    '立即疏散人员',
                    '联系消防部门',
                    '关闭电源和燃气',
                    '启动消防系统'
                ],
                'affected_sensors': self._get_affected_sensors(event, 'fire')
            }
        }
    
    def _generate_comfort_control_event(self, event: Dict[str, Any], rule: Dict[str, Any]) -> Dict[str, Any]:
        """生成舒适度控制复杂事件"""
        return {
            'id': f"comfort_control_{int(time.time())}",
            'type': 'ComplexEvent',
            'eventType': 'ComfortControlNeeded',
            'priority': rule.get('priority', 'medium'),
            'severity': 'medium',
            'timestamp': datetime.now().isoformat(),
            'source': 'EventProcessor',
            'trigger_event': event['id'],
            'details': {
                'description': '环境舒适度需要调节：温度和湿度不适宜',
                'location': event.get('semantics', {}).get('location', ''),
                'recommended_actions': [
                    '调节空调温度',
                    '启动除湿/加湿设备',
                    '调整通风系统'
                ],
                'target_ranges': {
                    'temperature': '20-26°C',
                    'humidity': '40-60%RH'
                }
            }
        }
    
    def _generate_energy_saving_event(self, event: Dict[str, Any], rule: Dict[str, Any]) -> Dict[str, Any]:
        """生成节能模式复杂事件"""
        return {
            'id': f"energy_saving_{int(time.time())}",
            'type': 'ComplexEvent',
            'eventType': 'EnergySavingTriggered',
            'priority': rule.get('priority', 'low'),
            'severity': 'low',
            'timestamp': datetime.now().isoformat(),
            'source': 'EventProcessor',
            'trigger_event': event['id'],
            'details': {
                'description': '长时间无人活动，建议启动节能模式',
                'location': event.get('semantics', {}).get('location', ''),
                'recommended_actions': [
                    '降低照明亮度',
                    '调整空调温度',
                    '关闭非必要设备',
                    '启动待机模式'
                ],
                'estimated_savings': '15-30%'
            }
        }
    
    def _get_affected_sensors(self, event: Dict[str, Any], event_type: str) -> List[str]:
        """获取受影响的传感器列表"""
        location = event.get('semantics', {}).get('location', '')
        affected_sensors = []
        
        # 根据位置和事件类型确定相关传感器
        for sensor_id, state in self.sensor_states.items():
            if event_type == 'fire':
                if 'smoke' in sensor_id.lower() or 'temperature' in sensor_id.lower():
                    affected_sensors.append(sensor_id)
            elif event_type == 'comfort':
                if 'temperature' in sensor_id.lower() or 'humidity' in sensor_id.lower():
                    affected_sensors.append(sensor_id)
        
        return affected_sensors
    
    def _analyze_event_correlations(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析事件关联"""
        correlated_events = []
        
        # 时间关联分析
        temporal_correlations = self._find_temporal_correlations(event)
        correlated_events.extend(temporal_correlations)
        
        # 空间关联分析
        spatial_correlations = self._find_spatial_correlations(event)
        correlated_events.extend(spatial_correlations)
        
        # 因果关联分析
        causal_correlations = self._find_causal_correlations(event)
        correlated_events.extend(causal_correlations)
        
        return correlated_events
    
    def _find_temporal_correlations(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """寻找时间关联"""
        correlations = []
        current_time = datetime.fromisoformat(event.get('timestamp', ''))
        time_window = timedelta(minutes=5)  # 5分钟时间窗口
        
        # 查找时间窗口内的相关事件
        related_events = []
        for historical_event in reversed(self.event_history):
            event_time = datetime.fromisoformat(historical_event.get('timestamp', ''))
            if current_time - event_time > time_window:
                break
            
            if (historical_event.get('eventType') == event.get('eventType') and
                historical_event.get('id') != event.get('id')):
                related_events.append(historical_event)
        
        # 如果找到多个相关事件，生成关联事件
        if len(related_events) >= 2:
            correlations.append({
                'id': f"temporal_correlation_{int(time.time())}",
                'type': 'CorrelationEvent',
                'eventType': 'TemporalCorrelation',
                'timestamp': datetime.now().isoformat(),
                'source': 'EventProcessor',
                'details': {
                    'correlation_type': 'temporal',
                    'trigger_event': event['id'],
                    'related_events': [e['id'] for e in related_events],
                    'time_window': f"{time_window.seconds}秒",
                    'pattern': f"在{time_window.seconds}秒内发生{len(related_events)+1}次相同类型事件"
                }
            })
        
        return correlations
    
    def _find_spatial_correlations(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """寻找空间关联"""
        correlations = []
        event_location = event.get('semantics', {}).get('location', '')
        
        if not event_location:
            return correlations
        
        # 查找同一位置的其他活跃事件
        location_events = []
        # 将deque转换为list以支持切片操作
        recent_events = list(self.event_history)[-20:] if len(self.event_history) > 20 else list(self.event_history)
        for historical_event in recent_events:
            if (historical_event.get('semantics', {}).get('location', '') == event_location and
                historical_event.get('id') != event.get('id')):
                location_events.append(historical_event)
        
        if len(location_events) >= 3:
            correlations.append({
                'id': f"spatial_correlation_{int(time.time())}",
                'type': 'CorrelationEvent',
                'eventType': 'SpatialCorrelation',
                'timestamp': datetime.now().isoformat(),
                'source': 'EventProcessor',
                'details': {
                    'correlation_type': 'spatial',
                    'location': event_location,
                    'trigger_event': event['id'],
                    'related_events': [e['id'] for e in location_events],
                    'pattern': f"{event_location}位置活动频繁，发生{len(location_events)+1}个事件"
                }
            })
        
        return correlations
    
    def _find_causal_correlations(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """寻找因果关联"""
        correlations = []
        
        # 简单的因果关系检测
        if event.get('eventType') == 'ThresholdExceeded':
            sensor_id = event.get('source', '')
            
            # 查找可能的因果关系
            if 'temperature' in sensor_id.lower():
                # 温度异常可能导致舒适度问题
                recent_events = list(self.event_history)[-10:] if len(self.event_history) > 10 else list(self.event_history)
                for historical_event in recent_events:
                    if (historical_event.get('eventType') == 'SensorReading' and
                        'humidity' in historical_event.get('source', '').lower()):
                        correlations.append({
                            'id': f"causal_correlation_{int(time.time())}",
                            'type': 'CorrelationEvent',
                            'eventType': 'CausalCorrelation',
                            'timestamp': datetime.now().isoformat(),
                            'source': 'EventProcessor',
                            'details': {
                                'correlation_type': 'causal',
                                'cause_event': event['id'],
                                'effect_hypothesis': '温度异常可能影响整体舒适度',
                                'confidence': 0.7
                            }
                        })
                        break
        
        return correlations
    
    def subscribe_to_complex_events(self, callback: Callable[[Dict[str, Any]], None]):
        """
        订阅复杂事件通知
        
        Args:
            callback: 复杂事件回调函数
        """
        self.subscribers.append(callback)
    
    def _notify_subscribers(self, complex_event: Dict[str, Any]):
        """通知所有订阅者"""
        for callback in self.subscribers:
            try:
                callback(complex_event)
            except Exception as e:
                print(f"复杂事件通知错误: {e}")
    
    def get_event_statistics(self) -> Dict[str, Any]:
        """获取事件处理统计信息"""
        event_types = defaultdict(int)
        severity_counts = defaultdict(int)
        
        for event in self.event_history:
            event_types[event.get('eventType', 'unknown')] += 1
            severity_counts[event.get('severity', 'unknown')] += 1
        
        return {
            '历史事件总数': len(self.event_history),
            '复杂事件总数': len(self.complex_events),
            '活跃传感器数': len(self.sensor_states),
            '监控位置数': len(self.location_states),
            '事件类型分布': dict(event_types),
            '严重程度分布': dict(severity_counts),
            '订阅者数量': len(self.subscribers)
        }
    
    def get_sensor_status_summary(self) -> Dict[str, Any]:
        """获取传感器状态摘要"""
        return {
            sensor_id: {
                '最新值': state.get('last_value', 'N/A'),
                '更新时间': state.get('last_update', 'N/A'),
                '趋势': state.get('trend', 'unknown'),
                '状态': state.get('status', 'unknown')
            }
            for sensor_id, state in self.sensor_states.items()
        }
    
    def clear_history(self, older_than_hours: int = 24):
        """清理历史数据"""
        cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
        
        # 清理事件历史
        filtered_events = deque()
        for event in self.event_history:
            try:
                event_time = datetime.fromisoformat(event.get('timestamp', ''))
                if event_time >= cutoff_time:
                    filtered_events.append(event)
            except:
                continue
        
        self.event_history = filtered_events
        print(f"已清理{older_than_hours}小时前的历史数据")

# 使用示例
if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from data_collector import DataCollector
    
    # 创建事件处理器
    processor = EventProcessor()
    
    # 设置复杂事件订阅
    def complex_event_handler(event):
        print(f"复杂事件: {event['eventType']} - {event.get('details', {}).get('description', '')}")
    
    processor.subscribe_to_complex_events(complex_event_handler)
    
    # 创建数据采集器来生成测试事件
    collector = DataCollector()
    
    print("=== 事件处理演示 ===")
    
    # 生成测试数据和事件
    readings = collector.collect_all_sensors()
    events = collector.generate_semantic_events(readings)
    
    # 处理语义事件
    for event in events:
        complex_events = processor.process_semantic_event(event)
        if complex_events:
            print(f"处理事件 {event['eventType']} -> 生成 {len(complex_events)} 个复杂事件")
    
    # 显示统计信息
    print("\n=== 事件处理统计 ===")
    stats = processor.get_event_statistics()
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    print("\n=== 传感器状态摘要 ===")
    sensor_summary = processor.get_sensor_status_summary()
    print(json.dumps(sensor_summary, indent=2, ensure_ascii=False))
