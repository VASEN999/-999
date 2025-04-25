"""
居住证明材料生成器调试工具
"""
import json
import logging
import sys
from document_generator.residence_materials import ResidenceMaterialsGenerator

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('residence_debug.log')
    ]
)

logger = logging.getLogger(__name__)

def test_residence_materials():
    """测试居住证明材料生成"""
    # 加载配置
    config = {
        "residenceMaterials": {
            "options": [
                "派出所开具的居住证确认单（原件）",
                "工作居住证确认单（可复印或扫描）",
                "居住证卡片原件（需提供原件）"
            ]
        }
    }
    
    # 示例表单数据 - 家庭申请
    form_data = {
        'residenceConsulate': 'beijing',
        'hukouConsulate': 'shanghai',
        'applicationType': 'FAMILY',
        'visaType': 'THREE',
        'processType': 'NORMAL',
        'identityType': 'EMPLOYED',
        'familyMembers': [
            {
                'name': '家庭成员1',
                'residenceConsulate': 'beijing',
                'hukouConsulate': 'beijing',  # 不需要居住证明
                'identityType': 'RETIRED'
            },
            {
                'name': '家庭成员2',
                'residenceConsulate': 'beijing',
                'hukouConsulate': 'shanghai',  # 需要居住证明
                'identityType': 'STUDENT'
            }
        ]
    }
    
    # 创建生成器
    generator = ResidenceMaterialsGenerator(config)
    
    # 测试不同的表单数据
    test_cases = [
        {
            'name': '标准家庭申请案例',
            'data': form_data
        },
        {
            'name': '没有家庭成员的家庭申请',
            'data': {**form_data, 'familyMembers': []}
        },
        {
            'name': '家庭成员缺少领区信息',
            'data': {
                **form_data,
                'familyMembers': [
                    {
                        'name': '家庭成员1',
                        'identityType': 'RETIRED'
                    }
                ]
            }
        },
        {
            'name': '非家庭申请',
            'data': {**form_data, 'applicationType': 'NORMAL', 'familyMembers': []}
        }
    ]
    
    # 遍历测试用例
    for case in test_cases:
        logger.info(f"\n测试用例: {case['name']}")
        logger.info(f"输入数据: {json.dumps(case['data'], ensure_ascii=False)}")
        
        # 生成居住证明材料
        materials = generator.get_materials(case['data'])
        
        # 输出结果
        logger.info(f"生成的居住证明材料:")
        for item in materials:
            logger.info(f"  {item}")
        logger.info("-" * 50)

if __name__ == '__main__':
    test_residence_materials() 