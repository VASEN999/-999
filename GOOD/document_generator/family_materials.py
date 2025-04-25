"""
日本签证材料清单生成器 - 家属材料生成模块
"""
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class FamilyMaterialsGenerator:
    """家属材料生成器类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化家属材料生成器
        
        Args:
            config: 配置数据字典
        """
        self.config = config
    
    def get_materials(self, form_data: Dict[str, Any]) -> List[str]:
        """
        获取家属材料列表
        
        Args:
            form_data: 用户提交的表单数据
            
        Returns:
            家属材料列表
        """
        # 绑签申请不需要家属材料，直接返回空列表
        application_type = form_data.get('applicationType', '')
        if application_type == 'BINDING':
            return []
            
        # 检查是否有家属
        has_family = self._check_has_family(form_data)
        
        # 如果没有家属，返回空列表
        if not has_family:
            return []
        
        # 获取居住地和户籍地信息
        residence_consulate = form_data.get('residenceConsulate', '').lower()
        hukou_consulate = form_data.get('hukouConsulate', '').lower()
        
        # 检查是否需要居住证明
        residence_proof_needed = residence_consulate != hukou_consulate
        
        # 初始化家属材料列表
        family_materials = []
        
        # 根据申请类型获取不同家属材料
        application_type = form_data.get('applicationType', '')
        
        if application_type == 'BINDING':
            # 绑签申请
            family_relation = form_data.get('familyRelation', '')
            family_visa_type = form_data.get('familyVisaType', '')
            
            # 获取绑签配置
            binding_config = self.config.get('familyApplications', {}).get('afterMainApplicant', {})
            
            # 添加基本绑签材料
            family_materials.append("家属绑签所需材料：")
            family_materials.extend(binding_config.get('materials', []))
            
            # 添加关系特定说明
            relation_text = self._get_relation_text(family_relation)
            if relation_text:
                family_materials.append(f"需提供与{relation_text}的关系证明")
            
            # 添加单次绑签的特殊说明
            if family_visa_type == 'SINGLE':
                note = binding_config.get('note', '')
                if note:
                    family_materials.append(f"注意：{note}")
                    
        elif application_type == 'FAMILY':
            # 家庭申请 - 直接添加材料项目，不添加标题
            family_materials.append("1.基本材料内的1、2、3、4项目")
            family_materials.append("2.与主申请人的关系证明")
            
            # 获取家庭成员信息
            family_members = form_data.get('familyMembers', [])
            if family_members and isinstance(family_members, list) and len(family_members) > 0:
                # 获取有特别要求的家庭成员
                member_idx = 3  # 从第3点开始编号
                
                for i, member in enumerate(family_members, 1):
                    if not member or not isinstance(member, dict):
                        continue
                        
                    member_name = member.get('name', f'家庭成员{i}')
                    member_identity = member.get('identityType', '')
                    
                    # 根据身份类型生成更详细和易读的说明
                    if member_identity == 'STUDENT':
                        family_materials.append(f"{member_idx}. {member_name}需要提供学信网在线学籍验证报告")
                        member_idx += 1
                    elif member_identity == 'CHILD':
                        family_materials.append(f"{member_idx}. {member_name}需要由监护人陪同并提供监护关系证明")
                        member_idx += 1
                    elif member_identity == 'RETIRED':
                        # 退休人员材料统一显示在其他材料部分，不再在家属材料中显示
                        logger.debug(f"家庭成员 {member_name} 是退休人员({member_identity})，材料将在其他材料部分显示")
                        pass
                    elif member_identity == 'FREELANCER' or member_identity == 'FREELANCE':
                        # 自由职业者的材料要求统一显示在其他材料部分
                        # 不再在家属材料中显示
                        logger.debug(f"家庭成员 {member_name} 是自由职业者({member_identity})，材料将在其他材料部分显示")
                        pass
        
        else:
            # 一般家属材料（普通申请但有家属）
            if residence_proof_needed:
                family_materials.append("所有家属也需要提供居住证明材料")
            
            family_materials.append("所有家属需要准备与主申请人相同的基本材料")
            family_materials.append("需提供与主申请人的关系证明（结婚证/出生证明等）")
        
        return family_materials
    
    def _check_has_family(self, form_data: Dict[str, Any]) -> bool:
        """检查是否有家属"""
        # 如果是绑签申请，返回False（绑签申请自身就是作为家属申请，不需要家属材料）
        # 如果是家庭申请，返回True
        application_type = form_data.get('applicationType', '')
        if application_type == 'BINDING':
            return False
        elif application_type == 'FAMILY':
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
    
    def _get_relation_text(self, relation: str) -> str:
        """获取关系文本"""
        relation_texts = {
            'SPOUSE': '配偶',
            'PARENT': '父母',
            'CHILD': '子女'
        }
        return relation_texts.get(relation, '家属')
    
    def _get_identity_special_note(self, identity_type: str) -> str:
        """获取身份特殊说明"""
        identity_notes = {
            'STUDENT': '学生需提供学信网材料',
            'CHILD': '未成年人需由监护人陪同',
            'RETIRED': '退休人员需提供退休证',
            'FREELANCER': '自由职业者需提供财力证明',
            'FREELANCE': '自由职业者需提供财力证明'
        }
        return identity_notes.get(identity_type, '') 