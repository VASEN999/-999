"""
日本签证材料清单生成器 - 其他材料生成模块
"""
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class OtherMaterialsGenerator:
    """其他材料生成器类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化其他材料生成器
        
        Args:
            config: 配置数据字典
        """
        self.config = config
    
    def get_materials(self, form_data: Dict[str, Any]) -> List[str]:
        """
        获取其他材料列表
        
        Args:
            form_data: 用户提交的表单数据
            
        Returns:
            其他材料列表
        """
        # 获取必要的表单数据
        residence_consulate = form_data.get('residenceConsulate', '').lower()
        identity_type = form_data.get('identityType', '')
        process_type = form_data.get('processType', '')
        application_type = form_data.get('applicationType', '')
        
        # 初始化其他材料列表
        other_materials = ["1. 和纸质照片一致的电子版照片"]
        
        # 当居住地领区是北京、申请人身份是在职人员、办理方式为普通经济材料办理时，添加税单要求
        if residence_consulate == 'beijing' and identity_type == 'EMPLOYED' and (process_type == 'NORMAL' or process_type == ''):
            other_materials.append("2. 近一年的个人所得税税单（从去年到今年相同月份）")
            other_materials.append("3. 如果税单右下角盖章是在外领区，需要额外提供领区内的营业执照副本复印件")
        
        # 检查主申请人是否为退休人员
        main_applicant_is_retired = False
        if identity_type == 'RETIRED':
            main_applicant_is_retired = True
        
        # 检查家属申请中是否有退休人员
        family_has_retired = False
        
        if application_type == 'FAMILY':
            family_members = form_data.get('familyMembers', [])
            for i, member in enumerate(family_members, 1):
                if isinstance(member, dict) and member.get('identityType') == 'RETIRED':
                    family_has_retired = True
                    break
        
        # 根据领区和退休人员情况添加退休证明要求
        if residence_consulate == 'shanghai':
            # 上海领区：只有主申请人是退休人员时才需要提供退休证明
            if main_applicant_is_retired:
                if other_materials[-1].startswith("1."):
                    next_num = 2
                else:
                    next_num = len(other_materials) + 1
                other_materials.append(f"{next_num}. 退休人员需要提供退休证或能够证明退休的文件复印件（主申请人）")
                logger.debug("上海领区：主申请人是退休人员，添加退休证明要求")
            elif family_has_retired:
                # 上海领区：家庭成员是退休人员时，不需要提供退休证明
                logger.debug("上海领区：家庭成员中有退休人员，但不需要提供退休证明")
        else:
            # 北京领区：主申请人或家庭成员中有退休人员，都需要提供退休证明
            if main_applicant_is_retired or family_has_retired:
                if other_materials[-1].startswith("1."):
                    next_num = 2
                else:
                    next_num = len(other_materials) + 1
                other_materials.append(f"{next_num}. 退休人员需要提供退休证或能够证明退休的文件复印件（包括家庭成员的申请）")
                logger.debug("北京领区：有退休人员（主申请人或家庭成员），添加退休证明要求")
        
        # 检查主申请人或家庭成员中是否有自由职业者，不管是哪个领区都添加说明
        has_freelancer = False
        
        # 检查主申请人是否为自由职业者
        if identity_type == 'FREELANCER' or identity_type == 'FREELANCE':
            has_freelancer = True
            logger.debug(f"主申请人是自由职业者: {identity_type}")
        
        # 检查家属申请中是否有自由职业者
        if application_type == 'FAMILY':
            family_members = form_data.get('familyMembers', [])
            for member in family_members:
                if isinstance(member, dict):
                    # 检查多种可能的标识
                    member_identity = member.get('identityType')
                    if member_identity == 'FREELANCER' or member_identity == 'FREELANCE':
                        has_freelancer = True
                        logger.debug(f"家庭成员中发现自由职业者: {member.get('name', '')} {member.get('number', '')}, 身份类型: {member_identity}")
                        break
        
        # 如果有自由职业者，添加相关说明
        if has_freelancer:
            # 获取下一个编号
            next_num = len(other_materials) + 1
            other_materials.append(f"{next_num}. 自由职业或无业要写收入来源说明并提供相关的证明材料（包括家庭成员的申请）")
        
        return other_materials 