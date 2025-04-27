"""
日本签证材料清单生成器 - 基本材料生成模块
"""
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class BasicMaterialsGenerator:
    """基本材料生成器类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化基本材料生成器
        
        Args:
            config: 配置数据字典
        """
        self.config = config
    
    def get_materials(self, form_data: Dict[str, Any]) -> List[str]:
        """
        获取基本材料列表
        
        Args:
            form_data: 用户提交的表单数据
            
        Returns:
            基本材料列表
        """
        # 获取居住地领区信息
        residence_consulate = form_data.get('residenceConsulate', '').lower()
        application_type = form_data.get('applicationType')
        identity_type = form_data.get('identityType', '')
        
        # 上海领区特有的基本材料
        if residence_consulate == 'shanghai':
            basic_materials = [
                "护照原件+首页彩色复印件（剩余有效期大于7个月）",
                "签证申请表（双面打印）",
                "小两寸（3.5cmx4.5cm）白底证件照（近期6个月内拍摄）",
                "户口本复印件（家庭户：户首页+户主页+本人页）"
            ]
            
            # 根据身份类型添加特定材料
            if identity_type == 'EMPLOYED':
                basic_materials.append("在职证明（原件）")
            
            # 为上海领区的绑签申请添加额外材料
            if application_type == 'BINDING':
                basic_materials.append("签证持有人的护照首页复印件 + 签证页复印件")
                
                # 根据关系类型添加不同的关系证明材料
                family_relation = form_data.get('familyRelation', '')
                if family_relation == 'SPOUSE':
                    basic_materials.append("与签证持有人的关系证明材料（结婚证/户口本）")
                elif family_relation == 'PARENT':
                    basic_materials.append("与签证持有人的关系证明材料（子女出生证明/户口本）")
                elif family_relation == 'CHILD':
                    basic_materials.append("与签证持有人的关系证明材料（出生证明/户口本）")
                else:
                    basic_materials.append("与签证持有人的关系证明材料（结婚证/户口本/出生证明等）")
            
            logger.debug("生成上海领区基本材料: %s", basic_materials)
            return basic_materials
        
        # 北京领区及其他领区使用默认的基本材料列表
        basic_materials = self.config.get('basicMaterials', {}).get('all', []).copy()
        
        # 获取户口类型，默认为家庭户
        hukou_type = form_data.get('hukouType', 'family')
        if not hukou_type or hukou_type == 'auto':
            hukou_type = 'family'
        
        # 获取户口材料详情
        hukou_details = None
        if hukou_type == 'family' or hukou_type == 'FAMILY':
            hukou_details = self.config.get('basicMaterials', {}).get('details', {}).get('family', '')
        elif hukou_type == 'collective' or hukou_type == 'COLLECTIVE':
            hukou_details = self.config.get('basicMaterials', {}).get('details', {}).get('collective', '')
        
        # 添加户口材料详情
        if hukou_details:
            # 修改户口本描述
            for i, item in enumerate(basic_materials):
                if '户口本' in item:
                    basic_materials[i] = f"{item}（{hukou_details}）"
                    break
        
        # 为北京领区的绑签申请添加额外材料
        if application_type == 'BINDING':
            basic_materials.append("签证持有人的护照首页复印件 + 签证页复印件")
            
            # 根据关系类型添加不同的关系证明材料
            family_relation = form_data.get('familyRelation', '')
            if family_relation == 'SPOUSE':
                basic_materials.append("与签证持有人的关系证明材料（结婚证/户口本）")
            elif family_relation == 'PARENT':
                basic_materials.append("与签证持有人的关系证明材料（子女出生证明/户口本）")
            elif family_relation == 'CHILD':
                basic_materials.append("与签证持有人的关系证明材料（出生证明/户口本）")
            else:
                basic_materials.append("与签证持有人的关系证明材料（结婚证/户口本/出生证明等）")
        
        logger.debug("生成基本材料: %s", basic_materials)
        return basic_materials 