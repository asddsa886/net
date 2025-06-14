"""
智能家居监控系统主程序
整合SSN建模、数据采集、事件处理和大模型服务组合功能
"""

import sys
import os
import time
import threading
import argparse
from datetime import datetime

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.ssn_modeling import SSNModeling
from src.data_collector import DataCollector
from src.event_processor import EventProcessor
from src.llm_composer import LLMServiceComposer
from src.web_interface import WebInterface

class SmartHomeSystem:
    """智能家居监控系统主类"""
    
    def __init__(self):
        """初始化系统"""
        print("🏠 智能家居监控系统启动中...")
        
        # 初始化各个组件
        self.ssn_model = SSNModeling()
        print("✅ SSN建模模块已加载")
        
        self.data_collector = DataCollector()
        print("✅ 数据采集模块已加载")
        
        self.event_processor = EventProcessor()
        print("✅ 事件处理模块已加载")
        
        self.llm_composer = LLMServiceComposer()
        print("✅ 大模型服务组合模块已加载")
        
        self.web_interface = WebInterface()
        print("✅ Web界面模块已加载")
        
        # 系统状态
        self.is_running = False
        self.start_time = None
        
        # 设置事件订阅
        self._setup_event_subscriptions()
        print("✅ 事件订阅已配置")
    
    def _setup_event_subscriptions(self):
        """设置事件订阅关系"""
        def on_semantic_event(event):
            """处理语义事件"""
            try:
                complex_events = self.event_processor.process_semantic_event(event)
                if complex_events:
                    print(f"📊 生成了 {len(complex_events)} 个复杂事件")
                    for complex_event in complex_events:
                        if complex_event.get('severity') == 'critical':
                            print(f"🚨 关键事件: {complex_event.get('eventType')} - {complex_event.get('details', {}).get('description', '')}")
            except Exception as e:
                print(f"❌ 事件处理错误: {e}")
        
        def on_complex_event(event):
            """处理复杂事件"""
            event_type = event.get('eventType', '')
            severity = event.get('severity', '')
            
            if severity == 'critical':
                print(f"🚨 严重事件: {event_type}")
            elif severity == 'high':
                print(f"⚠️  高级事件: {event_type}")
            else:
                print(f"ℹ️  事件: {event_type}")
        
        # 订阅事件
        self.data_collector.subscribe_to_events(on_semantic_event)
        self.event_processor.subscribe_to_complex_events(on_complex_event)
    
    def start_data_collection(self):
        """启动数据采集"""
        print("🔄 启动数据采集服务...")
        self.data_collector.start_continuous_collection()
        self.is_running = True
        self.start_time = datetime.now()
        print("✅ 数据采集服务已启动")
    
    def stop_data_collection(self):
        """停止数据采集"""
        print("⏹️  停止数据采集服务...")
        self.data_collector.stop_continuous_collection()
        self.is_running = False
        print("✅ 数据采集服务已停止")
    
    def demo_sensor_readings(self):
        """演示传感器读数"""
        print("\n📊 传感器读数演示:")
        print("-" * 50)
        
        readings = self.data_collector.collect_all_sensors()
        for reading in readings:
            sensor_name = reading['madeBySensor'].split(':')[-1]
            value = reading['hasResult']['value']
            unit = reading['hasResult']['unit']
            quality = reading.get('quality', 'unknown')
            
            print(f"🌡️  {sensor_name}: {value} {unit} (质量: {quality})")
        
        return readings
    
    def demo_event_processing(self, readings):
        """演示事件处理"""
        print("\n🔔 事件处理演示:")
        print("-" * 50)
        
        # 生成语义事件
        events = self.data_collector.generate_semantic_events(readings)
        print(f"生成了 {len(events)} 个语义事件")
        
        # 处理每个事件
        total_complex_events = 0
        for event in events:
            complex_events = self.event_processor.process_semantic_event(event)
            total_complex_events += len(complex_events)
            
            if complex_events:
                for complex_event in complex_events:
                    event_type = complex_event.get('eventType', '未知')
                    severity = complex_event.get('severity', 'unknown')
                    print(f"  ⚡ {event_type} (严重程度: {severity})")
        
        print(f"总共生成了 {total_complex_events} 个复杂事件")
        return total_complex_events
    
    def demo_service_composition(self):
        """演示服务组合"""
        print("\n🔧 服务组合演示:")
        print("-" * 50)
        
        # 示例1: 火灾安全系统
        print("1. 创建火灾安全服务组合...")
        fire_composition = self.llm_composer.compose_services(
            target_goal="建立一个智能火灾安全系统，能够及时检测火灾风险并自动响应",
            sensor_data={"smoke_level": 180, "temperature": 35},
            constraints=["响应时间小于30秒", "误报率低于5%"]
        )
        
        print(f"   组合ID: {fire_composition['id']}")
        print(f"   状态: {fire_composition['status']}")
        print(f"   服务数量: {len(fire_composition.get('composition_data', {}).get('services', []))}")
        
        # 示例2: 舒适度管理系统
        print("\n2. 创建舒适度管理服务组合...")
        comfort_composition = self.llm_composer.compose_services(
            target_goal="创建智能舒适度管理系统，自动维持最佳居住环境",
            sensor_data={"temperature": 28, "humidity": 75, "light": 200},
            constraints=["能耗增加不超过20%", "调节响应时间小于5分钟"]
        )
        
        print(f"   组合ID: {comfort_composition['id']}")
        print(f"   状态: {comfort_composition['status']}")
        print(f"   服务数量: {len(comfort_composition.get('composition_data', {}).get('services', []))}")
        
        return [fire_composition, comfort_composition]
    
    def demo_complete_workflow(self):
        """演示完整工作流程"""
        print("\n🚀 完整工作流程演示:")
        print("=" * 60)
        
        # 1. 展示SSN模型统计
        print("\n1. SSN模型统计:")
        ssn_stats = self.ssn_model.get_sensor_statistics()
        for key, value in ssn_stats.items():
            print(f"   {key}: {value}")
        
        # 2. 传感器读数
        readings = self.demo_sensor_readings()
        
        # 3. 事件处理
        complex_events_count = self.demo_event_processing(readings)
        
        # 4. 服务组合
        compositions = self.demo_service_composition()
        
        # 5. 系统统计
        print("\n📈 系统运行统计:")
        print("-" * 50)
        collector_stats = self.data_collector.get_statistics()
        processor_stats = self.event_processor.get_event_statistics()
        composer_stats = self.llm_composer.get_statistics()
        
        print(f"数据采集器状态: {collector_stats}")
        print(f"事件处理器状态: {processor_stats}")
        print(f"服务组合器状态: {composer_stats}")
        
        return {
            'readings_count': len(readings),
            'complex_events_count': complex_events_count,
            'compositions_count': len(compositions)
        }
    
    def run_interactive_mode(self):
        """运行交互模式"""
        print("\n🎮 交互模式启动")
        print("可用命令:")
        print("  start    - 启动数据采集")
        print("  stop     - 停止数据采集")
        print("  demo     - 运行演示")
        print("  status   - 显示系统状态")
        print("  compose  - 创建服务组合")
        print("  web      - 启动Web界面")
        print("  quit     - 退出系统")
        print("-" * 40)
        
        while True:
            try:
                command = input("\n请输入命令: ").strip().lower()
                
                if command == 'start':
                    if not self.is_running:
                        self.start_data_collection()
                    else:
                        print("系统已在运行中")
                
                elif command == 'stop':
                    if self.is_running:
                        self.stop_data_collection()
                    else:
                        print("系统未运行")
                
                elif command == 'demo':
                    result = self.demo_complete_workflow()
                    print(f"\n演示完成: {result}")
                
                elif command == 'status':
                    self.show_system_status()
                
                elif command == 'compose':
                    self.interactive_service_composition()
                
                elif command == 'web':
                    print("启动Web界面...")
                    self.start_web_interface()
                
                elif command == 'quit':
                    if self.is_running:
                        self.stop_data_collection()
                    print("系统退出")
                    break
                
                else:
                    print("未知命令，请重新输入")
            
            except KeyboardInterrupt:
                print("\n\n用户中断，系统退出")
                if self.is_running:
                    self.stop_data_collection()
                break
            except Exception as e:
                print(f"命令执行错误: {e}")
    
    def show_system_status(self):
        """显示系统状态"""
        print("\n📊 系统状态:")
        print("-" * 30)
        print(f"运行状态: {'🟢 运行中' if self.is_running else '🔴 已停止'}")
        
        if self.start_time:
            uptime = datetime.now() - self.start_time
            print(f"运行时长: {uptime}")
        
        collector_stats = self.data_collector.get_statistics()
        processor_stats = self.event_processor.get_event_statistics()
        composer_stats = self.llm_composer.get_statistics()
        
        print(f"采集数据量: {collector_stats.get('总采集数据量', 0)}")
        print(f"处理事件数: {processor_stats.get('历史事件总数', 0)}")
        print(f"服务组合数: {composer_stats.get('历史组合总数', 0)}")
    
    def interactive_service_composition(self):
        """交互式服务组合"""
        print("\n🔧 交互式服务组合:")
        
        target_goal = input("请输入目标需求: ").strip()
        if not target_goal:
            print("目标需求不能为空")
            return
        
        constraints_input = input("请输入约束条件 (用逗号分隔，可选): ").strip()
        constraints = [c.strip() for c in constraints_input.split(',') if c.strip()] if constraints_input else []
        
        print("正在生成服务组合...")
        try:
            composition = self.llm_composer.compose_services(
                target_goal=target_goal,
                sensor_data={},
                constraints=constraints
            )
            
            print(f"✅ 服务组合创建成功!")
            print(f"组合ID: {composition['id']}")
            print(f"状态: {composition['status']}")
            
            validation = composition.get('validation_results', {})
            if validation.get('is_valid'):
                print("✅ 组合验证通过")
            else:
                print("⚠️  组合验证有问题:")
                for error in validation.get('errors', []):
                    print(f"   - {error}")
            
        except Exception as e:
            print(f"❌ 服务组合创建失败: {e}")
    
    def start_web_interface(self):
        """启动Web界面"""
        try:
            # 在新线程中启动Web界面，避免阻塞
            web_thread = threading.Thread(target=self.web_interface.run, daemon=True)
            web_thread.start()
            
            print("Web界面已在后台启动")
            print("访问 http://localhost:5000 查看监控界面")
            print("按Enter键返回交互模式...")
            input()
            
        except Exception as e:
            print(f"Web界面启动失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='智能家居监控系统')
    parser.add_argument('--mode', choices=['demo', 'interactive', 'web'], 
                       default='interactive', help='运行模式')
    parser.add_argument('--auto-start', action='store_true', 
                       help='自动启动数据采集')
    
    args = parser.parse_args()
    
    # 创建系统实例
    system = SmartHomeSystem()
    
    if args.auto_start:
        system.start_data_collection()
    
    try:
        if args.mode == 'demo':
            print("运行演示模式...")
            result = system.demo_complete_workflow()
            print(f"\n🎉 演示完成! 结果: {result}")
            
        elif args.mode == 'web':
            print("启动Web界面模式...")
            system.start_web_interface()
            
        elif args.mode == 'interactive':
            system.run_interactive_mode()
            
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，正在清理资源...")
        if system.is_running:
            system.stop_data_collection()
        print("系统已安全退出")
    
    except Exception as e:
        print(f"❌ 系统运行错误: {e}")
        if system.is_running:
            system.stop_data_collection()

if __name__ == "__main__":
    main()
