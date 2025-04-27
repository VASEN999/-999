#!/usr/bin/env python3
"""
测试空家庭成员PDF生成功能
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
    """测试生成包含空家庭成员的PDF"""
    # 加载配置
    config = {}
    
    # 创建生成器
    document_generator = DocumentGenerator(config)
    pdf_generator = PDFGenerator(config)
    
    # 创建测试表单数据 - 有applicationType=FAMILY但空的familyMembers
    form_data = {
        'applicantName': '测试申请人',
        'applicationType': 'FAMILY',
        'identityType': 'EMPLOYED',
        'residenceConsulate': 'shanghai',
        'hukouConsulate': 'beijing',
        'visaType': 'SINGLE',
        'processType': 'NORMAL',
        'previousVisit': 'false',
        'familyMembers': [] # 空数组
    }
    
    # 测试不同形式的空家庭成员
    form_data_with_string = form_data.copy()
    form_data_with_string['familyMembers'] = "[]"  # 空数组字符串
    
    form_data_without = form_data.copy()
    del form_data_without['familyMembers']  # 完全没有家庭成员字段
    
    logger.info("测试1: 有空数组的家庭成员数据")
    test_pdf_generation(document_generator, pdf_generator, form_data, 'test_empty_family_array.pdf')
    
    logger.info("测试2: 有空字符串数组的家庭成员数据")
    test_pdf_generation(document_generator, pdf_generator, form_data_with_string, 'test_empty_family_string.pdf')
    
    logger.info("测试3: 没有家庭成员字段的情况")
    test_pdf_generation(document_generator, pdf_generator, form_data_without, 'test_no_family_field.pdf')

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