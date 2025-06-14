# 智能家居监控系统 - 物联网服务智能与应用实践

## 🏠 项目概述

本项目是网络服务智能与应用实践的大作业，实现了一个基于**SSN（Semantic Sensor Network）建模**的智能家居监控系统。系统集成了设备建模、数据采集、事件处理和大模型服务组合等核心功能，完全满足作业要求的四个关键点：

1. ✅ **SSN建模**: 对物联网设备进行语义建模
2. ✅ **数据采集服务**: 生成语义事件和复杂事件
3. ✅ **大模型服务组合**: 基于LLM的智能服务组合
4. ✅ **可运行展示**: 提供完整的可运行系统

## 🎯 核心功能

### 🌐 SSN语义建模
- 基于W3C SSN/SOSA标准的传感器网络建模
- 支持温度、湿度、烟雾、运动、光照等多种传感器类型
- RDF语义图构建与SPARQL查询支持
- 传感器能力与属性的完整描述

### 📊 智能数据采集
- 实时传感器数据模拟与采集
- 数据质量评估与异常检测
- 语义事件自动生成
- 支持批处理和流式处理

### 🧠 复杂事件推理
- 原子语义事件识别
- 基于规则的复杂事件推理
- 时间、空间、因果关联分析
- 多层次事件处理架构

### 🤖 大模型服务组合
- 基于GPT的智能服务组合生成
- 支持提示词工程和微调
- 服务组合验证与优化建议
- 自动故障排除与恢复

### 🖥️ 实时监控界面
- 响应式Web控制台
- 实时数据可视化图表
- 交互式服务组合工具
- 系统状态监控面板

## 📁 项目结构

```
homework_project/
├── 📄 README.md                    # 项目说明文档
├── 📄 requirements.txt             # Python依赖包
├── 📄 main.py                      # 🚀 主程序入口
├── 📄 demo.py                      # 🎬 快速演示脚本
├── 📁 config/                      # ⚙️ 配置文件
│   ├── ssn_model.json             # SSN语义模型配置
│   └── service_config.json        # 系统服务配置
├── 📁 src/                         # 💻 核心源代码
│   ├── __init__.py
│   ├── ssn_modeling.py            # SSN建模模块
│   ├── data_collector.py          # 数据采集模块
│   ├── event_processor.py         # 事件处理模块
│   ├── llm_composer.py            # 大模型服务组合
│   └── web_interface.py           # Web界面模块
├── 📁 data/                        # 📈 数据存储
│   ├── raw/                       # 原始传感器数据
│   ├── processed/                 # 处理后数据
│   └── events/                    # 事件数据
├── 📁 services/                    # 🔧 服务定义
│   └── basic_services.json        # 基础IoT服务定义
├── 📁 tests/                       # 🧪 测试文件
│   └── test_ssn.py               # SSN建模测试
├── 📁 docs/                        # 📚 文档
│   └── design_document.md         # 详细设计文档
└── 📁 logs/                        # 📝 系统日志 (运行时生成)
```

## 🚀 快速开始

### 📋 环境要求
- **Python**: 3.8+
- **内存**: 2GB+
- **磁盘**: 500MB可用空间
- **网络**: 可选（用于OpenAI API）

### 🔧 安装与配置

1. **克隆或下载项目**
```bash
# 如果从GitHub获取
git clone <repository-url>
cd homework_project

# 或直接使用提供的代码文件夹
cd homework_project
```

2. **安装Python依赖**
```bash
pip install -r requirements.txt
```

3. **配置系统（可选）**
```bash
# 编辑服务配置文件
vim config/service_config.json

# 如果要使用真实的OpenAI API，请设置API密钥
# 否则系统会使用模拟响应进行演示
```

### 🎬 运行演示

#### 方式1: 快速演示脚本 (推荐用于首次体验)
```bash
python demo.py
```
这个脚本会依次展示所有核心功能，用时约2-3分钟。

#### 方式2: 完整系统演示
```bash
# 演示模式 - 运行一次完整的工作流程
python main.py --mode demo

# 交互模式 - 手动控制系统各个功能
python main.py --mode interactive

# Web界面模式 - 启动可视化监控界面
python main.py --mode web
```

#### 方式3: Web界面体验
```bash
# 启动Web服务器
python main.py --mode web

# 然后在浏览器中访问
# http://localhost:5000
```

### 🖥️ Web界面功能

访问 `http://localhost:5000` 后可以体验：

- **📊 实时监控**: 传感器数据图表
- **⚡ 事件管理**: 实时事件流显示
- **🔧 服务组合**: 交互式服务组合工具
- **📈 系统状态**: 运行统计和性能监控
- **⚙️ 系统控制**: 启动/停止数据采集

## 🧪 测试验证

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python tests/test_ssn.py

# 检查代码覆盖率 (如果已安装pytest-cov)
python -m pytest tests/ --cov=src
```

## 📖 详细文档

### 🏗️ 系统架构
详见 [`docs/design_document.md`](docs/design_document.md)，包含：
- 详细系统架构图
- 模块设计说明
- API接口文档
- 部署与扩展指南

### 🔧 配置说明

#### SSN模型配置 (`config/ssn_model.json`)
定义传感器网络的语义结构：
- 传感器类型与属性
- 观测属性定义
- 平台配置信息
- 语义关系映射

#### 服务配置 (`config/service_config.json`)
系统运行参数：
- 数据采集间隔与批大小
- 复杂事件处理规则
- LLM服务配置
- Web界面设置

## 🎯 作业要求对应

| 作业要求 | 实现模块 | 核心功能 |
|---------|---------|---------|
| **(1) SSN建模** | `ssn_modeling.py` | 基于W3C标准的语义传感器网络建模 |
| **(2) 数据采集服务** | `data_collector.py` | 生成语义事件和复杂事件 |
| **(3) 大模型服务组合** | `llm_composer.py` | 基于LLM的智能服务组合 |
| **(4) 可运行展示** | `main.py` + `web_interface.py` | 完整可运行系统 |

## 🌟 系统特色

### 🎓 技术亮点
- **语义建模**: 严格遵循W3C SSN/SOSA标准
- **事件驱动**: 实时事件处理与复杂推理
- **AI驱动**: 大模型智能服务组合
- **可视化**: 直观的Web监控界面
- **模块化**: 松耦合的架构设计

### 💡 创新点
- **多层次事件处理**: 从原子事件到复杂事件的完整推理链
- **智能服务组合**: 基于自然语言描述的自动化服务组合
- **自适应监控**: 根据传感器特性动态调整监控策略
- **语义丰富**: 完整的RDF知识图谱支持

## 👥 团队协作

### 🎭 角色分工建议
- **成员1**: SSN建模与语义建模实现
- **成员2**: 数据采集与事件处理逻辑
- **成员3**: 大模型集成与服务组合
- **成员4**: Web界面开发与系统测试

### 📅 开发计划
- **Week 1**: 需求分析与架构设计
- **Week 2**: 核心模块开发与集成
- **Week 3**: 测试优化与文档完善
- **展示日**: 2025年6月16日

## 🔧 扩展开发

### 🔌 添加新传感器
1. 在 `config/ssn_model.json` 中定义新传感器
2. 在 `data_collector.py` 中添加数据模拟逻辑
3. 更新 `event_processor.py` 中的事件规则

### 🚀 添加新服务
1. 在 `services/basic_services.json` 中定义服务
2. 在 `llm_composer.py` 中更新服务库
3. 扩展 `web_interface.py` 中的UI支持

### 🤖 自定义LLM
1. 在 `config/service_config.json` 中配置API
2. 在 `llm_composer.py` 中实现新的调用逻辑
3. 优化提示词模板

## 🐛 常见问题

### Q: 系统启动失败？
**A**: 检查Python版本(>=3.8)和依赖安装：
```bash
python --version
pip install -r requirements.txt
```

### Q: Web界面无法访问？
**A**: 确认端口5000未被占用，或修改配置文件中的端口设置。

### Q: 大模型服务调用失败？
**A**: 系统会自动使用模拟响应，无需真实API即可演示完整功能。

### Q: 数据文件夹为空？
**A**: 数据文件夹在系统运行时自动创建和填充，这是正常现象。

## 📞 技术支持

- 📚 **详细文档**: `docs/design_document.md`
- 🧪 **测试用例**: `tests/` 目录
- 🎬 **快速演示**: `python demo.py`
- 💻 **交互模式**: `python main.py --mode interactive`

---

## 🎉 项目总结

本项目完整实现了网络服务智能与应用实践课程的所有要求，包括：

✅ **SSN建模**: 完整的语义传感器网络建模  
✅ **数据服务**: 智能数据采集与事件生成  
✅ **AI组合**: 大模型驱动的服务组合  
✅ **可运行**: 完整的可演示系统  

系统展现了物联网、语义技术、AI服务和Web技术的深度融合，为智能家居场景提供了完整的解决方案。

**🚀 立即开始体验**: `python demo.py`

---

*© 2025 智能家居监控系统开发团队 | 网络服务智能与应用实践课程*
