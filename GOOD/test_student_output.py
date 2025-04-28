"""
测试特定大学生单次办理方式的材料清单生成
"""
import os
import sys
import json
from collections import OrderedDict
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 添加当前目录到sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入需要的模块
from document_generator.main import DocumentGenerator

def load_config():
    """加载材料配置文件"""
    config_path = os.path.join(os.path.dirname(__file__), 'static', 'js', 'document_config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"配置文件未找到: {config_path}")
        return {}
    except json.JSONDecodeError:
        print("配置文件格式错误")
        return {}

def main():
    """主函数"""
    # 加载配置
    config = load_config()
    
    # 初始化文档生成器
    document_generator = DocumentGenerator(config)
    
    # 测试用表单数据 - 特定大学生单次办理方式
    form_data = {
        'processType': 'STUDENT',  # 特定大学生单次办理
        'identityType': 'STUDENT',  # 学生身份
        'graduateStatus': 'current',  # 在读学生
        'residenceConsulate': 'beijing',
        'hukouConsulate': 'shanghai',
        'applicationType': 'SINGLE',
        'visaType': 'SINGLE'
    }
    
    # 生成材料清单
    document_list = document_generator.generate_document_list(form_data)
    
    # 打印结果
    print("\n=== 材料清单生成结果 ===")
    for section_name, materials in document_list.items():
        print(f"\n【{section_name}】")
        for item in materials:
            print(f"- {item}")
    
    # 检查特定部分
    if '财力证明' in document_list:
        print("\n警告: 财力证明部分仍然存在")
    else:
        print("\n成功: 财力证明部分已被移除")
    
    # 检查学籍学历证明部分
    if '学籍/学历证明' in document_list:
        print(f"\n学籍/学历证明部分内容: {document_list['学籍/学历证明']}")
    else:
        print("\n警告: 学籍/学历证明部分不存在")

if __name__ == "__main__":
    main() 