"""
Web界面模块
提供实时监控界面、数据可视化和系统控制面板
"""

from flask import Flask, render_template_string, jsonify, request
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
        
        # Flask应用配置
        self.app = Flask(__name__)
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
    
    def _setup_routes(self):
        """设置Web路由"""
        
        @self.app.route('/')
        def dashboard():
            """主控制台页面"""
            return render_template('dashboard.html')
        
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
            # 获取最近的事件（这里简化为从事件处理器获取）
            recent_events = list(self.event_processor.event_history)[-20:]
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
            complex_events = self.event_processor.process_semantic_event(event)
            self.system_status['total_events_processed'] += 1 + len(complex_events)
        
        def on_complex_event(event):
            """处理复杂事件"""
            # 这里可以添加复杂事件的特殊处理逻辑
            pass
        
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
    
    def _get_dashboard_template(self) -> str:
        """获取仪表板HTML模板"""
        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>智能家居监控系统</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .header h1 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        
        .control-panel {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }
        
        .btn-primary {
            background: #3498db;
            color: white;
        }
        
        .btn-danger {
            background: #e74c3c;
            color: white;
        }
        
        .btn-success {
            background: #27ae60;
            color: white;
        }
        
        .btn:hover {
            opacity: 0.8;
            transform: translateY(-2px);
        }
        
        .status {
            margin-left: 20px;
            padding: 10px 15px;
            border-radius: 5px;
            font-weight: bold;
        }
        
        .status.running {
            background: #d5f4e6;
            color: #27ae60;
        }
        
        .status.stopped {
            background: #fadbd8;
            color: #e74c3c;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .card h3 {
            color: #2c3e50;
            margin-bottom: 15px;
            border-bottom: 2px solid #3498db;
            padding-bottom: 5px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }
        
        .stat-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #3498db;
        }
        
        .stat-label {
            color: #7f8c8d;
            margin-top: 5px;
        }
        
        .chart-container {
            position: relative;
            height: 300px;
            margin-top: 10px;
        }
        
        .sensor-status {
            margin-top: 10px;
        }
        
        .sensor-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            margin: 5px 0;
            background: #f8f9fa;
            border-radius: 5px;
        }
        
        .sensor-value {
            font-weight: bold;
            color: #2c3e50;
        }
        
        .event-list {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .event-item {
            padding: 10px;
            margin: 5px 0;
            border-left: 4px solid #3498db;
            background: #f8f9fa;
            border-radius: 0 5px 5px 0;
        }
        
        .event-time {
            font-size: 0.8em;
            color: #7f8c8d;
        }
        
        .service-composition {
            margin-top: 20px;
        }
        
        .composition-form {
            margin-top: 15px;
        }

        .composition-details {
            margin-top: 20px;
            padding: 15px;
            background-color: #f9f9f9;
            border: 1px solid #eee;
            border-radius: 5px;
        }
        .composition-details h5 {
            margin-top: 15px;
            margin-bottom: 5px;
            color: #3498db;
        }
        .composition-details p {
            margin-bottom: 8px;
            line-height: 1.6;
        }
        .composition-details ul {
            list-style-type: disc;
            margin-left: 20px;
            padding-left: 0;
        }
        .composition-details ul li {
            margin-bottom: 5px;
        }
        .service-list li {
            background-color: #fff;
            border: 1px solid #ddd;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 4px;
        }
        .service-list li strong {
            font-size: 1.1em;
            color: #2c3e50;
        }
        details {
            margin-top: 15px;
        }
        details summary {
            cursor: pointer;
            font-weight: bold;
            color: #3498db;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        
        .form-group input,
        .form-group textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        
        .form-group textarea {
            resize: vertical;
            min-height: 80px;
        }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #3498db;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .hidden {
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏠 智能家居监控系统</h1>
            <div class="control-panel">
                <button id="startBtn" class="btn btn-success">启动系统</button>
                <button id="stopBtn" class="btn btn-danger">停止系统</button>
                <button id="refreshBtn" class="btn btn-primary">刷新数据</button>
                <div id="systemStatus" class="status stopped">系统已停止</div>
            </div>
        </div>
        
        <div class="dashboard">
            <!-- 系统统计 -->
            <div class="card">
                <h3>📊 系统统计</h3>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div id="uptimeValue" class="stat-value">00:00:00</div>
                        <div class="stat-label">运行时间</div>
                    </div>
                    <div class="stat-item">
                        <div id="eventsValue" class="stat-value">0</div>
                        <div class="stat-label">处理事件</div>
                    </div>
                    <div class="stat-item">
                        <div id="sensorsValue" class="stat-value">5</div>
                        <div class="stat-label">活跃传感器</div>
                    </div>
                    <div class="stat-item">
                        <div id="compositionsValue" class="stat-value">0</div>
                        <div class="stat-label">服务组合</div>
                    </div>
                </div>
            </div>
            
            <!-- 传感器状态 -->
            <div class="card">
                <h3>🌡️ 传感器状态</h3>
                <div id="sensorStatus" class="sensor-status">
                    加载中...
                </div>
            </div>
            
            <!-- 实时数据图表 -->
            <div class="card">
                <h3>📈 实时数据</h3>
                <div class="chart-container">
                    <canvas id="sensorChart"></canvas>
                </div>
            </div>
            
            <!-- 最近事件 -->
            <div class="card">
                <h3>🔔 最近事件</h3>
                <div id="eventList" class="event-list">
                    暂无事件
                </div>
            </div>
        </div>
        
        <!-- 服务组合 -->
        <div class="card service-composition">
            <h3>🔧 服务组合</h3>
            <div class="composition-form">
                <div class="form-group">
                    <label for="targetGoal">目标需求：</label>
                    <textarea id="targetGoal" placeholder="描述您想要实现的智能家居功能..."></textarea>
                </div>
                <div class="form-group">
                    <label for="constraints">约束条件：</label>
                    <input type="text" id="constraints" placeholder="例如：响应时间<30秒,误报率<5%">
                </div>
                <button id="composeBtn" class="btn btn-primary">生成服务组合</button>
                <div id="compositionLoading" class="loading hidden"></div>
            </div>
            <div id="compositionResult" class="hidden">
                <h4>组合结果：</h4>
                <pre id="compositionData"></pre>
            </div>
        </div>
    </div>

    <script>
        // 全局变量
        let chart = null;
        let refreshInterval = null;
        
        // 存储历史数据
        let sensorHistory = {
            timestamps: [],
            temperature: [],
            humidity: [],
            light: []
        };
        
        const maxDataPoints = 5; // 最多显示5个数据点
        
        // DOM元素
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        const refreshBtn = document.getElementById('refreshBtn');
        const systemStatus = document.getElementById('systemStatus');
        const composeBtn = document.getElementById('composeBtn');
        
        // 初始化
        document.addEventListener('DOMContentLoaded', function() {
            initChart();
            setupEventListeners();
            refreshData();
            startAutoRefresh();
        });
        
        // 设置事件监听器
        function setupEventListeners() {
            startBtn.addEventListener('click', startSystem);
            stopBtn.addEventListener('click', stopSystem);
            refreshBtn.addEventListener('click', refreshData);
            composeBtn.addEventListener('click', createComposition);
        }
        
        // 启动系统
        async function startSystem() {
            try {
                const response = await fetch('/api/system/start', {
                    method: 'POST'
                });
                const result = await response.json();
                
                if (result.status === 'success') {
                    updateSystemStatus(true);
                    showNotification('系统启动成功', 'success');
                } else {
                    showNotification('系统启动失败: ' + result.message, 'error');
                }
            } catch (error) {
                showNotification('启动请求失败: ' + error.message, 'error');
            }
        }
        
        // 停止系统
        async function stopSystem() {
            try {
                const response = await fetch('/api/system/stop', {
                    method: 'POST'
                });
                const result = await response.json();
                
                if (result.status === 'success') {
                    updateSystemStatus(false);
                    showNotification('系统停止成功', 'success');
                } else {
                    showNotification('系统停止失败: ' + result.message, 'error');
                }
            } catch (error) {
                showNotification('停止请求失败: ' + error.message, 'error');
            }
        }
        
        // 更新系统状态显示
        function updateSystemStatus(running) {
            if (running) {
                systemStatus.textContent = '系统运行中';
                systemStatus.className = 'status running';
            } else {
                systemStatus.textContent = '系统已停止';
                systemStatus.className = 'status stopped';
            }
        }
        
        // 刷新数据
        async function refreshData() {
            try {
                await Promise.all([
                    updateSystemStats(),
                    updateSensorStatus(),
                    updateSensorChart(),
                    updateEventList()
                ]);
            } catch (error) {
                console.error('数据刷新失败:', error);
            }
        }
        
        // 更新系统统计
        async function updateSystemStats() {
            try {
                const response = await fetch('/api/system/status');
                const status = await response.json();
                
                document.getElementById('uptimeValue').textContent = status.uptime || '00:00:00';
                document.getElementById('eventsValue').textContent = status.total_events_processed || 0;
                document.getElementById('compositionsValue').textContent = status.total_compositions_created || 0;
                
                updateSystemStatus(status.running);
            } catch (error) {
                console.error('获取系统状态失败:', error);
            }
        }
        
        // 更新传感器状态
        async function updateSensorStatus() {
            try {
                const response = await fetch('/api/sensors/status');
                const status = await response.json();
                
                const statusContainer = document.getElementById('sensorStatus');
                statusContainer.innerHTML = '';
                
                for (const [sensorId, sensorData] of Object.entries(status)) {
                    const sensorDiv = document.createElement('div');
                    sensorDiv.className = 'sensor-item';
                    
                    const sensorName = sensorId.split(':')[1] || sensorId;
                    sensorDiv.innerHTML = `
                        <span>${sensorName}</span>
                        <span class="sensor-value">${sensorData['最新值'] || 'N/A'}</span>
                    `;
                    
                    statusContainer.appendChild(sensorDiv);
                }
            } catch (error) {
                console.error('获取传感器状态失败:', error);
            }
        }
        
        // 初始化图表
        function initChart() {
            const ctx = document.getElementById('sensorChart').getContext('2d');
            chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: '温度 (°C)',
                            data: [],
                            borderColor: '#e74c3c',
                            backgroundColor: 'rgba(231, 76, 60, 0.1)',
                            tension: 0.4
                        },
                        {
                            label: '湿度 (%)',
                            data: [],
                            borderColor: '#3498db',
                            backgroundColor: 'rgba(52, 152, 219, 0.1)',
                            tension: 0.4
                        },
                        {
                            label: '光照 (lux)',
                            data: [],
                            borderColor: '#f39c12',
                            backgroundColor: 'rgba(243, 156, 18, 0.1)',
                            tension: 0.4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top'
                        }
                    }
                }
            });
        }
        
        // 更新传感器图表
        async function updateSensorChart() {
            try {
                const response = await fetch('/api/sensors/realtime');
                const readings = await response.json();
                
                const now = new Date();
                const currentTime = now.toLocaleTimeString();
                
                // 获取当前读数
                let currentTemp = null;
                let currentHumid = null;
                let currentLight = null;
                
                readings.forEach(reading => {
                    const value = reading.hasResult.value;
                    const sensorId = reading.madeBySensor;
                    
                    if (sensorId.includes('temperature')) {
                        currentTemp = value;
                    } else if (sensorId.includes('humidity')) {
                        currentHumid = value;
                    } else if (sensorId.includes('light')) {
                        currentLight = value;
                    }
                });
                
                // 添加新数据点到历史记录
                if (currentTemp !== null || currentHumid !== null || currentLight !== null) {
                    sensorHistory.timestamps.push(currentTime);
                    sensorHistory.temperature.push(currentTemp || 0);
                    sensorHistory.humidity.push(currentHumid || 0);
                    sensorHistory.light.push(currentLight || 0);
                    
                    // 限制历史数据点数量
                    if (sensorHistory.timestamps.length > maxDataPoints) {
                        sensorHistory.timestamps.shift();
                        sensorHistory.temperature.shift();
                        sensorHistory.humidity.shift();
                        sensorHistory.light.shift();
                    }
                }
                
                // 更新图表数据
                chart.data.labels = sensorHistory.timestamps;
                chart.data.datasets[0].data = sensorHistory.temperature;
                chart.data.datasets[1].data = sensorHistory.humidity;
                chart.data.datasets[2].data = sensorHistory.light;
                
                chart.update('none'); // 使用 'none' 模式获得更好的性能
            } catch (error) {
                console.error('更新传感器图表失败:', error);
            }
        }
        
        // 更新事件列表
        async function updateEventList() {
            try {
                const response = await fetch('/api/events/recent');
                const events = await response.json();
                
                const eventContainer = document.getElementById('eventList');
                eventContainer.innerHTML = '';
                
                if (events.length === 0) {
                    eventContainer.innerHTML = '<div>暂无事件</div>';
                    return;
                }
                
                events.slice(-10).reverse().forEach(event => {
                    const eventDiv = document.createElement('div');
                    eventDiv.className = 'event-item';
                    
                    const eventTime = new Date(event.timestamp).toLocaleString();
                    const eventType = event.eventType || '未知事件';
                    const description = event.description || event.semantics?.value_interpretation || '';
                    
                    eventDiv.innerHTML = `
                        <div><strong>${eventType}</strong></div>
                        <div>${description}</div>
                        <div class="event-time">${eventTime}</div>
                    `;
                    
                    eventContainer.appendChild(eventDiv);
                });
            } catch (error) {
                console.error('更新事件列表失败:', error);
            }
        }
        
        // 创建服务组合
        async function createComposition() {
            const targetGoal = document.getElementById('targetGoal').value.trim();
            const constraintsInput = document.getElementById('constraints').value.trim();
            
            if (!targetGoal) {
                showNotification('请输入目标需求', 'error');
                return;
            }
            
            const constraints = constraintsInput ? constraintsInput.split(',').map(s => s.trim()) : [];
            
            // 显示加载状态
            composeBtn.disabled = true;
            document.getElementById('compositionLoading').classList.remove('hidden');
            document.getElementById('compositionResult').classList.add('hidden');
            
            try {
                // 首先获取最新的传感器数据
                const sensorResponse = await fetch('/api/sensors/realtime');
                const sensorReadings = await sensorResponse.json();
                
                // 格式化传感器数据为更友好的格式
                const sensorData = {};
                sensorReadings.forEach(reading => {
                    const sensorId = reading.madeBySensor;
                    const value = reading.hasResult.value;
                    const unit = reading.hasResult.unit;
                    
                    if (sensorId.includes('temperature')) {
                        sensorData.temperature = value;
                        sensorData.temperature_unit = unit;
                    } else if (sensorId.includes('humidity')) {
                        sensorData.humidity = value;
                        sensorData.humidity_unit = unit;
                    } else if (sensorId.includes('smoke')) {
                        sensorData.smoke_level = value;
                        sensorData.smoke_unit = unit;
                    } else if (sensorId.includes('motion')) {
                        sensorData.motion_detected = value > 0;
                    } else if (sensorId.includes('light')) {
                        sensorData.light_level = value;
                        sensorData.light_unit = unit;
                    }
                });
                
                // 添加时间戳和环境描述
                sensorData.timestamp = new Date().toISOString();
                sensorData.environment_summary = generateEnvironmentSummary(sensorData);
                
                const response = await fetch('/api/compositions/create', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        target_goal: targetGoal,
                        sensor_data: sensorData,
                        constraints: constraints
                    })
                });
                
                const composition = await response.json();
                
                if (composition.error) {
                    showNotification('服务组合失败: ' + composition.error, 'error');
                } else {
                    // 显示组合结果
                    displayCompositionResult(composition);
                    document.getElementById('compositionResult').classList.remove('hidden');
                    showNotification('服务组合创建成功', 'success');
                }
            } catch (error) {
                showNotification('创建服务组合失败: ' + error.message, 'error');
            } finally {
                composeBtn.disabled = false;
                document.getElementById('compositionLoading').classList.add('hidden');
            }
        }
        // 显示服务组合结果
        function displayCompositionResult(composition) {
            const resultContainer = document.getElementById('compositionData');
            
            if (!composition || composition.error) {
                resultContainer.textContent = '组合失败: ' + (composition.error || '未知错误');
                return;
            }
            
            // 格式化显示组合结果
            let resultHTML = '';
            
            if (composition.workflow) {
                resultHTML += `<div class="composition-details">`;
                resultHTML += `<h5>🔧 工作流程:</h5>`;
                resultHTML += `<p>${composition.workflow}</p>`;
                
                if (composition.services && composition.services.length > 0) {
                    resultHTML += `<h5>🔗 涉及服务:</h5>`;
                    resultHTML += `<ul class="service-list">`;
                    composition.services.forEach(service => {
                        resultHTML += `<li>`;
                        resultHTML += `<strong>${service.name || '未命名服务'}</strong><br>`;
                        resultHTML += `描述: ${service.description || '无描述'}<br>`;
                        if (service.endpoint) {
                            resultHTML += `端点: ${service.endpoint}<br>`;
                        }
                        if (service.parameters) {
                            resultHTML += `参数: ${JSON.stringify(service.parameters)}<br>`;
                        }
                        resultHTML += `</li>`;
                    });
                    resultHTML += `</ul>`;
                }
                
                if (composition.execution_plan) {
                    resultHTML += `<h5>📋 执行计划:</h5>`;
                    if (Array.isArray(composition.execution_plan)) {
                        resultHTML += `<ol>`;
                        composition.execution_plan.forEach(step => {
                            resultHTML += `<li>${step}</li>`;
                        });
                        resultHTML += `</ol>`;
                    } else {
                        resultHTML += `<p>${composition.execution_plan}</p>`;
                    }
                }
                
                if (composition.expected_outcome) {
                    resultHTML += `<h5>🎯 预期结果:</h5>`;
                    resultHTML += `<p>${composition.expected_outcome}</p>`;
                }
                
                if (composition.constraints_satisfied) {
                    resultHTML += `<h5>✅ 约束满足情况:</h5>`;
                    if (Array.isArray(composition.constraints_satisfied)) {
                        resultHTML += `<ul>`;
                        composition.constraints_satisfied.forEach(constraint => {
                            resultHTML += `<li>${constraint}</li>`;
                        });
                        resultHTML += `</ul>`;
                    } else {
                        resultHTML += `<p>${composition.constraints_satisfied}</p>`;
                    }
                }
                
                resultHTML += `</div>`;
                
                // 添加调试信息
                resultHTML += `<details style="margin-top: 15px;">`;
                resultHTML += `<summary>查看原始数据</summary>`;
                resultHTML += `<pre style="background-color: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto;">${JSON.stringify(composition, null, 2)}</pre>`;
                resultHTML += `</details>`;
            } else {
                // 如果没有workflow字段，显示原始JSON
                resultHTML = `<pre style="background-color: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto;">${JSON.stringify(composition, null, 2)}</pre>`;
            }
            
            resultContainer.innerHTML = resultHTML;
        }
        
        // 显示通知
        function showNotification(message, type) {
            // 简单的通知实现
            const notification = document.createElement('div');
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px 20px;
                border-radius: 5px;
                color: white;
                font-weight: bold;
                z-index: 1000;
                opacity: 0;
                transition: opacity 0.3s;
            `;
            
            if (type === 'success') {
                notification.style.backgroundColor = '#27ae60';
            } else {
                notification.style.backgroundColor = '#e74c3c';
            }
            
            notification.textContent = message;
            document.body.appendChild(notification);
            
            // 显示动画
            setTimeout(() => {
                notification.style.opacity = '1';
            }, 100);
            
            // 自动隐藏
            setTimeout(() => {
                notification.style.opacity = '0';
                setTimeout(() => {
                    document.body.removeChild(notification);
                }, 300);
            }, 3000);
        }
        
        // 生成环境摘要描述
        function generateEnvironmentSummary(sensorData) {
            const summaries = [];
            
            // 温度描述
            if (sensorData.temperature !== undefined) {
                const temp = sensorData.temperature;
                if (temp < 18) {
                    summaries.push(`环境偏冷(${temp}°C)`);
                } else if (temp > 28) {
                    summaries.push(`环境偏热(${temp}°C)`);
                } else {
                    summaries.push(`温度适宜(${temp}°C)`);
                }
            }
            
            // 湿度描述
            if (sensorData.humidity !== undefined) {
                const humidity = sensorData.humidity;
                if (humidity < 40) {
                    summaries.push(`空气干燥(${humidity}%)`);
                } else if (humidity > 70) {
                    summaries.push(`空气潮湿(${humidity}%)`);
                } else {
                    summaries.push(`湿度适宜(${humidity}%)`);
                }
            }
            
            // 光照描述
            if (sensorData.light_level !== undefined) {
                const light = sensorData.light_level;
                if (light < 100) {
                    summaries.push(`光线昏暗(${light}lux)`);
                } else if (light > 500) {
                    summaries.push(`光线明亮(${light}lux)`);
                } else {
                    summaries.push(`光照适中(${light}lux)`);
                }
            }
            
            // 运动检测描述
            if (sensorData.motion_detected !== undefined) {
                if (sensorData.motion_detected) {
                    summaries.push('检测到人员活动');
                } else {
                    summaries.push('无人员活动');
                }
            }
            
            // 烟雾检测描述
            if (sensorData.smoke_level !== undefined) {
                const smoke = sensorData.smoke_level;
                if (smoke > 200) {
                    summaries.push(`烟雾浓度偏高(${smoke}ppm)`);
                } else if (smoke > 100) {
                    summaries.push(`检测到轻微烟雾(${smoke}ppm)`);
                } else {
                    summaries.push('空气质量正常');
                }
            }
            
            return summaries.length > 0 ? summaries.join(', ') : '环境状态正常';
        }
        
        // 开始自动刷新
        function startAutoRefresh() {
            refreshInterval = setInterval(refreshData, 5000); // 每5秒刷新一次
        }
        
        // 页面卸载时清理
        window.addEventListener('beforeunload', function() {
            if (refreshInterval) {
                clearInterval(refreshInterval);
            }
        });
    </script>
</body>
</html>
        """
    
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
    web_interface.run()
