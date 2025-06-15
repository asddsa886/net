"""
Web界面模块
提供实时监控界面、数据可视化和系统控制面板
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import os

# 导入其他模块
from ssn_modeling import SSNModeling
from data_collector import DataCollector
from event_processor import EventProcessor
from llm_composer import LLMServiceComposer

class WebInterface:
    """Web界面类"""
    
    def __init__(self, config_path: str = "config/service_config.json"):
        """
        初始化Web界面
        
        Args:
            config_path: 服务配置文件路径
        """
        self.config = self._load_config(config_path)
        web_config = self.config.get('web_interface', {})
        
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"当前目录: {current_dir}")
        
        # 获取项目根目录（src的上一级目录）
        project_root = os.path.dirname(current_dir)
        print(f"项目根目录: {project_root}")
        
        # 构建模板和静态文件路径
        template_dir = os.path.join(project_root, 'templates')
        static_dir = os.path.join(project_root, 'static')
        
        print(f"模板目录: {template_dir}")
        print(f"静态文件目录: {static_dir}")
        print(f"模板文件存在: {os.path.exists(os.path.join(template_dir, 'dashboard.html'))}")
        

        
        # Flask应用配置
        self.app = Flask(__name__, 
                        template_folder=template_dir,
                        static_folder=static_dir)
        CORS(self.app)
        self.app.config['DEBUG'] = web_config.get('debug', True)
        
        # 服务组件
        self.ssn_model = SSNModeling()
        self.data_collector = DataCollector()
        self.event_processor = EventProcessor()
        self.llm_composer = LLMServiceComposer()
        
        # 界面配置
        self.host = web_config.get('host', '0.0.0.0')
        self.port = web_config.get('port', 5000)
        self.refresh_interval = web_config.get('dashboard_refresh_interval', 2)
        
        # 系统状态
        self.system_status = {
            'running': False,
            'start_time': None,
            'data_collection_active': False,
            'total_events_processed': 0,
            'total_compositions_created': 0
        }
        
        # 事件收集
        self.all_events = []  # 收集所有事件（包括复杂事件）
        
        # 设置路由
        self._setup_routes()
        
        # 设置事件订阅
        self._setup_event_subscriptions()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    def _load_html_template(self) -> str:
        """从外部文件加载HTML模板"""
        try:
            # 获取项目根目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            template_path = os.path.join(project_root, 'templates', 'dashboard.html')
            
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            # 如果文件不存在，返回默认模板
            return self._get_default_template()
        
    def _setup_routes(self):
        """设置Web路由"""
        
        @self.app.route('/')
        def dashboard():
            return render_template('dashboard.html')
        
        @self.app.route('/composition_result')
        def composition_result():
            """服务组合详情页面"""
            return render_template('composition_result.html')
    
        @self.app.route('/api/system/status')
        def get_system_status():
            """获取系统状态"""
            status = {
                **self.system_status,
                'current_time': datetime.now().isoformat(),
                'uptime': self._calculate_uptime(),
                'collector_stats': self.data_collector.get_statistics(),
                'processor_stats': self.event_processor.get_event_statistics(),
                'composer_stats': self.llm_composer.get_statistics()
            }
            return jsonify(status)
        
        @self.app.route('/api/sensors/data')
        def get_sensor_data():
            """获取传感器数据"""
            recent_data = self.data_collector.get_recent_data(hours=1)
            formatted_data = self._format_sensor_data(recent_data)
            return jsonify(formatted_data)
        
        @self.app.route('/api/sensors/realtime')
        def get_realtime_data():
            """获取实时传感器数据"""
            current_readings = self.data_collector.collect_all_sensors()
            return jsonify(current_readings)
        
        @self.app.route('/api/events/recent')
        def get_recent_events():
            """获取最近事件"""
            # 返回所有收集的事件（包括复杂事件）
            recent_events = self.all_events[-20:] if self.all_events else []
            return jsonify(recent_events)
        
        @self.app.route('/api/sensors/status')
        def get_sensors_status():
            """获取传感器状态"""
            status_summary = self.event_processor.get_sensor_status_summary()
            return jsonify(status_summary)
        
        @self.app.route('/api/services/available')
        def get_available_services():
            """获取可用服务列表"""
            services = self.llm_composer.get_available_services()
            return jsonify(services)
        
        @self.app.route('/api/compositions/create', methods=['POST'])
        def create_composition():
            """创建服务组合"""
            try:
                data = request.get_json()
                target_goal = data.get('target_goal', '')
                sensor_data = data.get('sensor_data', {})
                constraints = data.get('constraints', [])
                
                print(f"创建服务组合: 目标需求={target_goal}, 传感器数据={sensor_data}, 约束={constraints}")

                composition = self.llm_composer.compose_services(
                    target_goal=target_goal,
                    sensor_data=sensor_data,
                    constraints=constraints
                )
                
                
                self.system_status['total_compositions_created'] += 1

            

                return jsonify(composition)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/compositions/history')
        def get_composition_history():
            """获取服务组合历史"""
            history = self.llm_composer.get_composition_history()
            return jsonify(history)
        
        @self.app.route('/api/system/start', methods=['POST'])
        def start_system():
            """启动系统"""
            try:
                if not self.system_status['running']:
                    self.data_collector.start_continuous_collection()
                    self.system_status['running'] = True
                    self.system_status['start_time'] = datetime.now().isoformat()
                    self.system_status['data_collection_active'] = True
                    
                return jsonify({'status': 'success', 'message': '系统已启动'})
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)}), 500
        
        @self.app.route('/api/system/stop', methods=['POST'])
        def stop_system():
            """停止系统"""
            try:
                if self.system_status['running']:
                    self.data_collector.stop_continuous_collection()
                    self.system_status['running'] = False
                    self.system_status['data_collection_active'] = False
                    
                return jsonify({'status': 'success', 'message': '系统已停止'})
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)}), 500
        
        @self.app.route('/api/troubleshoot', methods=['POST'])
        def troubleshoot():
            """故障排除"""
            try:
                data = request.get_json()
                problem_description = data.get('problem_description', '')
                error_messages = data.get('error_messages', [])
                related_services = data.get('related_services', [])
                
                result = self.llm_composer.troubleshoot_composition(
                    problem_description=problem_description,
                    error_messages=error_messages,
                    related_services=related_services
                )
                
                return jsonify(result)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def _setup_event_subscriptions(self):
        """设置事件订阅"""
        def on_semantic_event(event):
            """处理语义事件"""
            # 添加原始事件到事件列表
            self.all_events.append(event)
            
            # 处理复杂事件
            complex_events = self.event_processor.process_semantic_event(event)
            
            # 添加复杂事件到事件列表
            self.all_events.extend(complex_events)
            
            # 限制事件列表大小，避免内存溢出
            if len(self.all_events) > 1000:
                self.all_events = self.all_events[-500:]
            
            self.system_status['total_events_processed'] += 1 + len(complex_events)
            
            # 打印复杂事件信息（用于调试）
            for complex_event in complex_events:
                print(f"生成复杂事件: {complex_event.get('eventType', '未知')} - {complex_event.get('details', {}).get('description', '')}")
        
        def on_complex_event(event):
            """处理复杂事件"""
            # 这里可以添加复杂事件的特殊处理逻辑
            print(f"收到复杂事件通知: {event.get('eventType', '未知')}")
        
        # 订阅事件
        self.data_collector.subscribe_to_events(on_semantic_event)
        self.event_processor.subscribe_to_complex_events(on_complex_event)
    
    def _format_sensor_data(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """格式化传感器数据用于图表显示"""
        formatted = {
            'timestamps': [],
            'temperature': [],
            'humidity': [],
            'smoke': [],
            'motion': [],
            'light': []
        }
        
        for reading in raw_data:
            timestamp = reading.get('resultTime', '')
            sensor_id = reading.get('madeBySensor', '')
            value = reading.get('hasResult', {}).get('value', 0)
            
            if timestamp:
                formatted['timestamps'].append(timestamp)
                
                if 'temperature' in sensor_id.lower():
                    formatted['temperature'].append(value)
                elif 'humidity' in sensor_id.lower():
                    formatted['humidity'].append(value)
                elif 'smoke' in sensor_id.lower():
                    formatted['smoke'].append(value)
                elif 'motion' in sensor_id.lower():
                    formatted['motion'].append(value)
                elif 'light' in sensor_id.lower():
                    formatted['light'].append(value)
        
        return formatted
    
    def _calculate_uptime(self) -> str:
        """计算系统运行时间"""
        if not self.system_status['start_time']:
            return "未启动"
        
        start_time = datetime.fromisoformat(self.system_status['start_time'])
        uptime = datetime.now() - start_time
        
        hours = uptime.seconds // 3600
        minutes = (uptime.seconds % 3600) // 60
        seconds = uptime.seconds % 60
        
        return f"{uptime.days}天 {hours:02d}:{minutes:02d}:{seconds:02d}"
    
    
    def run(self):
        """启动Web界面"""
        print(f"启动Web界面: http://{self.host}:{self.port}")
        print("按 Ctrl+C 停止服务器")
        
        self.app.run(
            host=self.host,
            port=self.port,
            debug=False,  # 在线程中运行时关闭调试模式
            threaded=True,
            use_reloader=False  # 关闭自动重载
        )
    def start(self):
        """启动Web服务器"""
        print(f"Web界面服务器启动在 http://{self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=False)
    
    def stop(self):
        """停止Web服务器"""
        # Flask的停止需要特殊处理，这里简化处理
        pass

# 使用示例
if __name__ == "__main__":
    # 创建Web界面
    web_interface = WebInterface()
    
    # 启动Web服务器
    web_interface.start
