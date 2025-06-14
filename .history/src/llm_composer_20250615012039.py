"""
大模型服务组合模块
基于大模型进行物联网服务组合，支持提示词工程和服务自动组合
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import requests
from dataclasses import dataclass
from openai import OpenAI



@dataclass
class IoTService:
    """物联网服务定义"""
    id: str
    name: str
    description: str
    inputs: List[str]
    outputs: List[str]
    category: str
    requirements: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'inputs': self.inputs,
            'outputs': self.outputs,
            'category': self.category,
            'requirements': self.requirements or []
        }

class LLMServiceComposer:
    """大模型服务组合器"""
    
    def __init__(self, config_path: str = "config/service_config.json"):
        """
        初始化服务组合器
        
        Args:
            config_path: 服务配置文件路径
        """
        self.config = self._load_config(config_path)
        self.llm_config = self.config.get('llm_service', {})
        
        # 可用服务库
        self.available_services = self._load_available_services()
        
        # 组合历史
        self.composition_history = []
        
        # 模型配置
        self.model_type = self.llm_config.get('model_type', 'gpt-3.5-turbo')
        self.api_key = self.llm_config.get('api_key', '')
        self.base_url = self.llm_config.get('base_url', 'https://api.openai.com/v1')
        self.max_tokens = self.llm_config.get('max_tokens', 1000)
        self.temperature = self.llm_config.get('temperature', 0.7)
        
        # 提示词模板
        self.prompt_templates = self._load_prompt_templates()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _load_available_services(self) -> List[IoTService]:
        """加载可用服务"""
        # 预定义的物联网服务
        services = [
            IoTService(
                id="temperature_monitor",
                name="温度监控服务",
                description="监控环境温度，提供实时温度数据和异常报警",
                inputs=["sensor_data"],
                outputs=["temperature_value", "temperature_status", "alert"],
                category="monitoring"
            ),
            IoTService(
                id="humidity_control",
                name="湿度控制服务",
                description="控制环境湿度，自动调节加湿/除湿设备",
                inputs=["humidity_data", "target_humidity"],
                outputs=["control_command", "adjustment_status"],
                category="control"
            ),
            IoTService(
                id="fire_detection",
                name="火灾检测服务",
                description="基于烟雾和温度传感器检测火灾风险",
                inputs=["smoke_data", "temperature_data"],
                outputs=["fire_risk_level", "emergency_alert"],
                category="safety"
            ),
            IoTService(
                id="energy_optimization",
                name="能源优化服务",
                description="基于占用情况和环境条件优化能源使用",
                inputs=["motion_data", "light_data", "schedule"],
                outputs=["energy_plan", "device_commands"],
                category="optimization"
            ),
            IoTService(
                id="comfort_management",
                name="舒适度管理服务",
                description="综合管理温度、湿度、光照，维持舒适环境",
                inputs=["temperature_data", "humidity_data", "light_data", "user_preferences"],
                outputs=["comfort_score", "adjustment_recommendations"],
                category="comfort"
            ),
            IoTService(
                id="security_monitoring",
                name="安全监控服务",
                description="监控人员活动，检测异常行为",
                inputs=["motion_data", "door_sensor", "time_schedule"],
                outputs=["security_status", "intrusion_alert"],
                category="security"
            ),
            IoTService(
                id="data_analytics",
                name="数据分析服务",
                description="分析传感器数据趋势，提供洞察和预测",
                inputs=["historical_data", "sensor_readings"],
                outputs=["trend_analysis", "predictions", "insights"],
                category="analytics"
            ),
            IoTService(
                id="notification_service",
                name="通知服务",
                description="发送各种类型的通知和警报",
                inputs=["alert_data", "notification_config"],
                outputs=["notification_sent", "delivery_status"],
                category="communication"
            ),
            IoTService(
                id="device_control",
                name="设备控制服务",
                description="控制各种智能设备的开关和参数",
                inputs=["device_id", "control_command", "parameters"],
                outputs=["execution_status", "device_response"],
                category="control"
            ),
            IoTService(
                id="scheduling_service",
                name="调度服务",
                description="根据时间表和条件自动执行任务",
                inputs=["schedule_config", "trigger_conditions"],
                outputs=["scheduled_tasks", "execution_log"],
                category="automation"
            )
        ]
        
        return services
    
def _load_prompt_templates(self) -> Dict[str, str]:
    """加载提示词模板"""
    return {
        "service_composition": """
你是一个专业的智能家居系统架构师。请根据以下信息设计一个完整的服务组合方案，并以详细的Markdown格式输出。

**目标需求：**
{target_goal}

**当前传感器数据：**
{sensor_data}

**可用服务列表：**
{available_services}

**约束条件：**
{constraints}

请按照以下Markdown格式提供详细的服务组合方案：

# 🏠 智能家居服务组合方案

## 📋 方案概述

### 基本信息
- **方案名称**: [为方案起一个专业的名称]
- **方案编号**: [生成唯一编号，如 IHCS-2025-001]
- **设计目标**: [详细描述要达成的目标]
- **适用场景**: [描述适合使用的具体场景]
- **预期效果**: [量化的预期效果和收益]

### 当前环境分析
基于传感器数据分析：
{sensor_data}

- **环境状态评估**: [对当前环境的综合评价]
- **关键指标**: [列出关键的环境指标]
- **优化空间**: [指出可以优化的方向]

## 🔧 服务架构设计

### 核心服务组件
[为每个选中的服务提供详细说明]

#### 1. [服务名称]
- **功能描述**: [详细功能说明]
- **输入数据**: [输入数据类型和来源]
- **输出结果**: [输出数据和格式]
- **优先级**: [1-5级，说明优先级理由]
- **依赖关系**: [依赖的其他服务]
- **配置要求**: [关键配置参数]

### 服务组合架构图
```mermaid
graph TB
    subgraph "数据采集层"
        A[温度传感器] --> D[数据预处理]
        B[湿度传感器] --> D
        C[其他传感器] --> D
    end
    
    subgraph "服务处理层"
        D --> E[监控服务]
        E --> F[分析服务]
        F --> G[决策服务]
    end
    
    subgraph "执行控制层"
        G --> H[设备控制]
        G --> I[通知服务]
    end
    
    subgraph "用户界面层"
        H --> J[用户界面]
        I --> J
    end
```

### 数据流设计
```json
{{
  "composition_id": "[生成唯一ID]",
  "version": "1.0",
  "created_date": "{datetime.now().strftime('%Y-%m-%d')}",
  "services": [
    {{
      "service_id": "[服务ID]",
      "service_name": "[服务名称]",
      "category": "[服务类别]",
      "role": "[在组合中的作用]",
      "priority": "[1-5优先级]",
      "inputs": ["[输入数据列表]"],
      "outputs": ["[输出数据列表]"],
      "dependencies": ["[依赖服务列表]"],
      "configuration": {{
        "[配置参数]": "[参数值]"
      }},
      "performance_requirements": {{
        "response_time": "[响应时间要求]",
        "availability": "[可用性要求]",
        "throughput": "[吞吐量要求]"
      }}
    }}
  ],
  "execution_flow": "[详细的执行流程描述]",
  "data_flow": "[数据在各服务间的流转路径]",
  "error_handling": "[错误处理策略]"
}}
```

## 🚀 实施方案

### 第一阶段：基础设施部署 (第1-2周)
1. **环境准备**
   - 硬件设备检查与安装
   - 网络连接配置
   - 基础软件环境搭建

2. **核心服务部署**
   - [按优先级列出要部署的服务]
   - 配置管理和参数调优
   - 基础测试验证

### 第二阶段：服务集成 (第3-4周)
1. **服务间通信配置**
   - API接口配置
   - 数据格式标准化
   - 通信协议优化

2. **业务流程集成**
   - 工作流配置
   - 事件触发机制
   - 异常处理流程

### 第三阶段：系统优化 (第5-6周)
1. **性能调优**
   - 响应时间优化
   - 资源使用优化
   - 并发处理能力提升

2. **用户体验优化**
   - 界面交互优化
   - 个性化设置
   - 智能推荐功能

## 📊 性能指标与监控

### 关键性能指标 (KPI)
| 指标类别 | 具体指标 | 目标值 | 监控方式 | 报警阈值 |
|---------|---------|--------|----------|----------|
| 响应性能 | 平均响应时间 | < 2秒 | 实时监控 | > 5秒 |
| 系统可用性 | 服务可用率 | > 99.5% | 健康检查 | < 95% |
| 数据准确性 | 传感器数据准确率 | > 98% | 定期校验 | < 95% |
| 用户满意度 | 用户评分 | > 4.5/5 | 用户反馈 | < 4.0/5 |
| 资源利用 | CPU使用率 | < 70% | 系统监控 | > 85% |
| 能耗效率 | 能耗降低率 | > 15% | 能耗统计 | < 10% |

### 监控仪表板
- **实时状态监控**: 显示所有服务的运行状态
- **性能趋势分析**: 历史性能数据趋势图
- **异常事件日志**: 详细的异常事件记录
- **用户行为分析**: 用户使用模式和偏好

## ⚙️ 配置管理

### 环境配置
```yaml
# 系统环境配置
environment:
  name: "production"
  region: "home"
  timezone: "Asia/Shanghai"

# 传感器配置
sensors:
  temperature:
    type: "DHT22"
    location: "living_room"
    sample_rate: 30  # 秒
    calibration_offset: 0.5
  
  humidity:
    type: "DHT22"
    location: "living_room"
    sample_rate: 30
    calibration_offset: -2.0

# 服务配置
services:
  temperature_monitor:
    enabled: true
    alert_threshold:
      high: 28.0
      low: 18.0
    notification_delay: 300  # 秒
```

### 用户偏好配置
```yaml
user_preferences:
  comfort_settings:
    temperature_range: [22, 26]  # 舒适温度范围
    humidity_range: [40, 60]     # 舒适湿度范围
    auto_adjust: true            # 自动调节开关
  
  notification_settings:
    channels: ["mobile", "email"]
    quiet_hours: ["22:00", "07:00"]
    priority_filter: "high"
  
  energy_settings:
    saving_mode: "smart"
    schedule: 
      weekday: ["06:00-08:00", "18:00-23:00"]
      weekend: ["08:00-23:00"]
```

## 🔒 安全与可靠性

### 安全措施
1. **数据安全**
   - 传输加密: TLS 1.3
   - 存储加密: AES-256
   - 访问控制: RBAC模型

2. **设备安全**
   - 设备认证: 双因子认证
   - 固件更新: 自动安全更新
   - 网络隔离: VLAN隔离

3. **隐私保护**
   - 数据匿名化处理
   - 用户授权管理
   - 审计日志跟踪

### 故障处理机制
1. **自动故障恢复**
   - 服务健康检查
   - 自动重启机制
   - 故障转移策略

2. **备份与恢复**
   - 配置数据备份
   - 历史数据备份
   - 快速恢复流程

## 💰 成本效益分析

### 投资成本
| 成本类别 | 预算金额 | 说明 |
|---------|---------|------|
| 硬件设备 | ¥2,000 | 传感器、控制器等 |
| 软件许可 | ¥500 | 第三方软件授权 |
| 部署实施 | ¥1,000 | 人工成本 |
| 维护运营 | ¥300/月 | 持续运营成本 |

### 预期收益
- **能源节约**: 月节省电费 ¥200-300
- **舒适度提升**: 量化为用户满意度提升 20%
- **安全保障**: 降低安全风险，价值难以量化
- **投资回收期**: 预计 12-15 个月

## 📈 优化建议

### 短期优化 (1-3个月)
- **性能调优**: 优化算法参数，提升响应速度
- **用户体验**: 完善界面交互，增加个性化设置
- **数据质量**: 提升传感器数据准确性和可靠性

### 中期优化 (3-6个月)
- **智能化升级**: 引入机器学习算法，提升预测能力
- **功能扩展**: 增加新的传感器类型和控制设备
- **集成优化**: 与其他智能家居平台集成

### 长期规划 (6-12个月)
- **生态建设**: 构建开放的插件和扩展机制
- **数据价值**: 开发数据分析和洞察功能
- **社区建设**: 建立用户社区和知识分享平台

## 🛠️ 技术支持

### 部署指南
1. **系统要求**: [详细的系统要求说明]
2. **安装步骤**: [逐步安装指导]
3. **配置说明**: [关键配置参数说明]
4. **测试验证**: [功能测试检查清单]

### 故障排除
1. **常见问题**: [FAQ和常见问题解决]
2. **日志分析**: [日志文件位置和分析方法]
3. **性能诊断**: [性能问题诊断工具]
4. **联系支持**: [技术支持联系方式]

---

**📝 备注**: 本方案基于当前环境数据和用户需求设计，实际部署时请根据具体情况进行调整。建议在正式部署前进行小规模试点验证。

**🔄 更新记录**: 
- v1.0 ({datetime.now().strftime('%Y-%m-%d')}): 初始版本
- 后续版本将根据使用反馈持续优化

请严格按照以上Markdown格式输出，确保内容详实、结构清晰、格式规范。
""",
        # 其他模板保持不变...
    }
    
    def compose_services(self, target_goal: str, sensor_data: Dict[str, Any] = None, 
                        constraints: List[str] = None) -> Dict[str, Any]:
        """
        基于目标需求组合服务
        
        Args:
            target_goal: 目标需求描述
            sensor_data: 当前传感器数据
            constraints: 约束条件
            
        Returns:
            服务组合方案
        """
        print(f"🎯 开始生成服务组合...")
        print(f"📝 目标需求: {target_goal}")
        
        # 准备提示词
        prompt = self._prepare_composition_prompt(target_goal, sensor_data, constraints)
        
        # 调用大模型
        print(f"🤖 正在调用AI模型生成方案...")
        llm_response = self._call_llm(prompt)
        
        # 解析响应
        composition = self._parse_composition_response(llm_response)
        
        # # 验证组合可行性
        # validated_composition = self._validate_composition(composition)
        
        # # 美化输出结果
        # self._record_composition(validated_composition, target_goal)
        
        return llm_response
    
    def _prepare_composition_prompt(self, target_goal: str, sensor_data: Dict[str, Any] = None, 
                                  constraints: List[str] = None) -> str:
        """准备服务组合提示词"""
        # 格式化传感器数据
        sensor_data_str = json.dumps(sensor_data or {}, indent=2, ensure_ascii=False)
        
        # 格式化可用服务
        services_str = ""
        for service in self.available_services:
            services_str += f"- **{service.name}** ({service.id}): {service.description}\n"
            services_str += f"  输入: {', '.join(service.inputs)}\n"
            services_str += f"  输出: {', '.join(service.outputs)}\n"
            services_str += f"  类别: {service.category}\n\n"
        
        # 格式化约束条件
        constraints_str = "\n".join(f"- {constraint}" for constraint in (constraints or []))
        
        # 填充模板
        prompt = self.prompt_templates["service_composition"].format(
            target_goal=target_goal,
            sensor_data=sensor_data_str,
            available_services=services_str,
            constraints=constraints_str
        )
        print(prompt)
        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """调用大语言模型"""
        # 这里实现对不同LLM的调用
        # 为了演示，我们模拟一个响应
        if self.model_type.startswith('glm'):
            return self._call_openai_api(prompt)
        else:
            return self._simulate_llm_response(prompt)
    
    def _call_openai_api(self, prompt: str) -> str:
        """调用智谱 GLM-4 API"""
        if not self.api_key or self.api_key == "your-api-key-here":
            print("🔄 使用模拟响应模式（未配置有效API密钥）")
            return self._simulate_llm_response(prompt)
        
        try:
            # 使用智谱 GLM-4 API
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            completion = client.chat.completions.create(
                model="glm-4",
                messages=[
                    {"role": "system", "content": "你是一个智能家居系统的服务组合专家，请根据用户需求提供专业的服务组合方案。"},
                    {"role": "user", "content": prompt}
                ],
                top_p=0.7,
                temperature=0.9
            )
            
            print(f"✅ GLM-4 API调用成功")
            return completion.choices[0].message.content
                
        except Exception as e:
            print(f"❌ GLM-4 API调用异常: {e}")
            print("🔄 切换到模拟响应模式")
            return self._simulate_llm_response(prompt)
    
    def _simulate_llm_response(self, prompt: str) -> str:
        """模拟LLM响应（用于演示）"""
        # 根据提示词内容生成模拟响应
        if "火灾" in prompt or "fire" in prompt.lower():
            return self._generate_fire_safety_composition()
        elif "舒适" in prompt or "comfort" in prompt.lower():
            return self._generate_comfort_composition()
        elif "节能" in prompt or "energy" in prompt.lower():
            return self._generate_energy_composition()
        else:
            return self._generate_default_composition()
    
    def _generate_fire_safety_composition(self) -> str:
        """生成火灾安全服务组合示例"""
        return """
## 服务组合方案

### 1. 方案概述
- 方案名称：智能火灾安全防护系统
- 主要目标：实时监控火灾风险，快速响应和处理火灾事件
- 预期效果：提高火灾检测精度，缩短响应时间，保障人员安全

### 2. 服务组合
```json
{
  "composition_id": "fire_safety_system_001",
  "services": [
    {
      "service_id": "fire_detection",
      "service_name": "火灾检测服务",
      "role": "核心检测组件",
      "priority": 5,
      "inputs": ["smoke_data", "temperature_data"],
      "outputs": ["fire_risk_level", "emergency_alert"],
      "dependencies": []
    },
    {
      "service_id": "notification_service",
      "service_name": "通知服务",
      "role": "紧急通知",
      "priority": 5,
      "inputs": ["alert_data", "notification_config"],
      "outputs": ["notification_sent", "delivery_status"],
      "dependencies": ["fire_detection"]
    },
    {
      "service_id": "device_control",
      "service_name": "设备控制服务",
      "role": "安全设备控制",
      "priority": 4,
      "inputs": ["device_id", "control_command", "parameters"],
      "outputs": ["execution_status", "device_response"],
      "dependencies": ["fire_detection"]
    },
    {
      "service_id": "data_analytics",
      "service_name": "数据分析服务",
      "role": "风险评估",
      "priority": 3,
      "inputs": ["historical_data", "sensor_readings"],
      "outputs": ["trend_analysis", "predictions", "insights"],
      "dependencies": []
    }
  ],
  "execution_flow": "火灾检测服务持续监控 -> 检测到风险时触发通知服务和设备控制 -> 数据分析服务提供决策支持",
  "data_flow": "传感器数据 -> 火灾检测 -> 风险评估 -> 通知+控制指令"
}
```

### 3. 实施建议
- 部署顺序：数据分析服务 -> 火灾检测服务 -> 通知服务 -> 设备控制服务
- 配置要点：设置合理的阈值，配置多种通知渠道，确保设备控制的可靠性
- 监控指标：检测响应时间、误报率、通知送达率、设备执行成功率
- 风险评估：避免误报影响用户体验，确保紧急情况下的可靠性
"""
    
    def _generate_comfort_composition(self) -> str:
        """生成舒适度管理服务组合示例"""
        return """
## 服务组合方案

### 1. 方案概述
- 方案名称：智能舒适度管理系统
- 主要目标：维持最佳环境舒适度，提升居住体验
- 预期效果：自动调节环境参数，提高生活质量，降低能源消耗

### 2. 服务组合
```json
{
  "composition_id": "comfort_management_001",
  "services": [
    {
      "service_id": "comfort_management",
      "service_name": "舒适度管理服务",
      "role": "核心管理组件",
      "priority": 5,
      "inputs": ["temperature_data", "humidity_data", "light_data", "user_preferences"],
      "outputs": ["comfort_score", "adjustment_recommendations"],
      "dependencies": []
    },
    {
      "service_id": "temperature_monitor",
      "service_name": "温度监控服务",
      "role": "温度数据提供",
      "priority": 4,
      "inputs": ["sensor_data"],
      "outputs": ["temperature_value", "temperature_status", "alert"],
      "dependencies": []
    },
    {
      "service_id": "humidity_control",
      "service_name": "湿度控制服务",
      "role": "湿度调节",
      "priority": 4,
      "inputs": ["humidity_data", "target_humidity"],
      "outputs": ["control_command", "adjustment_status"],
      "dependencies": ["comfort_management"]
    },
    {
      "service_id": "device_control",
      "service_name": "设备控制服务",
      "role": "环境设备控制",
      "priority": 4,
      "inputs": ["device_id", "control_command", "parameters"],
      "outputs": ["execution_status", "device_response"],
      "dependencies": ["comfort_management", "humidity_control"]
    }
  ],
  "execution_flow": "传感器监控 -> 舒适度评估 -> 生成调节方案 -> 执行设备控制",
  "data_flow": "环境数据 -> 舒适度分析 -> 控制策略 -> 设备执行"
}
```

### 3. 实施建议
- 部署顺序：温度监控 -> 舒适度管理 -> 湿度控制 -> 设备控制
- 配置要点：设定个人偏好参数，配置设备控制策略，设置节能模式
- 监控指标：舒适度评分、能耗水平、用户满意度、设备运行效率
- 风险评估：避免频繁调节影响设备寿命，平衡舒适度和能耗
"""
    
    def _generate_energy_composition(self) -> str:
        """生成节能服务组合示例"""
        return """
## 服务组合方案

### 1. 方案概述
- 方案名称：智能节能优化系统
- 主要目标：最大化能源利用效率，降低能耗成本
- 预期效果：节省15-30%能源消耗，智能化能源管理

### 2. 服务组合
```json
{
  "composition_id": "energy_optimization_001",
  "services": [
    {
      "service_id": "energy_optimization",
      "service_name": "能源优化服务",
      "role": "核心优化引擎",
      "priority": 5,
      "inputs": ["motion_data", "light_data", "schedule"],
      "outputs": ["energy_plan", "device_commands"],
      "dependencies": []
    },
    {
      "service_id": "scheduling_service",
      "service_name": "调度服务",
      "role": "任务调度管理",
      "priority": 4,
      "inputs": ["schedule_config", "trigger_conditions"],
      "outputs": ["scheduled_tasks", "execution_log"],
      "dependencies": []
    },
    {
      "service_id": "device_control",
      "service_name": "设备控制服务",
      "role": "设备执行控制",
      "priority": 4,
      "inputs": ["device_id", "control_command", "parameters"],
      "outputs": ["execution_status", "device_response"],
      "dependencies": ["energy_optimization", "scheduling_service"]
    },
    {
      "service_id": "data_analytics",
      "service_name": "数据分析服务",
      "role": "能耗分析优化",
      "priority": 3,
      "inputs": ["historical_data", "sensor_readings"],
      "outputs": ["trend_analysis", "predictions", "insights"],
      "dependencies": []
    }
  ],
  "execution_flow": "数据收集 -> 能源分析 -> 优化策略 -> 调度执行 -> 效果评估",
  "data_flow": "传感器数据 -> 能源优化算法 -> 控制策略 -> 设备执行 -> 反馈优化"
}
```

### 3. 实施建议
- 部署顺序：数据分析 -> 调度服务 -> 能源优化 -> 设备控制
- 配置要点：设置能耗基线，配置优化算法参数，建立用户行为模型
- 监控指标：能耗降低率、用户满意度、设备运行时间、成本节约
- 风险评估：确保舒适度不受影响，避免过度优化导致用户体验下降
"""
    
    def _generate_default_composition(self) -> str:
        """生成默认服务组合示例"""
        return """
## 服务组合方案

### 1. 方案概述
- 方案名称：综合智能家居管理系统
- 主要目标：提供全面的智能家居管理和监控
- 预期效果：提升居住体验，提高安全性，优化能源使用

### 2. 服务组合
```json
{
  "composition_id": "comprehensive_home_system_001",
  "services": [
    {
      "service_id": "temperature_monitor",
      "service_name": "温度监控服务",
      "role": "环境监控",
      "priority": 4,
      "inputs": ["sensor_data"],
      "outputs": ["temperature_value", "temperature_status", "alert"],
      "dependencies": []
    },
    {
      "service_id": "security_monitoring",
      "service_name": "安全监控服务",
      "role": "安全保障",
      "priority": 5,
      "inputs": ["motion_data", "door_sensor", "time_schedule"],
      "outputs": ["security_status", "intrusion_alert"],
      "dependencies": []
    },
    {
      "service_id": "data_analytics",
      "service_name": "数据分析服务",
      "role": "数据洞察",
      "priority": 3,
      "inputs": ["historical_data", "sensor_readings"],
      "outputs": ["trend_analysis", "predictions", "insights"],
      "dependencies": []
    },
    {
      "service_id": "notification_service",
      "service_name": "通知服务",
      "role": "信息推送",
      "priority": 4,
      "inputs": ["alert_data", "notification_config"],
      "outputs": ["notification_sent", "delivery_status"],
      "dependencies": ["temperature_monitor", "security_monitoring"]
    }
  ],
  "execution_flow": "多传感器监控 -> 数据分析处理 -> 状态评估 -> 通知推送",
  "data_flow": "传感器数据 -> 分析处理 -> 状态判断 -> 用户通知"
}
```

### 3. 实施建议
- 部署顺序：数据分析 -> 各监控服务 -> 通知服务
- 配置要点：调整监控阈值，配置通知策略，优化数据处理流程
- 监控指标：系统响应时间、数据准确性、通知及时性、用户满意度
- 风险评估：确保系统稳定性，避免误报，保护用户隐私
"""
    
    def _parse_composition_response(self, response: str) -> Dict[str, Any]:
        """解析LLM响应，提取服务组合信息"""
        try:
            # 尝试从响应中提取JSON部分
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                composition_data = json.loads(json_str)
            else:
                # 如果没有找到JSON，创建默认结构
                composition_data = {
                    "composition_id": f"composition_{int(time.time())}",
                    "services": [],
                    "execution_flow": "待定义",
                    "data_flow": "待定义"
                }
            
            # 添加元数据
            composition = {
                "id": composition_data.get("composition_id", f"composition_{int(time.time())}"),
                "created_at": datetime.now().isoformat(),
                "llm_response": response,
                "composition_data": composition_data,
                "status": "generated",
                "validation_results": {}
            }
            
            return composition
            
        except Exception as e:
            print(f"解析LLM响应失败: {e}")
            return {
                "id": f"composition_{int(time.time())}",
                "created_at": datetime.now().isoformat(),
                "llm_response": response,
                "composition_data": {"services": []},
                "status": "parsing_failed",
                "error": str(e)
            }
    
    def _validate_composition(self, composition: Dict[str, Any]) -> Dict[str, Any]:
        """验证服务组合的可行性"""
        validation_results = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "suggestions": []
        }
        
        composition_data = composition.get("composition_data", {})
        services = composition_data.get("services", [])
        
        if not services:
            validation_results["is_valid"] = False
            validation_results["errors"].append("服务组合中没有定义任何服务")
            composition["validation_results"] = validation_results
            return composition
        
        # 验证服务是否存在
        available_service_ids = {service.id for service in self.available_services}
        for service in services:
            service_id = service.get("service_id", "")
            if service_id not in available_service_ids:
                validation_results["warnings"].append(f"服务 {service_id} 不在可用服务列表中")
        
        # 验证服务依赖关系
        service_ids = {service.get("service_id") for service in services}
        for service in services:
            dependencies = service.get("dependencies", [])
            for dep in dependencies:
                if dep not in service_ids:
                    validation_results["errors"].append(f"服务 {service.get('service_id')} 依赖的服务 {dep} 不在组合中")
                    validation_results["is_valid"] = False
        
        # 验证数据流连接
        input_outputs = {}
        for service in services:
            service_id = service.get("service_id", "")
            inputs = service.get("inputs", [])
            outputs = service.get("outputs", [])
            input_outputs[service_id] = {"inputs": inputs, "outputs": outputs}
        
        # 检查数据流连接性
        for service in services:
            service_id = service.get("service_id", "")
            inputs = service.get("inputs", [])
            dependencies = service.get("dependencies", [])
            
            for input_data in inputs:
                # 检查输入数据是否有来源
                has_source = False
                for dep in dependencies:
                    if dep in input_outputs:
                        dep_outputs = input_outputs[dep]["outputs"]
                        if any(input_data in output for output in dep_outputs):
                            has_source = True
                            break
                
                # 检查输入数据是否有来源，排除传感器原始数据和外部输入
                external_inputs = [
                    "sensor_data", "user_preferences", "schedule", "smoke_data", 
                    "temperature_data", "humidity_data", "light_data", "motion_data", 
                    "alert_data", "notification_config", "historical_data",
                    # 新增常见的外部输入和配置参数
                    "target_humidity", "target_temperature", "door_sensor", 
                    "time_schedule", "schedule_config", "device_id", "parameters",
                    "trigger_conditions", "sensor_readings"
                ]
                
                if not has_source and input_data not in external_inputs:
                    validation_results["warnings"].append(f"服务 {service_id} 的输入 {input_data} 缺少数据源")
        
        # 添加优化建议
        if len(services) > 6:
            validation_results["suggestions"].append("服务组合较为复杂，建议考虑分阶段实施")
        
        high_priority_services = [s for s in services if int(s.get("priority", 0)) >= 4]
        if len(high_priority_services) > 3:
            validation_results["suggestions"].append("高优先级服务过多，建议重新评估优先级分配")
        
        composition["validation_results"] = validation_results
        composition["status"] = "validated" if validation_results["is_valid"] else "validation_failed"
        
        return composition
    
    def _record_composition(self, composition: Dict[str, Any], target_goal: str):
        """记录服务组合历史"""
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "composition_id": composition["id"],
            "target_goal": target_goal,
            "status": composition["status"],
            "is_valid": composition.get("validation_results", {}).get("is_valid", False),
            "service_count": len(composition.get("composition_data", {}).get("services", []))
        }
        
        self.composition_history.append(history_entry)
        
        # 限制历史记录数量
        if len(self.composition_history) > 100:
            self.composition_history = self.composition_history[-50:]
    
    def optimize_composition(self, composition_id: str, performance_data: Dict[str, Any] = None,
                           user_feedback: str = None) -> Dict[str, Any]:
        """
        优化现有服务组合
        
        Args:
            composition_id: 服务组合ID
            performance_data: 性能数据
            user_feedback: 用户反馈
            
        Returns:
            优化后的服务组合
        """
        # 查找现有组合
        existing_composition = self._find_composition(composition_id)
        if not existing_composition:
            return {"error": "未找到指定的服务组合"}
        
        # 准备优化提示词
        optimization_prompt = self._prepare_optimization_prompt(
            existing_composition, performance_data, user_feedback
        )
        
        # 调用LLM获取优化建议
        llm_response = self._call_llm(optimization_prompt)
        
        # 解析优化建议
        optimization_result = {
            "original_composition_id": composition_id,
            "optimization_timestamp": datetime.now().isoformat(),
            "optimization_suggestions": llm_response,
            "status": "optimization_generated"
        }
        
        return optimization_result
    
    def _find_composition(self, composition_id: str) -> Optional[Dict[str, Any]]:
        """查找服务组合"""
        # 这里应该从数据库或存储中查找
        # 为了演示，返回一个示例组合
        return {
            "id": composition_id,
            "composition_data": {
                "services": [
                    {
                        "service_id": "temperature_monitor",
                        "service_name": "温度监控服务",
                        "role": "环境监控",
                        "priority": 4
                    }
                ]
            }
        }
    
    def _prepare_optimization_prompt(self, composition: Dict[str, Any], 
                                   performance_data: Dict[str, Any] = None,
                                   user_feedback: str = None) -> str:
        """准备优化提示词"""
        template = self.prompt_templates["service_optimization"]
        
        return template.format(
            current_composition=json.dumps(composition, indent=2, ensure_ascii=False),
            performance_data=json.dumps(performance_data or {}, indent=2, ensure_ascii=False),
            user_feedback=user_feedback or "暂无用户反馈",
            optimization_goals="提高性能、降低成本、改善用户体验"
        )
    
    def troubleshoot_composition(self, problem_description: str, 
                               error_messages: List[str] = None,
                               related_services: List[str] = None) -> Dict[str, Any]:
        """
        故障排除
        
        Args:
            problem_description: 问题描述
            error_messages: 错误信息
            related_services: 相关服务
            
        Returns:
            故障排除方案
        """
        # 准备故障排除提示词
        troubleshooting_prompt = self._prepare_troubleshooting_prompt(
            problem_description, error_messages, related_services
        )
        
        # 调用LLM获取故障排除建议
        llm_response = self._call_llm(troubleshooting_prompt)
        
        return {
            "problem_description": problem_description,
            "troubleshooting_timestamp": datetime.now().isoformat(),
            "diagnosis_and_solution": llm_response,
            "status": "troubleshooting_completed"
        }
    
    def _prepare_troubleshooting_prompt(self, problem_description: str,
                                      error_messages: List[str] = None,
                                      related_services: List[str] = None) -> str:
        """准备故障排除提示词"""
        template = self.prompt_templates["trouble_shooting"]
        
        return template.format(
            problem_description=problem_description,
            error_messages="\n".join(error_messages or []),
            related_services=", ".join(related_services or []),
            system_status="正常运行"
        )
    
    def get_available_services(self) -> List[Dict[str, Any]]:
        """获取可用服务列表"""
        return [service.to_dict() for service in self.available_services]
    
    def get_composition_history(self) -> List[Dict[str, Any]]:
        """获取服务组合历史"""
        return self.composition_history.copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_compositions = len(self.composition_history)
        valid_compositions = sum(1 for comp in self.composition_history if comp.get("is_valid", False))
        
        return {
            "可用服务数量": len(self.available_services),
            "历史组合总数": total_compositions,
            "有效组合数量": valid_compositions,
            "成功率": f"{valid_compositions/total_compositions*100:.1f}%" if total_compositions > 0 else "0%",
            "模型类型": self.model_type,
            "最近组合时间": self.composition_history[-1]["timestamp"] if self.composition_history else "无"
        }

# 使用示例
if __name__ == "__main__":
    # 创建服务组合器
    composer = LLMServiceComposer()
    
    print("=== 大模型服务组合演示 ===")
    
    # 演示1: 火灾安全组合
    print("\n1. 火灾安全服务组合")
    fire_composition = composer.compose_services(
        target_goal="建立一个智能火灾安全系统，能够及时检测火灾风险并自动响应",
        sensor_data={"smoke_level": 180, "temperature": 35},
        constraints=["响应时间小于30秒", "误报率低于5%"]
    )
    print(f"组合ID: {fire_composition['id']}")
    print(f"状态: {fire_composition['status']}")
    print(f"包含服务数: {len(fire_composition.get('composition_data', {}).get('services', []))}")
    
    # 演示2: 舒适度管理组合
    print("\n2. 舒适度管理服务组合")
    comfort_composition = composer.compose_services(
        target_goal="创建智能舒适度管理系统，自动维持最佳居住环境",
        sensor_data={"temperature": 28, "humidity": 75, "light": 200},
        constraints=["能耗增加不超过20%", "调节响应时间小于5分钟"]
    )
    print(f"组合ID: {comfort_composition['id']}")
    print(f"状态: {comfort_composition['status']}")
    
    # 演示3: 查看可用服务
    print("\n3. 可用服务列表")
    services = composer.get_available_services()
    for service in services[:3]:  # 只显示前3个
        print(f"- {service['name']}: {service['description']}")
    
    # 演示4: 统计信息
    print("\n4. 统计信息")
    stats = composer.get_statistics()
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    # 演示5: 故障排除
    print("\n5. 故障排除演示")
    troubleshooting = composer.troubleshoot_composition(
        problem_description="温度监控服务频繁报警，但实际温度正常",
        error_messages=["温度阈值超限", "传感器数据异常"],
        related_services=["temperature_monitor", "notification_service"]
    )
    print(f"故障排除状态: {troubleshooting['status']}")
