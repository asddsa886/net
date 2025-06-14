"""
SSN建模模块测试
"""

import unittest
import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from ssn_modeling import SSNModeling
from datetime import datetime

class TestSSNModeling(unittest.TestCase):
    """SSN建模测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.ssn = SSNModeling()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.ssn)
        self.assertIsNotNone(self.ssn.ssn_config)
        self.assertGreater(len(self.ssn.ssn_config.get('sensors', [])), 0)
    
    def test_get_sensor_info(self):
        """测试获取传感器信息"""
        sensor_id = "home:temperatureSensor_001"
        sensor_info = self.ssn.get_sensor_info(sensor_id)
        
        self.assertIsNotNone(sensor_info)
        self.assertEqual(sensor_info['id'], sensor_id)
        self.assertIn('name', sensor_info)
        self.assertIn('location', sensor_info)
    
    def test_get_sensors_by_location(self):
        """测试根据位置获取传感器"""
        location = "客厅"
        sensors = self.ssn.get_sensors_by_location(location)
        
        self.assertIsInstance(sensors, list)
        for sensor in sensors:
            self.assertEqual(sensor['location'], location)
    
    def test_create_observation(self):
        """测试创建观测记录"""
        sensor_id = "home:temperatureSensor_001"
        value = 25.5
        timestamp = datetime.now()
        
        observation = self.ssn.create_observation(sensor_id, value, timestamp)
        
        self.assertIsNotNone(observation)
        self.assertEqual(observation['madeBySensor'], sensor_id)
        self.assertEqual(observation['hasResult']['value'], value)
        self.assertIn('id', observation)
        self.assertIn('type', observation)
    
    def test_validate_sensor_value(self):
        """测试传感器值验证"""
        sensor_id = "home:temperatureSensor_001"
        
        # 有效值测试
        self.assertTrue(self.ssn.validate_sensor_value(sensor_id, 25.0))
        
        # 边界值测试
        self.assertTrue(self.ssn.validate_sensor_value(sensor_id, -20.0))  # 最小值
        self.assertTrue(self.ssn.validate_sensor_value(sensor_id, 50.0))   # 最大值
        
        # 无效值测试
        self.assertFalse(self.ssn.validate_sensor_value(sensor_id, -30.0))  # 超出最小值
        self.assertFalse(self.ssn.validate_sensor_value(sensor_id, 60.0))   # 超出最大值
    
    def test_get_sensor_statistics(self):
        """测试获取传感器统计信息"""
        stats = self.ssn.get_sensor_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('总传感器数', stats)
        self.assertIn('平台数', stats)
        self.assertIn('观测属性数', stats)
        self.assertIn('按位置分布', stats)
        self.assertIn('按类型分布', stats)
        
        self.assertGreater(stats['总传感器数'], 0)
    
    def test_export_rdf(self):
        """测试RDF导出"""
        rdf_content = self.ssn.export_rdf()
        
        self.assertIsInstance(rdf_content, str)
        self.assertGreater(len(rdf_content), 0)
        
        # 检查是否包含基本的RDF三元组信息
        self.assertIn('ssn:', rdf_content)
        self.assertIn('sosa:', rdf_content)

if __name__ == '__main__':
    unittest.main()
