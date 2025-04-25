"""
日本签证材料清单生成器 - 财力证明材料生成模块
"""
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class FinancialMaterialsGenerator:
    """财力证明材料生成器类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化财力证明材料生成器
        
        Args:
            config: 配置数据字典
        """
        self.config = config
    
    def get_materials(self, form_data: Dict[str, Any]) -> List[str]:
        """
        生成财力证明材料列表
        
        Args:
            form_data: 用户提交的表单数据
            
        Returns:
            财力证明材料列表
        """
        # 提取表单数据
        process_type = form_data.get('processType', '')
        identity_type = form_data.get('identityType', '')
        application_type = form_data.get('applicationType', '')
        visa_duration = self._get_visa_duration(form_data)
        
        # 初始化财力材料列表
        financial_materials = []
        
        # 绑签申请的特殊处理
        if application_type == 'BINDING':
            return ["签证持有人的财力证明材料（能够确认年收入的存款证明或税单）"]
            
        # 根据不同申请类型和处理方式选择不同的财力材料生成逻辑
        if application_type == 'ECONOMIC':
            # 使用家庭成员经济材料申请
            financial_materials = self._generate_family_economic_materials()
        elif process_type == 'TAX':
            # 税单办理方式
            financial_materials = self._generate_tax_materials(form_data, visa_duration)
        elif process_type == 'STUDENT':
            # 特定大学生办理
            financial_materials = self._generate_student_materials(form_data)
        elif process_type == 'SIMPLIFIED':
            # 新政简化三年办理
            financial_materials = self._generate_simplified_materials()
        else:
            # 普通经济材料办理
            financial_materials = self._generate_normal_materials(form_data, visa_duration, identity_type)
        
        logger.debug("生成财力证明材料: %s", financial_materials)
        return financial_materials
    
    def _get_visa_duration(self, form_data: Dict[str, Any]) -> str:
        """获取标准化的签证期限"""
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
    
    def _generate_tax_materials(self, form_data: Dict[str, Any], visa_duration: str) -> List[str]:
        """生成税单办理的财力材料"""
        residence_consulate = form_data.get('residenceConsulate', '').lower()
        
        # 获取领区特定的税单要求
        tax_requirements = self.config.get('processMethods', {}).get('TAX', {}).get('requirements', {})
        consulate_requirements = tax_requirements.get(residence_consulate, tax_requirements.get('beijing', {}))
        
        # 获取签证类型特定的税单金额要求
        visa_tax_req = consulate_requirements.get(visa_duration, {})
        tax_amount = visa_tax_req.get('amount', 0)
        tax_description = visa_tax_req.get('description', '')
        
        if tax_description:
            return [f"税单办理：{tax_description}"]
        else:
            return ["税单办理：请准备符合要求的个人所得税税单"]
    
    def _generate_student_materials(self, form_data: Dict[str, Any]) -> List[str]:
        """生成特定大学生的财力材料"""
        graduate_status = form_data.get('graduateStatus', '')
        
        # 获取学生特定配置
        student_config = self.config.get('visaRequirements', {}).get('SINGLE', {}).get('education', {})
        
        if graduate_status == 'graduate' or graduate_status == '已毕业':
            # 毕业生
            return [student_config.get('graduate', '提供学信网电子学历注册备案表（毕业三年内）')]
        else:
            # 在读学生
            return [student_config.get('student', '提供学信网在线学籍验证报告（领区内大学在读）')]
    
    def _generate_simplified_materials(self) -> List[str]:
        """生成新政简化三年办理的财力材料"""
        simplified_config = self.config.get('visaRequirements', {}).get('THREE', {}).get('simplified', {})
        return simplified_config.get('requirements', [])
    
    def _generate_normal_materials(self, form_data: Dict[str, Any], visa_duration: str, identity_type: str) -> List[str]:
        """生成普通经济材料办理的财力材料"""
        # 获取用户选择的经济材料类型
        economic_material = form_data.get('economicMaterial', '')
        residence_consulate = form_data.get('residenceConsulate', '').lower()
        
        # 根据经济材料类型返回对应的要求
        if economic_material:
            # 信用卡金卡
            if economic_material in ['credit_card', 'creditCard']:
                return ["信用卡金卡及以上（自行遮挡CVV码）+有效性证明（近期三个月电子账单或pos机联）", 
                        "备注：账单联系信用卡客服索取，需体现姓名/卡号/额度/消费明细"]
            
            # 工资流水相关选项
            elif economic_material in ['salary_single', 'salarySingle']:
                return ["年工资流水10万以上（需可以验证，并仅统计能确认是工资收入的项）"]
            elif economic_material in ['salary_three', 'salaryThree']:
                return ["年工资流水20万以上（需可以验证，并仅统计能确认是工资收入的项）"]
            elif economic_material in ['salary_five', 'salaryFive']:
                return ["年工资流水50万以上（需可以验证，并仅统计能确认是工资收入的项）"]
            
            # 存款证明相关选项
            elif economic_material in ['deposit_single', 'depositSingle']:
                return [f"存款证明：10万以上（需要是可验证银行开具的存款证明（需提前确认））"]
            elif economic_material in ['deposit_three', 'depositThree']:
                return [f"存款证明：50万以上（需要是可验证银行开具的存款证明（需提前确认））"]
            elif economic_material in ['deposit_five', 'depositFive']:
                return [f"存款证明：100万以上（需要是可验证银行开具的存款证明（需提前确认））"]
        
        # 如果没有选择经济材料类型或无法识别选项，则使用默认逻辑
        materials = []
        
        # 获取签证类型特定的存款要求
        visa_req = self.config.get('visaRequirements', {}).get(visa_duration, {})
        bank_req = visa_req.get('bankBalance', {})
        tax_req = visa_req.get('taxAmount', {})
        
        # 添加存款证明要求
        if bank_req:
            bank_amount = bank_req.get('amount', 0) / 10000  # 转换为万
            bank_description = bank_req.get('description', '')
            
            # 获取支持的银行列表
            supported_banks = self.config.get('economicMaterials', {}).get('bankStatement', {}).get('supportedBanks', [])
            banks_text = "、".join(supported_banks[:3]) + "等银行"
            
            if bank_description:
                materials.append(f"存款证明：{bank_description}（{banks_text}可出具）")
            else:
                materials.append(f"存款证明：需提供{bank_amount}万以上的存款证明（{banks_text}可出具）")
        
        # 添加税单要求（仅对在职人员）
        if identity_type == 'EMPLOYED' and tax_req:
            tax_amount = tax_req.get('amount', 0) / 10000  # 转换为万
            tax_description = tax_req.get('description', '')
            
            if tax_description:
                materials.append(f"税单要求：{tax_description}")
            else:
                materials.append(f"税单要求：近一年的个人所得税税单，金额超过{tax_amount}万")
        
        return materials
    
    def _generate_family_economic_materials(self) -> List[str]:
        """生成使用家庭成员经济材料的财力材料"""
        return ["使用直系亲属的经济材料（存款证明、税单等）", "需提供关系证明"] 