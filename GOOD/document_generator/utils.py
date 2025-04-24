"""
日本签证材料清单生成器 - 工具函数模块
"""
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

def get_visa_duration(form_data: Dict[str, Any]) -> str:
    """
    从表单数据中获取标准化的签证期限
    
    Args:
        form_data: 用户提交的表单数据
        
    Returns:
        标准化的签证期限（SINGLE, THREE, FIVE）
    """
    visa_duration = None
    for field in ['visaDuration', 'visaType']:
        if field in form_data and form_data[field]:
            visa_duration = form_data[field]
            break
    
    # 标准化签证期限
    if visa_duration in ['SINGLE', 'single', '单次']:
        return 'SINGLE'
    elif visa_duration in ['THREE', 'three', '三年多次']:
        return 'THREE'
    elif visa_duration in ['FIVE', 'five', '五年多次']:
        return 'FIVE'
    else:
        return 'SINGLE'  # 默认为单次

def get_consulate_text(consulate_code: str) -> str:
    """
    获取领区显示文本
    
    Args:
        consulate_code: 领区代码
        
    Returns:
        领区的中文名称
    """
    consulate_texts = {
        'beijing': '北京',
        'shanghai': '上海',
        'guangzhou': '广州',
        'shenyang': '沈阳',
        'qingdao': '青岛',
        'dalian': '大连',
        'chongqing': '重庆',
        'wuhan': '武汉',
        'xian': '西安',
        'fuzhou': '福州',
        'nanning': '南宁',
        'hangzhou': '杭州',
        'nanjing': '南京',
        'chengdu': '成都',
        'shenzhen': '深圳',
        'suzhou': '苏州',
        'tianjin': '天津',
        'haerbin': '哈尔滨',
        'changsha': '长沙',
        'kunming': '昆明',
        'xiamen': '厦门',
        'jinan': '济南',
        'hefei': '合肥',
        'zhengzhou': '郑州',
        'nanchang': '南昌',
        'guiyang': '贵阳',
        'lanzhou': '兰州',
        'xining': '西宁',
        'yinchuan': '银川',
        'huhehaote': '呼和浩特',
        'wulumuqi': '乌鲁木齐',
        'lasa': '拉萨',
        'other': '其他'
    }
    
    # 确保使用小写进行比较
    if not consulate_code:
        return '未指定'
    
    return consulate_texts.get(consulate_code.lower(), '未指定')

def check_has_family(form_data: Dict[str, Any]) -> bool:
    """
    检查是否有家属
    
    Args:
        form_data: 用户提交的表单数据
        
    Returns:
        是否有家属
    """
    # 如果是绑签或家庭申请，一定有家属
    application_type = form_data.get('applicationType', '')
    if application_type in ['BINDING', 'FAMILY']:
        return True
    
    # 检查其他家属相关字段
    for field in ['hasFamily', 'has_family', 'familyMembers']:
        if field in form_data:
            value = form_data[field]
            if isinstance(value, bool):
                return value
            elif isinstance(value, list) and len(value) > 0:
                return True
            elif value in ['true', 'True', '1', 1]:
                return True
    
    return False 