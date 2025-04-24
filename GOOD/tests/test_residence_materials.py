"""
测试居住证明材料生成器
"""
import unittest
import json
import os
import sys
from pathlib import Path

# 添加项目根目录到系统路径
sys.path.append(str(Path(__file__).parent.parent))

from document_generator.residence_materials import ResidenceMaterialsGenerator

class TestResidenceMaterialsGenerator(unittest.TestCase):
    """测试居住证明材料生成器类"""
    
    def setUp(self):
        """设置测试环境"""
        # 准备测试配置
        self.test_config = {
            "residenceMaterials": {
                "options": [
                    "派出所开具的居住证确认单（原件）",
                    "工作居住证确认单（可复印或扫描）",
                    "居住证卡片原件（需原件进馆并签署免责声明）"
                ]
            }
        }
        
        # 创建生成器实例
        self.generator = ResidenceMaterialsGenerator(self.test_config)
    
    def test_same_consulate_no_proof_needed(self):
        """测试相同领区不需要居住证明"""
        form_data = {
            'residenceConsulate': 'beijing',
            'hukouConsulate': 'beijing',
            'applicationType': 'NORMAL'
        }
        
        materials = self.generator.get_materials(form_data)
        
        # 应该返回空列表，因为不需要居住证明
        self.assertEqual(materials, [])
    
    def test_different_consulate_proof_needed(self):
        """测试不同领区需要居住证明"""
        form_data = {
            'residenceConsulate': 'beijing',
            'hukouConsulate': 'shanghai',
            'applicationType': 'NORMAL'
        }
        
        materials = self.generator.get_materials(form_data)
        
        # 应该返回居住证明材料列表
        self.assertTrue(len(materials) > 0)
        self.assertIn("以下居住证明材料（选择一种即可）", materials[0])
    
    def test_family_application_with_members(self):
        """测试家庭申请时主申请人和部分家庭成员需要居住证明"""
        form_data = {
            'residenceConsulate': 'beijing',
            'hukouConsulate': 'shanghai',
            'applicationType': 'FAMILY',
            'familyMembers': [
                {
                    'name': '张三',
                    'residenceConsulate': 'beijing',
                    'hukouConsulate': 'beijing'  # 不需要居住证明
                },
                {
                    'name': '李四',
                    'residenceConsulate': 'beijing',
                    'hukouConsulate': 'shanghai'  # 需要居住证明
                }
            ]
        }
        
        materials = self.generator.get_materials(form_data)
        
        # 验证结果
        self.assertTrue(len(materials) > 0)
        # 应该包含主申请人和李四，但不包含张三
        self.assertIn("主申请人, 李四需要提供以下居住证明材料", materials[0])
        self.assertNotIn("张三", materials[0])
    
    def test_shanghai_special_case(self):
        """测试上海领区的特殊处理"""
        form_data = {
            'residenceConsulate': 'shanghai',
            'hukouConsulate': 'beijing',
            'applicationType': 'NORMAL'
        }
        
        materials = self.generator.get_materials(form_data)
        
        # 验证上海领区特有的居住证明材料
        self.assertTrue(len(materials) > 0)
        self.assertIn("全部需要提供", materials[0])
        self.assertIn("居住证双面复印件", materials[1])
        self.assertIn("社保", materials[2])
        self.assertIn("纳税证明", materials[3])

if __name__ == '__main__':
    unittest.main() 