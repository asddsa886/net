"""
数据采集服务模块
实现传感器数据采集、语义事件生成和实时数据流处理
"""

import json
import random
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Callable, Optional
from queue import Queue
import os
import pandas as pd
from ssn_modeling import SSNModeling

class DataCollector:
    """数据采集服务类"""
    
    def __init__(self, config_path: str = "config/service_config.json"):
        """
        初始化数据采集器
        
        Args:
            config_path: 服务配置文件路径
        """
        self.config = self._load_config(config_path)
        self.ssn_model = SSNModeling()
        self.is_running = False
        self.data_queue = Queue()
        self.event_queue = Queue()
        self.subscribers = []
        self.collected_data = []
        
        # 数据采集配置
        self.sampling_interval = self.config.get('data_collection', {}).get('sampling_interval', 5)
        self.batch_size = self.config.get('data_collection', {}).get('batch_size', 10)
        self.real_time_processing = self.config.get('data_collection', {}).get('real_time_processing', True)
        
        # 创建数据存储目录
        self._ensure_data_directories()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _ensure_data_directories(self):
        """确保数据目录存在"""
        directories = ['data/raw', 'data/processed', 'data/events']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def simulate_sensor_data(self, sensor_id: str) -> Optional[float]:
        """
        模拟传感器数据
        
        Args:
            sensor_id: 传感器ID
            
        Returns:
            模拟的传感器值
        """
        sensor_info = self.ssn_model.get_sensor_info(sensor_id)
        if not sensor_info:
            return None
        
        # 根据传感器类型生成模拟数据
        if 'Temperature' in sensor_id:
            # 温度传感器：20-30°C之间，有一定波动
            base_temp = 25.0
            variation = random.uniform(-3.0, 5.0)
            # 添加时间因素（夜晚温度稍低）
            hour = datetime.now().hour
            if 22 <= hour or hour <= 6:
                variation -= 2.0
            return round(base_temp + variation, 1)
            
        elif 'Humidity' in sensor_id:
            # 湿度传感器：40-80%之间
            base_humidity = 60.0
            variation = random.uniform(-15.0, 20.0)
            return max(0, min(100, round(base_humidity + variation, 1)))
            
        elif 'Smoke' in sensor_id:
            # 烟雾传感器：通常很低，偶尔有峰值
            if random.random() < 0.05:  # 5%概率产生烟雾事件
                return random.uniform(150, 300)
            else:
                return random.uniform(0, 50)
                
        elif 'Motion' in sensor_id:
            # 人体感应器：0或1
            # 白天活动概率高，夜晚低
            hour = datetime.now().hour
            if 7 <= hour <= 22:
                return 1 if random.random() < 0.3 else 0
            else:
                return 1 if random.random() < 0.1 else 0
                
        elif 'Light' in sensor_id:
            # 光照传感器：根据时间模拟
            hour = datetime.now().hour
            if 6 <= hour <= 18:
                # 白天：300-1000 lux
                return random.uniform(300, 1000)
            elif 19 <= hour <= 22:
                # 傍晚：50-300 lux
                return random.uniform(50, 300)
            else:
                # 夜晚：1-50 lux
                return random.uniform(1, 50)
        
        return random.uniform(0, 100)  # 默认值
    
    def collect_single_reading(self, sensor_id: str) -> Optional[Dict[str, Any]]:
        """
        采集单个传感器读数
        
        Args:
            sensor_id: 传感器ID
            
        Returns:
            传感器读数数据
        """
        value = self.simulate_sensor_data(sensor_id)
        if value is None:
            return None
        
        # 验证数据有效性
        if not self.ssn_model.validate_sensor_value(sensor_id, value):
            print(f"警告: 传感器 {sensor_id} 的值 {value} 超出有效范围")
        
        # 创建观测记录
        observation = self.ssn_model.create_observation(sensor_id, value)
        
        # 添加额外信息
        reading = {
            **observation,
            "quality": self._assess_data_quality(sensor_id, value),
            "anomaly": self._detect_anomaly(sensor_id, value),
            "collected_at": datetime.now().isoformat()
        }
        
        return reading
    
    def _assess_data_quality(self, sensor_id: str, value: float) -> str:
        """评估数据质量"""
        if not self.ssn_model.validate_sensor_value(sensor_id, value):
            return "poor"
        
        # 简单的质量评估逻辑
        sensor_info = self.ssn_model.get_sensor_info(sensor_id)
        properties = sensor_info.get('properties', {})
        range_info = properties.get('range', {})
        
        if 'min' in range_info and 'max' in range_info:
            range_size = range_info['max'] - range_info['min']
            # 如果值在中间80%范围内，认为质量好
            middle_min = range_info['min'] + 0.1 * range_size
            middle_max = range_info['max'] - 0.1 * range_size
            
            if middle_min <= value <= middle_max:
                return "good"
            else:
                return "fair"
        
        return "good"
    
    def _detect_anomaly(self, sensor_id: str, value: float) -> bool:
        """检测异常值"""
        # 简单的异常检测：基于历史数据的统计分析
        if len(self.collected_data) < 10:
            return False
        
        # 获取该传感器的历史数据
        sensor_data = [
            reading for reading in self.collected_data[-50:]
            if reading.get('madeBySensor') == sensor_id
        ]
        
        if len(sensor_data) < 5:
            return False
        
        # 计算统计参数
        values = [reading['hasResult']['value'] for reading in sensor_data]
        mean_val = sum(values) / len(values)
        variance = sum((x - mean_val) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        
        # 3-sigma规则检测异常
        if abs(value - mean_val) > 3 * std_dev:
            return True
        
        return False
    
    def collect_all_sensors(self) -> List[Dict[str, Any]]:
        """采集所有传感器数据"""
        readings = []
        sensors = self.ssn_model.ssn_config.get('sensors', [])
        
        for sensor in sensors:
            reading = self.collect_single_reading(sensor['id'])
            if reading:
                readings.append(reading)
        
        return readings
    
    def generate_semantic_events(self, readings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        生成语义事件
        
        Args:
            readings: 传感器读数列表
            
        Returns:
            语义事件列表
        """
        events = []
        
        for reading in readings:
            # 基础语义事件
            base_event = {
                "id": f"event_{reading['id']}",
                "type": "SemanticEvent",
                "eventType": "SensorReading",
                "source": reading['madeBySensor'],
                "timestamp": reading['resultTime'],
                "data": reading,
                "semantics": {
                    "property": reading['observedProperty'].split(':')[-1],
                    "location": self._get_sensor_location(reading['madeBySensor']),
                    "value_interpretation": self._interpret_value(reading)
                }
            }
            events.append(base_event)
            
            # 特殊条件下的语义事件
            special_events = self._generate_special_events(reading)
            events.extend(special_events)
        
        return events
    
    def _get_sensor_location(self, sensor_id: str) -> str:
        """获取传感器位置"""
        sensor_info = self.ssn_model.get_sensor_info(sensor_id)
        return sensor_info.get('location', '未知')
    
    def _interpret_value(self, reading: Dict[str, Any]) -> str:
        """解释传感器值"""
        value = reading['hasResult']['value']
        sensor_id = reading['madeBySensor']
        
        if 'Temperature' in sensor_id:
            if value < 18:
                return "偏冷"
            elif value > 28:
                return "偏热"
            else:
                return "适宜"
                
        elif 'Humidity' in sensor_id:
            if value < 40:
                return "干燥"
            elif value > 70:
                return "潮湿"
            else:
                return "适宜"
                
        elif 'Smoke' in sensor_id:
            if value > 200:
                return "高浓度"
            elif value > 100:
                return "中等浓度"
            else:
                return "正常"
                
        elif 'Motion' in sensor_id:
            return "有人活动" if value > 0 else "无人活动"
            
        elif 'Light' in sensor_id:
            if value < 50:
                return "昏暗"
            elif value > 500:
                return "明亮"
            else:
                return "适中"
        
        return "正常"
    
    def _generate_special_events(self, reading: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成特殊语义事件"""
        events = []
        value = reading['hasResult']['value']
        sensor_id = reading['madeBySensor']
        
        # 异常值事件
        if reading.get('anomaly', False):
            events.append({
                "id": f"anomaly_{reading['id']}",
                "type": "SemanticEvent",
                "eventType": "AnomalyDetected",
                "source": sensor_id,
                "timestamp": reading['resultTime'],
                "severity": "medium",
                "description": f"检测到异常值: {value}"
            })
        
        # 阈值事件
        threshold_events = self._check_thresholds(sensor_id, value, reading['resultTime'])
        events.extend(threshold_events)
        
        return events
    
    def _check_thresholds(self, sensor_id: str, value: float, timestamp: str) -> List[Dict[str, Any]]:
        """检查阈值并生成事件"""
        events = []
        
        # 定义阈值规则
        thresholds = {
            'temperatureSensor_001': {'high': 30, 'low': 15},
            'humiditySensor_001': {'high': 80, 'low': 30},
            'smokeSensor_001': {'high': 200, 'low': None},
            'lightSensor_001': {'high': 1000, 'low': 10}
        }
        
        sensor_key = sensor_id.split(':')[-1]
        if sensor_key in thresholds:
            threshold_config = thresholds[sensor_key]
            
            if threshold_config.get('high') and value > threshold_config['high']:
                events.append({
                    "id": f"threshold_high_{sensor_id}_{int(datetime.fromisoformat(timestamp).timestamp())}",
                    "type": "SemanticEvent",
                    "eventType": "ThresholdExceeded",
                    "source": sensor_id,
                    "timestamp": timestamp,
                    "threshold_type": "high",
                    "threshold_value": threshold_config['high'],
                    "actual_value": value,
                    "severity": "high" if 'smoke' in sensor_id.lower() else "medium"
                })
            
            if threshold_config.get('low') and value < threshold_config['low']:
                events.append({
                    "id": f"threshold_low_{sensor_id}_{int(datetime.fromisoformat(timestamp).timestamp())}",
                    "type": "SemanticEvent",
                    "eventType": "ThresholdExceeded",
                    "source": sensor_id,
                    "timestamp": timestamp,
                    "threshold_type": "low",
                    "threshold_value": threshold_config['low'],
                    "actual_value": value,
                    "severity": "medium"
                })
        
        return events
    
    def subscribe_to_events(self, callback: Callable[[Dict[str, Any]], None]):
        """
        订阅事件通知
        
        Args:
            callback: 事件回调函数
        """
        self.subscribers.append(callback)
    
    def _notify_subscribers(self, event: Dict[str, Any]):
        """通知所有订阅者"""
        for callback in self.subscribers:
            try:
                callback(event)
            except Exception as e:
                print(f"事件通知错误: {e}")
    
    def start_continuous_collection(self):
        """开始连续数据采集"""
        if self.is_running:
            print("数据采集已在运行中")
            return
        
        self.is_running = True
        collection_thread = threading.Thread(target=self._collection_loop)
        collection_thread.daemon = True
        collection_thread.start()
        
        if self.real_time_processing:
            processing_thread = threading.Thread(target=self._processing_loop)
            processing_thread.daemon = True
            processing_thread.start()
        
        print(f"数据采集已启动，采样间隔: {self.sampling_interval}秒")
    
    def _collection_loop(self):
        """数据采集循环"""
        while self.is_running:
            try:
                # 采集所有传感器数据
                readings = self.collect_all_sensors()
                
                # 存储数据
                self.collected_data.extend(readings)
                
                # 限制内存中数据量
                if len(self.collected_data) > 1000:
                    self.collected_data = self.collected_data[-500:]
                
                # 将数据加入队列进行处理
                for reading in readings:
                    self.data_queue.put(reading)
                
                # 批量保存数据
                if len(readings) > 0:
                    self._save_raw_data(readings)
                
                time.sleep(self.sampling_interval)
                
            except Exception as e:
                print(f"数据采集错误: {e}")
                time.sleep(self.sampling_interval)
    
    def _processing_loop(self):
        """数据处理循环"""
        batch = []
        while self.is_running:
            try:
                # 收集批量数据
                while len(batch) < self.batch_size and not self.data_queue.empty():
                    batch.append(self.data_queue.get())
                
                if batch:
                    # 生成语义事件
                    events = self.generate_semantic_events(batch)
                    
                    # 处理事件
                    for event in events:
                        self.event_queue.put(event)
                        self._notify_subscribers(event)
                    
                    # 保存处理后的数据和事件
                    self._save_processed_data(batch)
                    self._save_events(events)
                    
                    batch = []
                
                time.sleep(1)  # 短暂等待
                
            except Exception as e:
                print(f"数据处理错误: {e}")
                time.sleep(1)
    
    def stop_continuous_collection(self):
        """停止连续数据采集"""
        self.is_running = False
        print("数据采集已停止")
    
    def _save_raw_data(self, readings: List[Dict[str, Any]]):
        """保存原始数据"""
        timestamp = datetime.now().strftime("%Y%m%d_%H")
        filename = f"data/raw/sensor_data_{timestamp}.json"
        
        # 读取现有数据
        existing_data = []
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except:
                existing_data = []
        
        # 添加新数据
        existing_data.extend(readings)
        
        # 保存数据
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
    
    def _save_processed_data(self, readings: List[Dict[str, Any]]):
        """保存处理后的数据"""
        timestamp = datetime.now().strftime("%Y%m%d_%H")
        filename = f"data/processed/processed_data_{timestamp}.json"
        
        # 添加处理信息
        processed_readings = []
        for reading in readings:
            processed_reading = {
                **reading,
                "processed_at": datetime.now().isoformat(),
                "processing_version": "1.0"
            }
            processed_readings.append(processed_reading)
        
        # 读取现有数据并追加
        existing_data = []
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except:
                existing_data = []
        
        existing_data.extend(processed_readings)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
    
    def _save_events(self, events: List[Dict[str, Any]]):
        """保存事件数据"""
        timestamp = datetime.now().strftime("%Y%m%d_%H")
        filename = f"data/events/events_{timestamp}.json"
        
        # 读取现有事件并追加
        existing_events = []
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    existing_events = json.load(f)
            except:
                existing_events = []
        
        existing_events.extend(events)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(existing_events, f, ensure_ascii=False, indent=2)
    
    def get_recent_data(self, hours: int = 1) -> List[Dict[str, Any]]:
        """获取最近的数据"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_data = []
        for reading in self.collected_data:
            reading_time = datetime.fromisoformat(reading['resultTime'])
            if reading_time >= cutoff_time:
                recent_data.append(reading)
        
        return recent_data
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取采集统计信息"""
        return {
            "总采集数据量": len(self.collected_data),
            "队列中数据量": self.data_queue.qsize(),
            "队列中事件量": self.event_queue.qsize(),
            "是否运行中": self.is_running,
            "订阅者数量": len(self.subscribers),
            "采样间隔": self.sampling_interval,
            "批处理大小": self.batch_size
        }

# 使用示例
if __name__ == "__main__":
    # 创建数据采集器
    collector = DataCollector()
    
    # 设置事件订阅
    def event_handler(event):
        print(f"收到事件: {event['eventType']} - {event.get('description', '')}")
    
    collector.subscribe_to_events(event_handler)
    
    # 单次采集演示
    print("=== 单次数据采集演示 ===")
    readings = collector.collect_all_sensors()
    for reading in readings:
        print(f"传感器: {reading['madeBySensor']}")
        print(f"值: {reading['hasResult']['value']} {reading['hasResult']['unit']}")
        print(f"质量: {reading['quality']}")
        print("---")
    
    # 生成语义事件
    events = collector.generate_semantic_events(readings)
    print(f"\n生成了 {len(events)} 个语义事件")
    
    # 启动连续采集（演示5秒）
    print("\n=== 启动连续采集演示 ===")
    collector.start_continuous_collection()
    time.sleep(10)
    collector.stop_continuous_collection()
    
    # 显示统计信息
    print("\n=== 采集统计信息 ===")
    stats = collector.get_statistics()
    print(json.dumps(stats, indent=2, ensure_ascii=False))
