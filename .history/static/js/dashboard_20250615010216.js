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

function displayCompositionResult(composition) {
    const resultContainer = document.getElementById('compositionData');
    
    if (!composition || composition.error) {
        resultContainer.textContent = '组合失败: ' + (composition.error || '未知错误');
        return;
    }
    
    // 保存到sessionStorage
    sessionStorage.setItem('latestComposition', JSON.stringify(composition));
    
    // 添加查看详情按钮
    let resultHTML = `
        <div style="margin-bottom: 15px;">
            <button onclick="viewCompositionDetail()" class="btn btn-primary">📄 查看详细内容</button>
        </div>
    `;
    
    // 显示简要信息
    if (composition.workflow) {
        resultHTML += `<div class="composition-summary">`;
        resultHTML += `<h5>🔧 工作流程:</h5>`;
        resultHTML += `<p>${composition.workflow.substring(0, 200)}...</p>`;
        resultHTML += `</div>`;
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