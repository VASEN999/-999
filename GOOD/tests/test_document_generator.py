"""
文档生成器单元测试
"""
import unittest
import json
import os
import sys
from collections import OrderedDict
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from document_generator import DocumentGenerator
from document_generator.basic_materials import BasicMaterialsGenerator
from document_generator.identity_materials import IdentityMaterialsGenerator
from document_generator.financial_materials import FinancialMaterialsGenerator
from document_generator.residence_materials import ResidenceMaterialsGenerator
from document_generator.family_materials import FamilyMaterialsGenerator
from document_generator.other_materials import OtherMaterialsGenerator

class TestDocumentGenerator(unittest.TestCase):
    """文档生成器测试类"""
    
    @classmethod
    def setUpClass(cls):
        """准备测试环境"""
        # 加载测试配置
        with open(os.path.join(os.path.dirname(__file__), 'fixtures', 'test_config.json'), 'r', encoding='utf-8') as f:
            cls.test_config = json.load(f)
        
        # 初始化生成器
        cls.generator = DocumentGenerator(cls.test_config)
        
    def test_basic_materials(self):
        """测试基本材料生成"""
        # 创建测试表单数据
        form_data = {
            'identityType': 'EMPLOYED',
            'visaType': 'SINGLE',
            'residenceConsulate': 'beijing',
            'hukouConsulate': 'beijing',
            'hukouType': 'family'
        }
        
        # 生成基本材料
        basic_generator = BasicMaterialsGenerator(self.test_config)
        result = basic_generator.get_materials(form_data)
        
        # 验证结果
        self.assertIsInstance(result, list)
        self.assertTrue(any('护照原件' in item for item in result))
        self.assertTrue(any('签证申请表' in item for item in result))
        self.assertTrue(any('户口本' in item and '家庭户' in item for item in result))
    
    def test_identity_materials_employed(self):
        """测试在职人员身份材料生成"""
        identity_generator = IdentityMaterialsGenerator(self.test_config)
        result = identity_generator.get_materials('EMPLOYED')
        
        # 验证结果
        self.assertIsInstance(result, list)
        self.assertTrue(any('税单' in item for item in result))
    
    def test_identity_materials_student(self):
        """测试学生身份材料生成"""
        identity_generator = IdentityMaterialsGenerator(self.test_config)
        result = identity_generator.get_materials('STUDENT')
        
        # 验证结果
        self.assertIsInstance(result, list)
        self.assertTrue(any('学信网' in item for item in result))
    
    def test_financial_materials_single(self):
        """测试单次签证财力材料生成"""
        # 创建测试表单数据
        form_data = {
            'identityType': 'EMPLOYED',
            'visaType': 'SINGLE',
            'residenceConsulate': 'beijing',
            'hukouConsulate': 'beijing',
            'processType': 'NORMAL'
        }
        
        # 生成财力材料
        financial_generator = FinancialMaterialsGenerator(self.test_config)
        result = financial_generator.get_materials(form_data)
        
        # 验证结果
        self.assertIsInstance(result, list)
        self.assertTrue(any('存款/理财证明' in item for item in result))
        self.assertTrue(any('10万' in item for item in result))
    
    def test_residence_materials_different_consulate(self):
        """测试不同领区居住证明材料生成"""
        # 创建测试表单数据（居住地和户籍地不同）
        form_data = {
            'residenceConsulate': 'beijing',
            'hukouConsulate': 'shanghai'
        }
        
        # 生成居住证明材料
        residence_generator = ResidenceMaterialsGenerator(self.test_config)
        result = residence_generator.get_materials(form_data)
        
        # 验证结果
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)
        self.assertTrue(any('居住证明材料' in item for item in result))
    
    def test_residence_materials_same_consulate(self):
        """测试相同领区居住证明材料生成"""
        # 创建测试表单数据（居住地和户籍地相同）
        form_data = {
            'residenceConsulate': 'beijing',
            'hukouConsulate': 'beijing'
        }
        
        # 生成居住证明材料
        residence_generator = ResidenceMaterialsGenerator(self.test_config)
        result = residence_generator.get_materials(form_data)
        
        # 验证结果（应该是空列表，因为不需要居住证明）
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)
    
    def test_family_materials_with_family(self):
        """测试有家属情况下的家属材料生成"""
        # 创建测试表单数据
        form_data = {
            'hasFamily': True,
            'residenceConsulate': 'beijing',
            'hukouConsulate': 'shanghai'
        }
        
        # 生成家属材料
        family_generator = FamilyMaterialsGenerator(self.test_config)
        result = family_generator.get_materials(form_data)
        
        # 验证结果
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)
        self.assertTrue(any('关系证明' in item for item in result))
    
    def test_family_materials_no_family(self):
        """测试无家属情况下的家属材料生成"""
        # 创建测试表单数据
        form_data = {
            'hasFamily': False
        }
        
        # 生成家属材料
        family_generator = FamilyMaterialsGenerator(self.test_config)
        result = family_generator.get_materials(form_data)
        
        # 验证结果（应该是空列表，因为没有家属）
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)
    
    def test_complete_document_generation(self):
        """测试完整的材料清单生成"""
        # 创建测试表单数据
        form_data = {
            'identityType': 'EMPLOYED',
            'visaType': 'SINGLE',
            'residenceConsulate': 'beijing',
            'hukouConsulate': 'beijing',
            'processType': 'NORMAL',
            'hukouType': 'family',
            'hasFamily': False
        }
        
        # 生成完整材料清单
        result = self.generator.generate_document_list(form_data)
        
        # 验证结果
        self.assertIsInstance(result, OrderedDict)
        self.assertIn('基本信息', result)
        self.assertIn('基本材料', result)
        self.assertIn('财力证明', result)
        
        # 验证基本信息内容
        self.assertTrue(any('居住地领区: 北京' in item for item in result['基本信息']))
        
        # 验证基本材料内容
        self.assertTrue(any('护照原件' in item for item in result['基本材料']))
        
        # 验证财力证明内容
        self.assertTrue(any('存款/理财证明' in item for item in result['财力证明']))
        
        # 验证"在职证明"在某个章节中
        found_work_cert = False
        for section_items in result.values():
            if any('在职证明' in item for item in section_items):
                found_work_cert = True
                break
        self.assertTrue(found_work_cert, "在职证明未在任何章节中找到")
    
    def test_tax_process_type(self):
        """测试税单办理方式"""
        # 创建测试表单数据
        form_data = {
            'identityType': 'EMPLOYED',
            'visaType': 'SINGLE',
            'residenceConsulate': 'beijing',
            'hukouConsulate': 'beijing',
            'processType': 'TAX'
        }
        
        # 生成财力材料
        financial_generator = FinancialMaterialsGenerator(self.test_config)
        result = financial_generator.get_materials(form_data)
        
        # 验证结果
        self.assertIsInstance(result, list)
        self.assertTrue(any('税单办理' in item for item in result))
        self.assertTrue(any('北京领区' in item for item in result))
    
    def test_student_process_type(self):
        """测试特定大学生办理方式"""
        # 创建测试表单数据
        form_data = {
            'identityType': 'STUDENT',
            'visaType': 'SINGLE',
            'residenceConsulate': 'beijing',
            'hukouConsulate': 'beijing',
            'processType': 'STUDENT',
            'graduateStatus': 'current'
        }
        
        # 生成财力材料
        financial_generator = FinancialMaterialsGenerator(self.test_config)
        result = financial_generator.get_materials(form_data)
        
        # 验证结果
        self.assertIsInstance(result, list)
        self.assertTrue(any('学信网在线学籍验证报告' in item for item in result))

if __name__ == '__main__':
    unittest.main() 