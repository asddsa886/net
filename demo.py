#!/usr/bin/env python
"""
智能家居监控系统演示脚本
用于快速展示系统功能
"""

import sys
import os
import time
from datetime import datetime

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def print_header(title):
    """打印标题"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_section(title):
    """打印章节"""
    print(f"\n📋 {title}")
    print("-" * 40)

def demo_system():
    """演示系统功能"""
    print_header("智能家居监控系统 - 功能演示")
    
    try:
        # 导入模块
        print("🔄 正在加载系统模块...")
        from src.ssn_modeling import SSNModeling
        from src.data_collector import DataCollector
        from src.event_processor import EventProcessor
        from src.llm_composer import LLMServiceComposer
        print("✅ 所有模块加载成功!")
        
        # 1. SSN建模演示
        print_section("1. SSN语义传感器网络建模")
        ssn = SSNModeling()
        
        # 显示传感器统计
        stats = ssn.get_sensor_statistics()
        print("📊 传感器网络统计:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # 显示传感器信息
        print("\n🌡️ 传感器详情:")
        sensors = ssn.ssn_config.get('sensors', [])[:3]  # 只显示前3个
        for sensor in sensors:
            print(f"   • {sensor['name']} ({sensor['location']})")
            print(f"     观测属性: {sensor['observes'].split(':')[-1]}")
        
        # 创建观测记录示例
        obs = ssn.create_observation("home:temperatureSensor_001", 23.5)
        print(f"\n📝 观测记录示例:")
        print(f"   传感器: {obs['madeBySensor']}")
        print(f"   数值: {obs['hasResult']['value']} {obs['hasResult']['unit']}")
        print(f"   时间: {obs['resultTime']}")
        
        time.sleep(2)
        
        # 2. 数据采集演示
        print_section("2. 数据采集与语义事件生成")
        collector = DataCollector()
        
        print("🔄 正在采集传感器数据...")
        readings = collector.collect_all_sensors()
        
        print(f"✅ 成功采集 {len(readings)} 个传感器读数:")
        for reading in readings:
            sensor_name = reading['madeBySensor'].split(':')[-1]
            value = reading['hasResult']['value']
            unit = reading['hasResult']['unit']
            quality = reading.get('quality', 'unknown')
            
            print(f"   🌡️ {sensor_name}: {value} {unit} (质量: {quality})")
        
        # 生成语义事件
        print("\n🔄 正在生成语义事件...")
        events = collector.generate_semantic_events(readings)
        print(f"✅ 生成了 {len(events)} 个语义事件")
        
        # 显示部分事件
        for event in events[:3]:
            event_type = event.get('eventType', '未知')
            semantics = event.get('semantics', {})
            interpretation = semantics.get('value_interpretation', '正常')
            print(f"   ⚡ {event_type}: {interpretation}")
        
        time.sleep(2)
        
        # 3. 事件处理演示
        print_section("3. 复杂事件推理与处理")
        processor = EventProcessor()
        
        print("🔄 正在处理语义事件并进行复杂推理...")
        total_complex_events = 0
        
        for event in events:
            complex_events = processor.process_semantic_event(event)
            total_complex_events += len(complex_events)
            
            for complex_event in complex_events:
                event_type = complex_event.get('eventType', '未知')
                severity = complex_event.get('severity', 'unknown')
                print(f"   🧠 复杂事件: {event_type} (严重程度: {severity})")
        
        print(f"✅ 总共生成了 {total_complex_events} 个复杂事件")
        
        # 显示传感器状态
        sensor_status = processor.get_sensor_status_summary()
        print(f"\n📊 传感器状态摘要:")
        for sensor_id, status in list(sensor_status.items())[:3]:
            sensor_name = sensor_id.split(':')[-1] if ':' in sensor_id else sensor_id
            print(f"   • {sensor_name}: {status.get('最新值', 'N/A')} ({status.get('趋势', 'unknown')})")
        
        time.sleep(2)
        
        # 4. 服务组合演示
        print_section("4. 大模型智能服务组合")
        composer = LLMServiceComposer()
        
        # 显示可用服务
        services = composer.get_available_services()
        print(f"📋 可用服务数量: {len(services)}")
        print("   主要服务类别:")
        categories = set(service['category'] for service in services)
        for category in categories:
            count = sum(1 for s in services if s['category'] == category)
            print(f"   • {category}: {count} 个服务")
        
        # 创建服务组合示例
        print("\n🔄 正在创建智能服务组合...")
        composition = composer.compose_services(
            target_goal="建立一个智能火灾安全系统，能够及时检测火灾风险并自动响应",
            sensor_data={"smoke_level": 150, "temperature": 32},
            constraints=["响应时间小于30秒", "误报率低于5%"]
        )
        
        print("✅ 服务组合创建完成!")
        print(f"   组合ID: {composition['id']}")
        print(f"   状态: {composition['status']}")
        
        composition_data = composition.get('composition_data', {})
        services_list = composition_data.get('services', [])
        print(f"   包含服务: {len(services_list)} 个")
        
        for service in services_list[:3]:  # 只显示前3个
            print(f"   • {service.get('service_name', '未知服务')} (优先级: {service.get('priority', 'N/A')})")
        
        # 验证结果
        validation = composition.get('validation_results', {})
        if validation.get('is_valid'):
            print("   ✅ 组合验证通过")
        else:
            print("   ⚠️ 组合验证有警告")
            for warning in validation.get('warnings', [])[:2]:
                print(f"      - {warning}")
        
        time.sleep(2)
        
        # 5. 系统统计
        print_section("5. 系统运行统计")
        collector_stats = collector.get_statistics()
        processor_stats = processor.get_event_statistics()
        composer_stats = composer.get_statistics()
        
        print("📈 系统性能统计:")
        print(f"   数据采集:")
        print(f"     • 总数据量: {collector_stats.get('总采集数据量', 0)}")
        print(f"     • 队列状态: {collector_stats.get('队列中数据量', 0)} 条待处理")
        
        print(f"   事件处理:")
        print(f"     • 历史事件: {processor_stats.get('历史事件总数', 0)} 个")
        print(f"     • 活跃传感器: {processor_stats.get('活跃传感器数', 0)} 个")
        
        print(f"   服务组合:")
        print(f"     • 可用服务: {composer_stats.get('可用服务数量', 0)} 个")
        print(f"     • 历史组合: {composer_stats.get('历史组合总数', 0)} 个")
        
        # 6. 演示总结
        print_section("6. 演示总结")
        print("🎉 系统功能演示完成!")
        print("\n✅ 已成功展示的功能:")
        print("   • SSN语义传感器网络建模")
        print("   • 传感器数据采集与模拟")
        print("   • 语义事件生成与识别")
        print("   • 复杂事件推理与关联分析")
        print("   • 大模型智能服务组合")
        print("   • 系统状态监控与统计")
        
        print(f"\n📊 演示数据摘要:")
        print(f"   • 传感器数量: {len(sensors)} 个")
        print(f"   • 采集读数: {len(readings)} 条")
        print(f"   • 语义事件: {len(events)} 个")
        print(f"   • 复杂事件: {total_complex_events} 个")
        print(f"   • 服务组合: 1 个")
        
        print(f"\n🌟 系统特色:")
        print("   • 基于W3C SSN/SOSA标准的语义建模")
        print("   • 实时数据采集与事件驱动处理")
        print("   • 多层次事件推理与智能分析")
        print("   • 大模型驱动的服务自动组合")
        print("   • 模块化设计，易于扩展")
        
        print(f"\n🚀 下一步体验:")
        print("   • 运行 'python main.py --mode web' 启动Web界面")
        print("   • 运行 'python main.py --mode interactive' 进入交互模式")
        print("   • 运行 'python -m pytest tests/' 执行测试用例")
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        print("请确保已安装所有依赖: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo_system()
