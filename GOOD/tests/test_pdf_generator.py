"""
测试PDF生成器功能
"""
import unittest
import os
import json
import sys
import tempfile

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from document_generator.pdf_generator import PDFGenerator
from document_generator import DocumentGenerator


class TestPDFGenerator(unittest.TestCase):
    """测试PDF生成器类"""
    
    def setUp(self):
        """初始化测试环境"""
        # 加载测试配置
        config_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'js', 'document_config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            # 使用简单的测试配置
            self.config = {
                "basicMaterials": {
                    "all": [
                        "护照原件+首页彩色复印件",
                        "签证申请表（双面打印）",
                        "小两寸白底证件照"
                    ],
                    "details": {
                        "family": "家庭户：户首页+户主页+本人页",
                        "collective": "集体户：本人页"
                    }
                }
            }
        
        # 初始化PDF生成器和文档生成器
        self.pdf_generator = PDFGenerator(self.config)
        self.document_generator = DocumentGenerator(self.config)
    
    def test_get_visa_type_display(self):
        """测试获取签证类型显示名称方法"""
        self.assertEqual(self.pdf_generator._get_visa_type_display('SINGLE'), '单次签证')
        self.assertEqual(self.pdf_generator._get_visa_type_display('THREE'), '三年多次签证')
        self.assertEqual(self.pdf_generator._get_visa_type_display('FIVE'), '五年多次签证')
        self.assertEqual(self.pdf_generator._get_visa_type_display('UNKNOWN'), '单次签证')  # 默认值
    
    def test_get_identity_type_display(self):
        """测试获取身份类型显示名称方法"""
        self.assertEqual(self.pdf_generator._get_identity_type_display('EMPLOYED'), '在职人员')
        self.assertEqual(self.pdf_generator._get_identity_type_display('STUDENT'), '学生')
        self.assertEqual(self.pdf_generator._get_identity_type_display('FREELANCER'), '自由职业者')
        self.assertEqual(self.pdf_generator._get_identity_type_display('UNKNOWN'), '一般申请人')  # 默认值
    
    def test_get_consulate_display(self):
        """测试获取领区显示名称方法"""
        self.assertEqual(self.pdf_generator._get_consulate_display('beijing'), '北京')
        self.assertEqual(self.pdf_generator._get_consulate_display('BEIJING'), '北京')
        self.assertEqual(self.pdf_generator._get_consulate_display('shanghai'), '上海')
        self.assertEqual(self.pdf_generator._get_consulate_display('unknown'), 'unknown')  # 未知领区
    
    def test_generate_pdf_simple(self):
        """测试简单的PDF生成功能"""
        # 准备测试数据
        document_list = {
            "基本材料": ["护照原件", "签证申请表"],
            "财力证明": ["银行存款证明"]
        }
        form_data = {
            "applicantName": "测试用户",
            "visaType": "SINGLE",
            "identityType": "EMPLOYED",
            "residenceConsulate": "beijing"
        }
        
        try:
            # 尝试生成PDF
            pdf_content = self.pdf_generator.generate_pdf(document_list, form_data)
            
            # 验证生成的PDF不为空
            self.assertIsNotNone(pdf_content)
            self.assertTrue(len(pdf_content) > 0)
            
            # 将PDF写入临时文件（用于手动检查）
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(pdf_content)
                print(f"PDF文件已保存至：{temp_file.name}")
        except Exception as e:
            self.fail(f"生成PDF时出错: {str(e)}")
    
    def test_generate_pdf_with_document_generator(self):
        """测试使用DocumentGenerator生成的材料清单创建PDF"""
        # 准备表单数据
        form_data = {
            "applicantName": "测试用户",
            "visaType": "SINGLE",
            "identityType": "EMPLOYED",
            "residenceConsulate": "beijing",
            "hukouConsulate": "beijing",
            "hukouType": "family",
            "applicationType": "NORMAL",
            "previousVisit": "false"
        }
        
        try:
            # 使用DocumentGenerator生成材料清单
            document_list = self.document_generator.generate_document_list(form_data)
            
            # 使用PDF生成器生成PDF
            pdf_content = self.pdf_generator.generate_pdf(document_list, form_data)
            
            # 验证生成的PDF不为空
            self.assertIsNotNone(pdf_content)
            self.assertTrue(len(pdf_content) > 0)
        except Exception as e:
            self.fail(f"使用DocumentGenerator生成PDF时出错: {str(e)}")


if __name__ == '__main__':
    unittest.main() 