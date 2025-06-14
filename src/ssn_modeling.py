"""
SSN (Semantic Sensor Network) 建模模块
实现传感器网络的语义建模，包括传感器、观测属性、平台等的定义和管理
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD


class SSNModeling:
    """SSN语义传感器网络建模类"""
    
    def __init__(self, config_path: str = None):
        """
        初始化SSN建模器
        
        Args:
            config_path: SSN配置文件路径
        """
        self.config_path = config_path or "config/ssn_model.json"
        self.ssn_config = self._load_config()
        self.graph = Graph()
        self._setup_namespaces()
        self._build_semantic_model()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载SSN配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"SSN配置文件未找到: {self.config_path}")
        except json.JSONDecodeError:
            raise ValueError(f"SSN配置文件格式错误: {self.config_path}")
    
    def _setup_namespaces(self):
        """设置RDF命名空间"""
        self.SSN = Namespace("http://www.w3.org/ns/ssn/")
        self.SOSA = Namespace("http://www.w3.org/ns/sosa/")
        self.HOME = Namespace("http://smart-home.example.org/")
        
        # 绑定命名空间
        self.graph.bind("ssn", self.SSN)
        self.graph.bind("sosa", self.SOSA)
        self.graph.bind("home", self.HOME)
        self.graph.bind("rdfs", RDFS)
    
    def _build_semantic_model(self):
        """构建语义模型"""
        self._model_sensors()
        self._model_observable_properties()
        self._model_platforms()
    
    def _model_sensors(self):
        """建模传感器"""
        for sensor in self.ssn_config.get('sensors', []):
            sensor_uri = URIRef(sensor['id'])
            
            # 基本类型声明
            self.graph.add((sensor_uri, RDF.type, self.SSN.Sensor))
            self.graph.add((sensor_uri, RDF.type, self.SOSA.Sensor))
            
            # 基本属性
            self.graph.add((sensor_uri, RDFS.label, Literal(sensor['name'], lang='zh')))
            self.graph.add((sensor_uri, self.HOME.location, Literal(sensor['location'])))
            self.graph.add((sensor_uri, self.SOSA.observes, URIRef(sensor['observes'])))
            
            # 传感器属性
            if 'properties' in sensor:
                self._add_sensor_properties(sensor_uri, sensor['properties'])
            
            # 传感器能力
            if 'capabilities' in sensor:
                self._add_sensor_capabilities(sensor_uri, sensor['capabilities'])
    
    def _add_sensor_properties(self, sensor_uri: URIRef, properties: Dict[str, Any]):
        """添加传感器属性"""
        for prop, value in properties.items():
            if prop == 'range':
                range_node = self.HOME[f"{sensor_uri.split('/')[-1]}_range"]
                self.graph.add((sensor_uri, self.HOME.hasRange, range_node))
                self.graph.add((range_node, self.HOME.minValue, Literal(value['min'])))
                self.graph.add((range_node, self.HOME.maxValue, Literal(value['max'])))
                self.graph.add((range_node, self.HOME.unit, Literal(value['unit'])))
            else:
                self.graph.add((sensor_uri, self.HOME[prop], Literal(value)))
    
    def _add_sensor_capabilities(self, sensor_uri: URIRef, capabilities: Dict[str, Any]):
        """添加传感器能力"""
        for cap, value in capabilities.items():
            if isinstance(value, dict):
                cap_node = self.HOME[f"{sensor_uri.split('/')[-1]}_{cap}"]
                self.graph.add((sensor_uri, self.HOME[cap], cap_node))
                for sub_cap, sub_value in value.items():
                    self.graph.add((cap_node, self.HOME[sub_cap], Literal(str(sub_value))))
            else:
                self.graph.add((sensor_uri, self.HOME[cap], Literal(value)))
    
    def _model_observable_properties(self):
        """建模可观测属性"""
        for prop in self.ssn_config.get('observableProperties', []):
            prop_uri = URIRef(prop['id'])
            
            self.graph.add((prop_uri, RDF.type, self.SOSA.ObservableProperty))
            self.graph.add((prop_uri, RDFS.label, Literal(prop['name'], lang='zh')))
            self.graph.add((prop_uri, RDFS.comment, Literal(prop['description'], lang='zh')))
    
    def _model_platforms(self):
        """建模平台"""
        for platform in self.ssn_config.get('platforms', []):
            platform_uri = URIRef(platform['id'])
            
            self.graph.add((platform_uri, RDF.type, self.SOSA.Platform))
            self.graph.add((platform_uri, RDFS.label, Literal(platform['name'], lang='zh')))
            self.graph.add((platform_uri, self.HOME.location, Literal(platform['location'])))
            
            # 关联托管的传感器
            for sensor_id in platform.get('hosts', []):
                sensor_uri = URIRef(sensor_id)
                self.graph.add((platform_uri, self.SOSA.hosts, sensor_uri))
                self.graph.add((sensor_uri, self.SOSA.isHostedBy, platform_uri))
    
    def get_sensor_info(self, sensor_id: str) -> Dict[str, Any]:
        """获取传感器信息"""
        for sensor in self.ssn_config.get('sensors', []):
            if sensor['id'] == sensor_id:
                return sensor
        return {}
    
    def get_sensors_by_location(self, location: str) -> List[Dict[str, Any]]:
        """根据位置获取传感器列表"""
        sensors = []
        for sensor in self.ssn_config.get('sensors', []):
            if sensor.get('location') == location:
                sensors.append(sensor)
        return sensors
    
    def get_sensors_by_property(self, property_type: str) -> List[Dict[str, Any]]:
        """根据观测属性获取传感器列表"""
        sensors = []
        for sensor in self.ssn_config.get('sensors', []):
            if property_type in sensor.get('observes', ''):
                sensors.append(sensor)
        return sensors
    
    def create_observation(self, sensor_id: str, value: float, timestamp: datetime = None) -> Dict[str, Any]:
        """创建观测记录"""
        if timestamp is None:
            timestamp = datetime.now()
        
        sensor_info = self.get_sensor_info(sensor_id)
        if not sensor_info:
            raise ValueError(f"传感器不存在: {sensor_id}")
        
        observation = {
            "id": f"obs_{sensor_id}_{int(timestamp.timestamp())}",
            "type": "sosa:Observation",
            "madeBySensor": sensor_id,
            "observedProperty": sensor_info.get('observes'),
            "hasResult": {
                "value": value,
                "unit": self._get_sensor_unit(sensor_info)
            },
            "resultTime": timestamp.isoformat(),
            "phenomenonTime": timestamp.isoformat()
        }
        
        return observation
    
    def _get_sensor_unit(self, sensor_info: Dict[str, Any]) -> str:
        """获取传感器单位"""
        properties = sensor_info.get('properties', {})
        range_info = properties.get('range', {})
        return range_info.get('unit', '')
    
    def validate_sensor_value(self, sensor_id: str, value: float) -> bool:
        """验证传感器值是否在有效范围内"""
        sensor_info = self.get_sensor_info(sensor_id)
        if not sensor_info:
            return False
        
        properties = sensor_info.get('properties', {})
        range_info = properties.get('range', {})
        
        if 'min' in range_info and 'max' in range_info:
            return range_info['min'] <= value <= range_info['max']
        
        return True
    
    def export_rdf(self, format: str = 'turtle') -> str:
        """导出RDF格式的语义模型"""
        return self.graph.serialize(format=format)
    
    def save_rdf(self, filepath: str, format: str = 'turtle'):
        """保存RDF格式的语义模型到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.export_rdf(format))
    
    def query_sensors(self, sparql_query: str) -> List[Dict[str, Any]]:
        """执行SPARQL查询"""
        results = []
        qres = self.graph.query(sparql_query)
        
        for row in qres:
            result = {}
            for i, var in enumerate(qres.vars):
                result[str(var)] = str(row[i])
            results.append(result)
        
        return results
    
    def get_sensor_statistics(self) -> Dict[str, Any]:
        """获取传感器网络统计信息"""
        stats = {
            "总传感器数": len(self.ssn_config.get('sensors', [])),
            "平台数": len(self.ssn_config.get('platforms', [])),
            "观测属性数": len(self.ssn_config.get('observableProperties', [])),
            "按位置分布": {},
            "按类型分布": {}
        }
        
        # 按位置统计
        for sensor in self.ssn_config.get('sensors', []):
            location = sensor.get('location', '未知')
            stats["按位置分布"][location] = stats["按位置分布"].get(location, 0) + 1
        
        # 按观测属性统计
        for sensor in self.ssn_config.get('sensors', []):
            prop_type = sensor.get('observes', '').split(':')[-1]
            stats["按类型分布"][prop_type] = stats["按类型分布"].get(prop_type, 0) + 1
        
        return stats


# 使用示例
if __name__ == "__main__":
    # 创建SSN建模器
    ssn = SSNModeling()
    
    # 打印统计信息
    print("传感器网络统计信息:")
    print(json.dumps(ssn.get_sensor_statistics(), indent=2, ensure_ascii=False))
    
    # 创建观测记录
    obs = ssn.create_observation("home:temperatureSensor_001", 23.5)
    print(f"\n观测记录: {json.dumps(obs, indent=2, ensure_ascii=False)}")
    
    # 验证传感器值
    print(f"\n值验证 (23.5°C): {ssn.validate_sensor_value('home:temperatureSensor_001', 23.5)}")
    print(f"值验证 (100°C): {ssn.validate_sensor_value('home:temperatureSensor_001', 100)}")
    
    # 导出RDF模型
    print(f"\nRDF模型已生成，包含 {len(ssn.graph)} 个三元组")
