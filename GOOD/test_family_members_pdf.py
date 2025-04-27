#!/usr/bin/env python3
"""
测试家庭成员PDF生成功能
"""
import sys
import os
import json
import logging
from document_generator import DocumentGenerator
from document_generator.pdf_generator import PDFGenerator

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """测试生成包含家庭成员信息的PDF"""
    # 加载配置
    config = {}
    
    # 创建生成器
    document_generator = DocumentGenerator(config)
    pdf_generator = PDFGenerator(config)
    
    # 创建测试表单数据
    form_data = {
        'applicantName': '测试申请人',
        'applicationType': 'FAMILY',
        'identityType': 'EMPLOYED',
        'residenceConsulate': 'shanghai',
        'hukouConsulate': 'beijing',
        'visaType': 'SINGLE',
        'processType': 'NORMAL',
        'previousVisit': 'false',
        'familyMembers': [
            {
                'relation': 'SPOUSE',
                'identityType': 'EMPLOYED',
                'residenceConsulate': 'shanghai',
                'hukouConsulate': 'beijing',
                'number': 1
            },
            {
                'relation': 'CHILD',
                'identityType': 'STUDENT',
                'residenceConsulate': 'shanghai',
                'hukouConsulate': 'beijing',
                'number': 2
            }
        ]
    }
    
    # 测试字符串形式的familyMembers
    form_data_with_string = form_data.copy()
    form_data_with_string['familyMembers'] = json.dumps(form_data['familyMembers'])
    
    logger.info("测试1: 使用对象形式的家庭成员数据")
    test_pdf_generation(document_generator, pdf_generator, form_data, 'test_family_object.pdf')
    
    logger.info("测试2: 使用字符串形式的家庭成员数据")
    test_pdf_generation(document_generator, pdf_generator, form_data_with_string, 'test_family_string.pdf')

def test_pdf_generation(document_generator, pdf_generator, form_data, output_filename):
    """测试PDF生成并保存到文件"""
    try:
        # 生成材料清单
        document_list = document_generator.generate_document_list(form_data)
        
        # 记录生成的材料清单，便于调试
        logger.debug("为PDF生成的材料清单:")
        for section_name, materials in document_list.items():
            logger.debug("部分: %s", section_name)
            for item in materials:
                logger.debug("  - %s", item)
        
        # 生成PDF
        pdf_content = pdf_generator.generate_pdf(document_list, form_data)
        
        # 保存PDF到文件
        with open(output_filename, 'wb') as f:
            f.write(pdf_content)
        
        logger.info("PDF生成成功，已保存到: %s", os.path.abspath(output_filename))
        return True
    except Exception as e:
        logger.error("PDF生成失败: %s", str(e), exc_info=True)
        return False

if __name__ == "__main__":
    main() 