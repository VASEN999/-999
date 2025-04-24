"""
日本签证材料清单生成器 - 风险评估模块
"""
import logging

logger = logging.getLogger(__name__)

class RiskAssessmentService:
    """风险评估服务类"""
    
    def __init__(self, config):
        """
        初始化风险评估服务
        
        Args:
            config: JSON格式的配置数据
        """
        self.config = config
        self.risk_config = config.get('riskAssessment', {})
    
    def assess_risk(self, form_data):
        """
        评估申请人的滞留风险
        
        Args:
            form_data: 用户提交的表单数据
            
        Returns:
            dict: 风险评估结果
        """
        logger.info("开始风险评估")
        logger.debug("评估的表单数据: %s", form_data)
        
        risk_result = {
            'is_high_risk': False,
            'risk_factors': [],
            'additional_materials': [],
            'notes': []
        }
        
        # 获取关键数据，处理可能的不同字段名和格式
        identity_type = form_data.get('identityType')
        
        # 处理教育程度，可能有多种字段名
        education_level = None
        for field in ['educationLevel', 'education', 'education_level']:
            if field in form_data and form_data[field]:
                education_level = form_data[field]
                break
        
        # 处理纳税信息，可能有多种字段名
        tax_payment = None
        for field in ['taxPayment', 'tax', 'tax_payment']:
            if field in form_data and form_data[field]:
                tax_payment = form_data[field]
                break
        
        # 处理社保信息，可能有多种字段名
        social_insurance = None
        for field in ['socialInsurance', 'social_insurance', 'insurance']:
            if field in form_data and form_data[field]:
                social_insurance = form_data[field]
                break
        
        # 处理护照状态，可能有多种字段名
        passport_status = None
        for field in ['passportStatus', 'passport_status', 'passport']:
            if field in form_data and form_data[field]:
                passport_status = form_data[field]
                break
        
        # 处理户口类型，可能有多种字段名
        hukou_type = None
        for field in ['hukouType', 'hukou_type', 'hukou']:
            if field in form_data and form_data[field]:
                hukou_type = form_data[field]
                break
        
        logger.debug("处理后的关键数据: identity_type=%s, education_level=%s, tax_payment=%s, social_insurance=%s, passport_status=%s, hukou_type=%s", 
                   identity_type, education_level, tax_payment, social_insurance, passport_status, hukou_type)
        
        # 检查高风险因素
        self._check_identity_risk(identity_type, risk_result)
        self._check_education_risk(education_level, risk_result)
        self._check_tax_risk(tax_payment, risk_result)
        self._check_social_insurance_risk(social_insurance, risk_result)
        self._check_passport_risk(passport_status, risk_result)
        self._check_hukou_risk(hukou_type, risk_result)
        
        # 如果存在风险因素，标记为高风险
        if risk_result['risk_factors']:
            risk_result['is_high_risk'] = True
            risk_result['notes'].append('申请人属于高风险群体，需要通过滞留风险评估方案。')
            risk_result['additional_materials'].extend(self._get_additional_materials())
        
        # 检查税单盖章情况
        tax_stamped = False
        for field in ['taxStamped', 'tax_stamped', 'has_tax_stamp']:
            if field in form_data:
                value = form_data[field]
                if isinstance(value, bool):
                    tax_stamped = value
                elif value in ['true', 'True', '1', 1]:
                    tax_stamped = True
                break
        
        if tax_payment and tax_stamped:
            risk_result['notes'].append('税单有盖章，需要补充社保+营业执照确认居住条件。')
            risk_result['additional_materials'].append('社保缴纳证明')
            risk_result['additional_materials'].append('营业执照复印件')
        
        # 检查社保变更频繁情况
        frequent_job_change = False
        for field in ['frequentJobChange', 'frequent_job_change', 'job_change_frequent']:
            if field in form_data:
                value = form_data[field]
                if isinstance(value, bool):
                    frequent_job_change = value
                elif value in ['true', 'True', '1', 1]:
                    frequent_job_change = True
                break
        
        if social_insurance and frequent_job_change:
            risk_result['notes'].append('过去五年社保缴纳单位变更频繁，需通过滞留风险评估方案。')
            risk_result['is_high_risk'] = True
        
        logger.info("风险评估完成，结果: is_high_risk=%s, 风险因素数量=%d", 
                  risk_result['is_high_risk'], len(risk_result['risk_factors']))
        return risk_result
    
    def _check_identity_risk(self, identity_type, risk_result):
        """检查身份相关风险"""
        if identity_type == 'FREELANCER':
            risk_result['risk_factors'].append('自由职业')
    
    def _check_education_risk(self, education_level, risk_result):
        """检查教育程度相关风险"""
        low_education_levels = ['HIGH_SCHOOL', 'JUNIOR_HIGH', 'PRIMARY', 'NONE']
        if education_level in low_education_levels:
            risk_result['risk_factors'].append('低学历')
    
    def _check_tax_risk(self, tax_payment, risk_result):
        """检查纳税相关风险"""
        if not tax_payment or tax_payment == 'NONE':
            risk_result['risk_factors'].append('无纳税')
    
    def _check_social_insurance_risk(self, social_insurance, risk_result):
        """检查社保相关风险"""
        if not social_insurance or social_insurance == 'NONE':
            risk_result['risk_factors'].append('无社保')
    
    def _check_passport_risk(self, passport_status, risk_result):
        """检查护照相关风险"""
        if passport_status == 'NEW':
            risk_result['risk_factors'].append('护照白本申请')
    
    def _check_hukou_risk(self, hukou_type, risk_result):
        """检查户口相关风险"""
        high_risk_hukou = ['REMOTE', 'FARMING']
        if hukou_type in high_risk_hukou:
            risk_result['risk_factors'].append('高危户籍')
    
    def _get_additional_materials(self):
        """获取高风险申请人需要的额外材料"""
        return [
            '详细的行程计划（包含每日具体安排）',
            '住宿预订证明',
            '往返机票预订证明',
            '在职证明原件（需加盖公章，注明职位、入职时间、准假时间）',
            '最近6个月的详细银行流水（需盖银行章）'
        ]
    
    def get_risk_assessment_guide(self):
        """获取风险评估指南"""
        guide = {
            'high_risk_groups': self.risk_config.get('highRiskGroups', []),
            'tax_verification': self.risk_config.get('taxVerification', ''),
            'frequent_job_change': self.risk_config.get('frequentJobChange', '')
        }
        return guide 