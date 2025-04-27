#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试带详细申请人信息确认的PDF生成
"""

import logging
import json
import os
from document_generator.basic_materials import BasicMaterialsGenerator
from document_generator.pdf_generator import PDFGenerator
from document_generator.main import DocumentGenerator

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 加载配置文件
def load_config():
    """加载材料配置文件"""
    config_path = os.path.join('static', 'js', 'document_config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("配置文件未找到: %s", config_path)
        return {}
    except json.JSONDecodeError:
        logger.error("配置文件格式错误")
        return {}

def main():
    """主测试函数"""
    # 加载配置
    config = load_config()
    
    # 创建测试数据，包含详细的申请人信息
    form_data = {
        'residenceConsulate': 'beijing',
        'applicationType': 'FAMILY',
        'hukouConsulate': 'shanghai',
        'applicantName': '测试用户',
        'identityType': 'EMPLOYED',
        'visaType': 'FIVE',
        'processType': 'TAX',
        'visitedJapan': True,
        'familyMembers': [
            {
                'relation': 'SPOUSE',
                'identityType': 'FREELANCER',
                'residenceConsulate': 'beijing',
                'hukouConsulate': 'shanghai'
            },
            {
                'relation': 'PARENT',
                'identityType': 'RETIRED',
                'residenceConsulate': 'beijing',
                'hukouConsulate': 'beijing'
            }
        ]
    }
    
    # 初始化生成器
    document_generator = DocumentGenerator(config)
    pdf_generator = PDFGenerator(config)
    
    # 生成材料清单
    document_list = document_generator.generate_document_list(form_data)
    
    # 打印生成的材料清单
    logger.info("生成的材料清单:")
    for section_name, materials in document_list.items():
        logger.info("部分: %s", section_name)
        for item in materials:
            logger.info("  - %s", item)
    
    # 生成PDF
    try:
        pdf_content = pdf_generator.generate_pdf(document_list, form_data)
        
        # 保存PDF
        with open('test_with_details.pdf', 'wb') as f:
            f.write(pdf_content)
        
        logger.info("带详细信息的PDF已保存为test_with_details.pdf")
    except Exception as e:
        logger.error("生成PDF时出错: %s", str(e), exc_info=True)

if __name__ == '__main__':
    main() 