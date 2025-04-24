"""
日本签证材料清单生成器 - 居住证明材料生成模块
"""
from typing import Dict, List, Any, Optional, Union, Tuple
import logging

logger = logging.getLogger(__name__)

class ResidenceMaterialsGenerator:
    """居住证明材料生成器类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化居住证明材料生成器
        
        Args:
            config: 配置数据字典
        """
        self.config = config
    
    def get_materials(self, form_data: Dict[str, Any]) -> List[str]:
        """
        获取居住证明材料列表
        
        Args:
            form_data: 用户提交的表单数据
            
        Returns:
            居住证明材料列表
        """
        # 获取关键数据
        residence_consulate = form_data.get('residenceConsulate', '').lower()
        hukou_consulate = form_data.get('hukouConsulate', '').lower()
        process_type = form_data.get('processType', '')
        identity_type = form_data.get('identityType', '')
        application_type = form_data.get('applicationType', '')
        
        # 日志记录输入数据，便于调试
        logger.debug(f"处理居住证明材料: residence={residence_consulate}, hukou={hukou_consulate}, type={application_type}")
        
        # 检查是否需要居住证明
        residence_proof_needed = self._check_residence_proof_needed(residence_consulate, hukou_consulate)
        
        # 特定大学生单次办理且为在读状态时，不需要居住证明
        if process_type == 'STUDENT' and identity_type == 'STUDENT':
            graduate_status = form_data.get('graduateStatus', 'auto')
            if graduate_status == 'current' or graduate_status == '在读':
                residence_proof_needed = False
                logger.info("在读大学生不需要额外的居住证明")
        
        # 如果不需要居住证明，返回空列表
        if not residence_proof_needed and application_type != 'FAMILY':
            return []
        
        # 准备居住证明材料选项
        if residence_consulate == 'shanghai' and residence_consulate != hukou_consulate:
            # 上海领区特殊处理
            options_title = '以下居住证明材料（全部需要提供）'
            shanghai_options = [
                "居住证双面复印件（上海居住证需额外附上密码）",
                "近期一年的社保（社保单最低要近期6个月缴纳在上海领区内）",
                "近期一年的纳税证明（税单最低要近期6个月缴纳在上海领区内）"
            ]
            options = shanghai_options
        else:
            # 其他领区一般处理
            options_title = '以下居住证明材料（选择一种即可）'
            options = self.config.get('residenceMaterials', {}).get('options', [])
        
        # 构建居住证明材料清单
        residence_materials = []
        
        # 根据申请类型确定标题
        if application_type == 'FAMILY':
            # 检查哪些家庭成员需要提供居住证明
            main_applicant_needs_proof = residence_proof_needed
            applicants_needing_proof = []
            
            if main_applicant_needs_proof:
                applicants_needing_proof.append("主申请人")
            
            # 处理家庭成员
            family_members_needing_proof = []
            family_members = form_data.get('familyMembers', [])
            
            # 确保family_members是列表类型
            if not isinstance(family_members, list):
                family_members = []
                logger.warning("表单数据中的familyMembers不是列表类型")
            
            # 遍历家庭成员
            for i, member in enumerate(family_members, 1):
                if not isinstance(member, dict):
                    logger.warning(f"家庭成员数据格式不正确: {member}")
                    continue
                
                # 获取家庭成员信息
                member_name = member.get('name', f'家庭成员{i}')
                member_residence = member.get('residenceConsulate', '').lower()
                member_hukou = member.get('hukouConsulate', '').lower()
                
                # 记录家庭成员数据
                logger.debug(f"处理家庭成员: {member_name}, residence={member_residence}, hukou={member_hukou}")
                
                # 检查家庭成员是否需要居住证明
                if member_residence and member_hukou:
                    member_needs_proof = self._check_residence_proof_needed(member_residence, member_hukou)
                    
                    if member_needs_proof:
                        family_members_needing_proof.append(member_name)
                        logger.info(f"家庭成员需要居住证明: {member_name}")
            
            # 合并所有需要提供居住证明的人员
            applicants_needing_proof.extend(family_members_needing_proof)
            
            # 如果有需要提供居住证明的申请人，添加列表
            if applicants_needing_proof:
                # 修改为更清晰的格式
                residence_materials.append(f"{', '.join(applicants_needing_proof)}需要提供{options_title}：")
            else:
                # 如果没有人需要提供居住证明，添加一个默认说明
                residence_materials.append(f"{options_title}：")
                logger.info("家庭申请中没有发现需要居住证明的成员")
        else:
            # 单人申请时使用原来的格式
            residence_materials.append(f"{options_title}：")
        
        # 添加居住证明材料选项
        for i, option in enumerate(options, 1):
            residence_materials.append(f"{i}. {option}")
        
        # 记录最终生成的材料清单
        logger.debug(f"生成的居住证明材料: {residence_materials}")
        return residence_materials
    
    def process_family_members_residence_proof(self, form_data: Dict[str, Any], main_applicant_needs_proof: bool = False) -> List[str]:
        """
        处理家庭成员的居住证明需求（此方法用于集中生成需要居住证明的家庭成员列表，但不再用于生成具体材料说明）
        
        Args:
            form_data: 用户提交的表单数据
            main_applicant_needs_proof: 主申请人是否需要居住证明
            
        Returns:
            家庭成员居住证明说明列表
        """
        # 此方法已被修改后的get_materials方法替代，保留但不再生成居住证明说明
        # 当主申请人不需要居住证明，但部分家庭成员需要时，仍需要此方法返回需要证明的成员列表
        family_residence_notes = []
        
        # 检查是否是家庭申请
        if form_data.get('applicationType') != 'FAMILY':
            return family_residence_notes
        
        # 获取家庭成员信息
        family_members = form_data.get('familyMembers', [])
        if not family_members or not isinstance(family_members, list):
            return family_residence_notes
        
        # 处理每个家庭成员
        for i, member in enumerate(family_members, 1):
            if not member or not isinstance(member, dict):
                continue
                
            member_name = member.get('name', f'家庭成员{i}')
            member_residence = member.get('residenceConsulate', '').lower()
            member_hukou = member.get('hukouConsulate', '').lower()
            
            # 检查家庭成员是否需要居住证明
            member_needs_proof = self._check_residence_proof_needed(member_residence, member_hukou)
            
            if member_needs_proof:
                family_residence_notes.append(f"{member_name} 需要提供居住证明材料")
        
        return family_residence_notes
    
    def _check_residence_proof_needed(self, residence_consulate: str, hukou_consulate: str) -> bool:
        """
        检查是否需要居住证明
        
        Args:
            residence_consulate: 居住地领区
            hukou_consulate: 户籍所在地领区
            
        Returns:
            是否需要居住证明
        """
        # 如果居住地领区和户籍所在地领区不同，则需要居住证明
        if not residence_consulate or not hukou_consulate:
            return False
            
        return residence_consulate.lower() != hukou_consulate.lower() 