"""
日本签证材料清单生成器 - 主模块
"""
from typing import Dict, List, Any, OrderedDict as OrderedDictType
from collections import OrderedDict
import logging

from document_generator.basic_materials import BasicMaterialsGenerator
from document_generator.identity_materials import IdentityMaterialsGenerator
from document_generator.financial_materials import FinancialMaterialsGenerator
from document_generator.residence_materials import ResidenceMaterialsGenerator
from document_generator.family_materials import FamilyMaterialsGenerator
from document_generator.other_materials import OtherMaterialsGenerator
from document_generator.utils import get_visa_duration, get_consulate_text, check_has_family

logger = logging.getLogger(__name__)

class DocumentGenerator:
    """材料清单生成器主类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化生成器
        
        Args:
            config: JSON格式的配置数据
        """
        self.config = config
        
        # 初始化各个子生成器
        self.basic_generator = BasicMaterialsGenerator(config)
        self.identity_generator = IdentityMaterialsGenerator(config)
        self.financial_generator = FinancialMaterialsGenerator(config)
        self.residence_generator = ResidenceMaterialsGenerator(config)
        self.family_generator = FamilyMaterialsGenerator(config)
        self.other_generator = OtherMaterialsGenerator(config)
        
        # 定义材料显示顺序
        self.section_order = ['基本信息', '基本材料', '学籍/学历证明', '学籍/学历证明及情况说明', 
                             '工作证明', '财力证明', '居住证明材料', '家属材料', '其他材料']
    
    def generate_document_list(self, form_data: Dict[str, Any]) -> OrderedDictType[str, List[str]]:
        """
        根据表单数据生成所需证件列表
        
        Args:
            form_data: 用户提交的表单数据
            
        Returns:
            有序字典，包含各类材料
        """
        # 初始化结果字典
        document_list: OrderedDictType[str, List[str]] = OrderedDict()
        
        # 获取主要表单数据
        identity_type = form_data.get('identityType', '')
        application_type = form_data.get('applicationType', '')
        residence_consulate = form_data.get('residenceConsulate', '')
        hukou_consulate = form_data.get('hukouConsulate', '')
        process_type = form_data.get('processType', '')
        visa_duration = get_visa_duration(form_data)
        
        # 1. 添加基本信息
        document_list['基本信息'] = self._generate_basic_info(form_data)
        
        # 2. 添加基本材料
        document_list['基本材料'] = self.basic_generator.get_materials(form_data)
        
        # 3. 添加身份特定材料（根据不同处理方式）
        if process_type == 'STUDENT':
            # 特定大学生单次办理不添加普通身份材料，但添加学籍材料
            if identity_type == 'STUDENT':
                student_materials = self.financial_generator._generate_student_materials(form_data)
                if student_materials:
                    document_list['学籍/学历证明'] = student_materials
            else:
                # 非学生身份使用特定大学生办理方式
                document_list['学籍/学历证明及情况说明'] = ["非在读学生使用特定大学生办理方式，需要提供曾经的学籍或学历证明"]
        elif process_type in ['NORMAL', 'SIMPLIFIED'] and identity_type == 'STUDENT':
            # 学生使用普通经济材料办理时，添加学籍材料而不是普通身份材料
            student_materials = self.financial_generator._generate_student_materials(form_data)
            if student_materials:
                document_list['学籍/学历证明'] = student_materials
        elif application_type == 'ECONOMIC':
            # 使用家庭成员经济材料申请时，不添加身份特定材料
            pass
        else:
            # 其他情况添加身份特定材料
            identity_materials = self.identity_generator.get_materials(identity_type, process_type)
            if identity_materials:
                if identity_type == 'STUDENT':
                    document_list['学籍/学历证明'] = identity_materials
                elif identity_type == 'EMPLOYED':
                    document_list['工作证明'] = identity_materials
                else:
                    document_list[self._get_identity_section_name(identity_type)] = identity_materials
        
        # 4. 添加财力证明材料
        financial_materials = self.financial_generator.get_materials(form_data)
        if financial_materials:
            document_list['财力证明'] = financial_materials
        
        # 5. 添加居住证明材料
        residence_materials = self.residence_generator.get_materials(form_data)
        
        # 处理家庭成员和家属的居住证明需求
        has_family = check_has_family(form_data)
        residence_proof_needed = self.residence_generator._check_residence_proof_needed(
            residence_consulate, hukou_consulate)
            
        # 根据申请类型处理居住证明材料
        if application_type == 'FAMILY':
            # 对于家庭申请，居住证明材料已经在residence_generator.get_materials中处理
            if residence_materials:
                document_list['居住证明材料'] = residence_materials
        else:
            # 普通申请或绑签申请
            if residence_materials:
                document_list['居住证明材料'] = residence_materials
                
                # 如果有家属（非家庭申请），添加家属居住证明说明
                if has_family and residence_proof_needed and application_type != 'BINDING':
                    document_list['居住证明材料'].append("持签人家属需提供上述居住材料之一")
        
        # 6. 添加家属材料
        family_materials = self.family_generator.get_materials(form_data)
        if family_materials and application_type != 'BINDING':
            document_list['家属材料'] = family_materials
        
        # 7. 添加其他材料
        other_materials = self.other_generator.get_materials(form_data)
        if other_materials:
            document_list['其他材料'] = other_materials
        
        # 确保返回的材料按照指定顺序排列
        ordered_list = OrderedDict()
        for section in self.section_order:
            if section in document_list:
                ordered_list[section] = document_list[section]
        
        logger.debug("生成的材料清单: %s", ordered_list)
        return ordered_list
    
    def _generate_basic_info(self, form_data: Dict[str, Any]) -> List[str]:
        """生成基本信息部分"""
        # 获取领区信息
        residence_consulate = form_data.get('residenceConsulate', '')
        hukou_consulate = form_data.get('hukouConsulate', '')
        
        # 获取领区显示文本
        residence_text = get_consulate_text(residence_consulate)
        hukou_text = get_consulate_text(hukou_consulate)
        
        # 根据签证类型和申请类型获取显示文本
        visa_type_text = self._get_visa_type_text(form_data)
        
        # 构建基本信息
        basic_info = [
            f"居住地领区: {residence_text}",
            f"户籍所在地领区: {hukou_text}",
            f"申请类型: {visa_type_text}"
        ]
        
        # 如果是绑签申请，添加家属签证信息
        if form_data.get('applicationType') == 'BINDING':
            family_visa_type = form_data.get('familyVisaType', '')
            family_visa_text = "三年多次往返签证" if family_visa_type == 'THREE' else "五年多次往返签证"
            basic_info.append(f"家属签证类型: {family_visa_text}")
        
        return basic_info
    
    def _get_visa_type_text(self, form_data: Dict[str, Any]) -> str:
        """获取签证类型显示文本"""
        # 获取签证类型和处理方式
        visa_duration = get_visa_duration(form_data)
        application_type = form_data.get('applicationType', '')
        process_type = form_data.get('processType', '')
        
        # 基本签证类型文本
        visa_type_text = "单次签证"
        if visa_duration == 'THREE':
            visa_type_text = "三年多次往返签证"
        elif visa_duration == 'FIVE':
            visa_type_text = "五年多次往返签证"
        
        # 根据申请类型修改签证类型显示文本
        if application_type == 'BINDING':
            family_relation = form_data.get('familyRelation', '')
            relation_text = ''
            if family_relation == 'SPOUSE':
                relation_text = '配偶'
            elif family_relation == 'PARENT':
                relation_text = '父母'
            elif family_relation == 'CHILD':
                relation_text = '子女'
            
            visa_type_display = "三年多次往返签证" if visa_duration == 'THREE' else "五年多次往返签证"
            visa_type_text = f"申请人是{visa_type_display}持有人的{relation_text}"
        elif process_type == 'SIMPLIFIED':
            # 新政简化三年办理方式的特殊处理
            visa_type_text = "三年多次签证（新政简化）"
        elif process_type == 'STUDENT':
            # 特定大学生单次办理方式
            visa_type_text = "单次签证（学生专用）"
        
        return visa_type_text
    
    def _get_identity_section_name(self, identity_type: str) -> str:
        """根据身份类型获取对应的材料部分名称"""
        identity_sections = {
            'EMPLOYED': '工作证明',
            'RETIRED': '退休证明',
            'FREELANCER': '自由职业者证明',
            'STUDENT': '学籍/学历证明',
            'CHILD': '未成年人材料'
        }
        return identity_sections.get(identity_type, '身份证明材料') 