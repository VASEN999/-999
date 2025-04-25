"""
日本签证材料清单生成器 - 材料生成模块
"""
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)

class DocumentGenerator:
    """材料清单生成器类"""
    
    def __init__(self, config):
        """
        初始化生成器
        
        Args:
            config: JSON格式的配置数据
        """
        self.config = config
    
    def generate_document_list(self, form_data):
        """根据表单数据生成所需证件列表"""
        document_list = {}
        
        # 获取主要表单数据
        identity_type = form_data.get('identityType', '')
        visa_type = form_data.get('visaType', '')
        application_type = form_data.get('applicationType', '')
        residence_consulate = form_data.get('residenceConsulate', '')
        hukou_consulate = form_data.get('hukouConsulate', '')
        process_type = form_data.get('processType', '')
        
        # 对于绑签申请，处理方式默认为普通经济材料办理
        if application_type == 'BINDING':
            process_type = 'NORMAL'
            # 根据家属签证类型设置申请人的签证类型
            family_visa_type = form_data.get('familyVisaType', '')
            if family_visa_type:
                visa_type = family_visa_type
        
        # 标准化签证类型
        visa_duration = None
        for field in ['visaDuration', 'visaType']:
            if field in form_data and form_data[field]:
                visa_duration = form_data[field]
                break
        
        # 标准化签证期限值并设置显示文本
        visa_type_text = "单次签证"
        if visa_duration in ['SINGLE', 'single', '单次']:
            visa_duration = 'SINGLE'
            visa_type_text = "单次签证"
        elif visa_duration in ['THREE', 'three', '三年多次']:
            visa_duration = 'THREE'
            visa_type_text = "三年多次往返签证"
        elif visa_duration in ['FIVE', 'five', '五年多次']:
            visa_duration = 'FIVE'
            visa_type_text = "五年多次往返签证"
        else:
            # 默认为单次
            visa_duration = 'SINGLE'
            visa_type_text = "单次签证"
        
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
            visa_duration = 'THREE'  # 确保签证类型固定为三年
        elif process_type == 'STUDENT':
            # 特定大学生单次办理方式
            visa_type_text = "单次签证（学生专用）"
            visa_duration = 'SINGLE'  # 确保签证类型固定为单次
        
        # 设置领区显示文本
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
        
        # 获取领区显示文本，确保使用小写进行比较
        residence_text = consulate_texts.get(residence_consulate.lower() if residence_consulate else None, '未指定')
        hukou_text = consulate_texts.get(hukou_consulate.lower() if hukou_consulate else None, '未指定')
        
        # 添加基本信息到材料清单
        document_list['基本信息'] = [
            f"居住地领区: {residence_text}",
            f"户籍所在地领区: {hukou_text}",
            f"申请类型: {visa_type_text}"
        ]
        
        # 如果是绑签申请，添加家属签证信息
        if application_type == 'BINDING':
            family_visa_text = "三年多次往返签证" if visa_type == 'THREE' else "五年多次往返签证"
            document_list['基本信息'].append(f"家属签证类型: {family_visa_text}")
        
        # 检查是否有家属
        has_family = False
        for field in ['hasFamily', 'has_family', 'familyMembers']:
            if field in form_data:
                value = form_data[field]
                if isinstance(value, bool):
                    has_family = value
                elif isinstance(value, list) and len(value) > 0:
                    has_family = True
                elif value in ['true', 'True', '1', 1]:
                    has_family = True
                break
        
        logger.debug("处理后的关键数据: identity_type=%s, residence_consulate=%s, hukou_consulate=%s, visa_duration=%s, has_family=%s", 
                    identity_type, residence_consulate, hukou_consulate, visa_duration, has_family)
        
        # 检查是否是家庭申请
        is_family_application = application_type == 'FAMILY'
        
        # 添加基本材料
        basic_materials = self._get_basic_materials(form_data)
        
        # 修改在职人员特定材料处理逻辑，确保税单信息不包含在基本材料中
        if process_type == 'STUDENT':
            # 特定大学生单次办理不添加普通身份材料
            identity_materials = []
        elif process_type == 'NORMAL' and identity_type == 'STUDENT':
            # 学生使用普通经济材料办理时，不需要学信网材料
            identity_materials = []
        elif process_type == 'SIMPLIFIED' and identity_type == 'STUDENT':
            # 学生使用新政简化三年办理时，不需要学信网材料
            identity_materials = []
        elif application_type == 'ECONOMIC':
            # 使用家庭成员经济材料申请时，不添加身份特定材料
            identity_materials = []
        elif identity_type == 'EMPLOYED':
            # 确保身份材料不包含税单信息，这些将在其他材料中统一处理
            identity_materials = self._get_identity_materials(identity_type)
        elif identity_type == 'FREELANCER' and process_type == 'TAX':
            # 自由职业者选择税单办理时，不显示"个税app无需开具的截图"
            identity_materials = []
            for item in self.config['identityMaterials'].get('FREELANCER', []):
                if "个税app无需开具" not in item:
                    identity_materials.append(item)
        else:
            # 其他身份类型正常处理
            identity_materials = self._get_identity_materials(identity_type)
        
        # 检查是否需要居住证明
        residence_proof_needed = self._check_residence_proof_needed(residence_consulate, hukou_consulate)
        
        # 特定大学生单次办理且为在读状态时，不需要居住证明
        if process_type == 'STUDENT' and identity_type == 'STUDENT':
            current_graduate_status = form_data.get('graduateStatus', 'auto')
            if current_graduate_status == 'current' or current_graduate_status == '在读':
                residence_proof_needed = False
                logger.info("在读大学生不需要额外的居住证明")
        
        # 获取财力证明材料
        financial_materials = self._get_financial_materials(form_data)
        
        # 获取居住证明材料
        residence_materials = self._get_residence_materials(residence_proof_needed, form_data)
        
        # 检查是否为上海领区，确保居住证明材料正确显示
        if residence_proof_needed and form_data.get('residenceConsulate', '').lower() == 'shanghai' and form_data.get('residenceConsulate', '').lower() != form_data.get('hukouConsulate', '').lower():
            # 确保上海领区的居住证明材料包含所有三项
            residence_materials = ['以下居住证明材料（全部需要提供）：']
            shanghai_options = [
                "居住证双面复印件（上海居住证需额外附上密码）",
                "近期一年的社保（社保单最低要近期6个月缴纳在上海领区内）",
                "近期一年的纳税证明（税单最低要近期6个月缴纳在上海领区内）"
            ]
            for i, option in enumerate(shanghai_options, 1):
                residence_materials.append(f"{i}. {option}")
        
        # 处理家庭成员和家属的居住证明需求
        needs_residence_note = False
        family_residence_notes = []
        
        # 处理家庭申请中的家庭成员
        if application_type == 'FAMILY':
            family_residence_notes = self.process_family_members_residence_proof(form_data, residence_proof_needed)
            if family_residence_notes:
                needs_residence_note = True
        
        # 处理家属是否需要居住证明（针对家庭成员或有家属的情况）
        if (has_family or application_type == 'FAMILY') and residence_proof_needed:
            needs_residence_note = True
        
        # 根据需要添加居住证明说明
        if needs_residence_note:
            residence_consulate = form_data.get('residenceConsulate', '').lower()
            
            if not residence_materials:  # 如果主申请人不需要居住证明
                residence_materials = ['以下人员需要提供居住证明材料:']
                
                # 添加所有家庭成员的居住证明需求
                if family_residence_notes:
                    residence_materials.extend(family_residence_notes)
                
                # 添加家属的居住证明需求（如果有家属）
                if has_family and application_type != 'FAMILY':
                    residence_materials.append("所有家属也需要提供居住证明材料")
                
                # 添加居住证明材料选项
                if residence_consulate == 'shanghai':
                    residence_materials.append('上海领区需要提供以下全部居住证明材料:')
                    options = [
                        "居住证双面复印件（上海居住证需额外附上密码）",
                        "近期一年的社保（社保单最低要近期6个月缴纳在上海领区内）",
                        "近期一年的纳税证明（税单最低要近期6个月缴纳在上海领区内）"
                    ]
                else:
                    residence_materials.append('可选择以下居住证明材料之一:')
                    options = [
                        "派出所开具的居住证确认单（原件）",
                        "工作居住证确认单（可复印或扫描）",
                        "居住证卡片原件（需提供原件）"
                    ]
                
                for i, option in enumerate(options, 1):
                    residence_materials.append(f"{i}. {option}")
            else:  # 如果主申请人已经需要居住证明
                # 添加主申请人需要居住证明的说明
                if residence_materials and residence_materials[0] != "主申请人需要提供居住证明材料":
                    residence_materials.insert(0, "主申请人需要提供居住证明材料")
                
                # 添加所有家庭成员的居住证明需求
                if family_residence_notes:
                    if residence_consulate == 'shanghai':
                        residence_materials.append('同时，以下家庭成员也需要提供上海领区特有的全部居住证明材料:')
                    else:
                        residence_materials.append('同时，以下家庭成员也需要提供居住证明材料:')
                    residence_materials.extend(family_residence_notes)
                
                # 添加家属的居住证明需求（如果有家属）
                if has_family and application_type != 'FAMILY':
                    if residence_consulate == 'shanghai':
                        residence_materials.append("所有家属也需要提供上海领区特有的全部居住证明材料")
                    else:
                        residence_materials.append("所有家属也需要提供居住证明材料")
        
        # 获取家属材料
        family_materials = self._get_family_materials(has_family, residence_proof_needed)
        
        # 获取其他材料
        other_materials = self._get_other_materials(form_data, visa_duration)
        
        # 根据办理方式决定材料标题和内容
        if process_type == 'STUDENT':
            # 特定大学生单次办理使用"学籍/学历证明"作为标题
            graduate_status = form_data.get('graduateStatus', 'auto')
            
            # 获取学籍/学历证明材料
            financial_materials = self._get_financial_materials(form_data)
            
            # 区分不同身份类型显示不同标题和材料
            if identity_type == 'EMPLOYED':
                # 在职人员需要添加额外的在职证明
                document_list['学籍/学历证明'] = ["学信网电子注册备案表"]
                
                # 根据申请类型调整税单说明文本
                tax_prefix = "仅主申请人需要提供：" if application_type == 'FAMILY' else ""
                
                # 税单信息移动到其他材料中，不再创建单独的工作证明部分
                other_materials.append(f"{tax_prefix}近一年的个人所得税税单（从去年到今年相同月份）")
                other_materials.append(f"{tax_prefix}如果税单右下角盖章是在外领区，需要额外提供领区内的营业执照副本复印件")
            elif identity_type == 'STUDENT':
                # 学生添加学信网材料
                student_materials = ["学信网学籍在线验证报告"]
                
                # 如果是在读，标注学籍信息；如果是毕业，标注学历信息
                current_graduate_status = form_data.get('graduateStatus', 'auto')
                if current_graduate_status == 'current' or current_graduate_status == '在读':
                    student_materials.append("登录学信网(https://www.chsi.com.cn/)，查询并打印学籍信息，须本人签名")
                else:
                    student_materials.append("登录学信网(https://www.chsi.com.cn/)，查询并打印学历信息，须本人签名")
                
                # 添加到文档列表
                document_list['学籍/学历证明'] = student_materials + financial_materials
            elif identity_type == 'FREELANCE' or identity_type == 'UNEMPLOYED':
                # 自由职业或无业人员选择特定大学生单次
                document_list['学籍/学历证明'] = ["学信网电子注册备案表", "学信网学历在线验证报告（https://www.chsi.com.cn/）"]
            elif identity_type == 'RETIRED':
                # 退休人员选择特定大学生单次
                document_list['学籍/学历证明'] = ["学信网电子注册备案表", "学信网学历在线验证报告（https://www.chsi.com.cn/）"]
            elif identity_type == 'CHILD':
                # 学龄前儿童选择特定大学生单次（不太可能发生，但也处理）
                document_list['学籍/学历证明'] = ["监护人学信网电子注册备案表", "监护人学信网学历在线验证报告（https://www.chsi.com.cn/）"]
            else:
                # 其他身份类型
                document_list['学籍/学历证明'] = ["学信网电子注册备案表", "学信网学历在线验证报告（https://www.chsi.com.cn/）"]
            
            logger.info("特定大学生单次办理材料分类: 身份类型=%s, 标题=%s", 
                      identity_type, list(document_list.keys()))
        else:
            # 其他办理方式使用"财力证明"
            if financial_materials:
                document_list['财力证明'] = financial_materials
        
        # 为在职人员添加税单盖章说明，但如果是特定大学生单次办理方式则已在上方单独处理
        if identity_type == 'EMPLOYED' and process_type != 'STUDENT' and application_type != 'ECONOMIC':
            # 根据申请类型调整税单说明文本
            tax_prefix = "主申请人需要提供：" if application_type == 'FAMILY' else ""
            
            # 只有当不是税单办理方式时，才在其他材料中添加税单说明
            if process_type != 'TAX':
                other_materials.append(f"{tax_prefix}近一年的个人所得税税单（从去年到今年相同月份）")
            
            # 无论是否使用税单办理，都需要添加税单盖章提示
            other_materials.append(f"{tax_prefix}如果税单右下角盖章是在外领区，需要额外提供领区内的营业执照副本复印件")
        
        # 按固定顺序添加材料
        # 修改这里，使所有基本材料包括身份特定材料重新编号
        all_basic_materials = []
        
        # 首先合并基本材料和身份特定材料
        combined_basic_items = []
        
        # 添加基本材料项（去掉编号）
        for item in basic_materials:
            # 提取出不包含编号的材料内容
            item_content = item.split('. ', 1)[1] if '. ' in item else item
            combined_basic_items.append(item_content)
        
        # 添加身份特定材料项
        for item in identity_materials:
            combined_basic_items.append(item)
        
        # 重新添加序号
        for i, item in enumerate(combined_basic_items, 1):
            all_basic_materials.append(f"{i}. {item}")
        
        document_list['基本材料'] = all_basic_materials
        
        if residence_materials:
            document_list['居住证明材料'] = residence_materials
        if family_materials:
            document_list['家属材料'] = family_materials
        if other_materials:
            document_list['其他材料'] = other_materials
        
        # 确保所有项都是列表类型
        for key in document_list.keys():
            if not isinstance(document_list[key], list):
                document_list[key] = [str(document_list[key])]
        
        # 设置结果格式
        result = {
            "status": "success",
            "document_list": document_list,
            "ordered_sections": ["基本信息", "基本材料", "学籍/学历证明", "学籍/学历证明及情况说明", "财力证明", "家属材料", "居住证明材料", "其他材料"],
            "visa_type": visa_type_text
        }
        
        logger.info("材料清单生成完成，包含以下分类: %s", list(document_list.keys()))
        return result
    
    def _get_basic_materials(self, form_data):
        """获取基本材料"""
        # 获取居住地领区信息
        residence_consulate = form_data.get('residenceConsulate', '').lower()
        application_type = form_data.get('applicationType')
        
        # 上海领区特有的基本材料
        if residence_consulate == 'shanghai':
            basic_items = [
                "1. 护照原件+首页彩色复印件（剩余有效期大于7个月）",
                "2. 签证申请表（双面打印）",
                "3. 小两寸（3.5cmx4.5cm）白底证件照（近期6个月内拍摄）",
                "4. 户口本复印件（家庭户：户首页+户主页+本人页）"
            ]
            
            # 为上海领区的绑签申请添加额外两项材料
            if application_type == 'BINDING':
                basic_items.append("5. 签证持有人的护照首页复印件 + 签证页复印件")
                
                # 根据关系类型添加不同的关系证明材料
                family_relation = form_data.get('familyRelation', '')
                if family_relation == 'SPOUSE':
                    basic_items.append("6. 与签证持有人的关系证明材料（结婚证/户口本）")
                elif family_relation == 'PARENT':
                    basic_items.append("6. 与签证持有人的关系证明材料（子女出生证明/户口本）")
                elif family_relation == 'CHILD':
                    basic_items.append("6. 与签证持有人的关系证明材料（出生证明/户口本）")
                else:
                    basic_items.append("6. 与签证持有人的关系证明材料（结婚证/户口本/出生证明等）")
            
            return basic_items
        
        # 获取通用基本材料列表（不添加序号）
        basic_items = []
        for item in self.config.get('basicMaterials', {}).get('all', []):
            if "户口本复印件" not in item:
                basic_items.append(item)
        
        # 添加户口本复印件，并基于户口类型添加详细说明
        hukou_type = form_data.get('hukouType', 'family')
        
        # 添加户口本复印件说明
        if hukou_type == 'collective':
            basic_items.append("户口本复印件（集体户：户首页 + 本人页）")
        else:
            basic_items.append("户口本复印件（家庭户：户首页 + 本人页）")
        
        # 为绑签申请添加家属护照和签证复印件
        if application_type == 'BINDING':
            basic_items.append("签证持有人的护照首页复印件 + 签证页复印件")
            # 添加关系证明材料
            family_relation = form_data.get('familyRelation', '')
            relation_text = ''
            if family_relation == 'SPOUSE':
                relation_text = '结婚证/户口本'
            elif family_relation == 'PARENT':
                relation_text = '子女出生证明/户口本'
            elif family_relation == 'CHILD':
                relation_text = '出生证明/户口本'
            else:
                relation_text = '结婚证、出生证明、户口本等'
            
            basic_items.append(f"与签证持有人的关系证明材料（{relation_text}）")
        
        # 重新添加序号
        numbered_items = []
        for i, item in enumerate(basic_items, 1):
            numbered_items.append(f"{i}. {item}")
            
        return numbered_items
    
    def _get_identity_materials(self, identity_type):
        """获取身份特定材料"""
        identity_materials = []
        if identity_type and identity_type in self.config.get('identityMaterials', {}):
            identity_materials = self.config['identityMaterials'][identity_type]
            
            # 移除在职人员身份材料中的税单相关内容，这些内容将在其他材料中统一处理
            if identity_type == 'EMPLOYED':
                filtered_materials = []
                for item in identity_materials:
                    if "个人所得税" not in item and "税单" not in item:
                        filtered_materials.append(item)
                identity_materials = filtered_materials
        
        return identity_materials
    
    def _check_residence_proof_needed(self, residence_consulate, hukou_consulate):
        """检查是否需要居住证明"""
        if residence_consulate and hukou_consulate and residence_consulate != hukou_consulate:
            return True
        return False
    
    def _get_financial_materials(self, form_data):
        """获取财力证明材料列表"""
        materials = []
        identity_type = form_data.get('identityType')
        process_type = form_data.get('processType')
        economic_material = form_data.get('economicMaterial')
        application_type = form_data.get('applicationType')
        
        # 绑签申请的特殊处理
        if application_type == 'BINDING':
            family_relation = form_data.get('familyRelation', '')
            family_visa_type = form_data.get('familyVisaType', '')
            
            holder_text = ''
            if family_relation == 'SPOUSE':
                holder_text = '配偶'
            elif family_relation == 'PARENT': 
                holder_text = '子女'
            elif family_relation == 'CHILD':
                holder_text = '父母'
            
            visa_text = ''
            if family_visa_type == 'THREE':
                visa_text = '三年多次往返签证'
            elif family_visa_type == 'FIVE':
                visa_text = '五年多次往返签证'
            
            # 检查是否上海领区且提供了签证持有人身份信息
            residence_consulate = form_data.get('residenceConsulate', '').lower()
            if residence_consulate == 'shanghai' and 'familyHolderIdentity' in form_data:
                holder_identity = form_data.get('familyHolderIdentity', '')
                identity_text = ''
                
                if holder_identity == 'EMPLOYED':
                    identity_text = '在职人员'
                    materials = [f"需提供{holder_text}{visa_text}申请时使用的经济材料",
                                f"签证持有人为{identity_text}，需额外提供在职证明原件"]
                elif holder_identity == 'RETIRED':
                    identity_text = '退休人员'
                    materials = [f"需提供{holder_text}{visa_text}申请时使用的经济材料",
                                f"签证持有人为{identity_text}，需额外提供退休证复印件"]
                elif holder_identity == 'FREELANCE':
                    identity_text = '自由职业或无业'
                    materials = [f"需提供{holder_text}{visa_text}申请时使用的经济材料",
                                f"签证持有人为{identity_text}，需额外提供情况说明及相关佐证材料"]
                else:
                    materials = [f"需提供{holder_text}{visa_text}申请时使用的经济材料"]
            else:
                materials = [f"需提供{holder_text}{visa_text}申请时使用的经济材料"]
            
            return materials
            
        # 使用家庭成员经济材料申请的特殊处理
        if application_type == 'ECONOMIC':
            # 无论是北京还是上海领区，都显示相同的材料清单
            materials = [
                "1. 需提供直系亲属的经济材料（如：税单/存款/理财证明）", 
                "2. 与直系亲属的关系证明（如：户口本/出生证明/结婚证）"
            ]
            return materials
            
        # 根据不同的办理方式和材料选择提供对应的财力证明材料
        if process_type == 'TAX':
            materials = ["个人所得税完税证明（近一年）"]
        elif process_type == 'NORMAL':
            # 普通经济材料办理根据经济材料选项决定
            # 获取签证类型
            visa_duration = None
            for field in ['visaDuration', 'visaType']:
                if field in form_data and form_data[field]:
                    visa_duration = form_data[field]
                    break
                
            if economic_material:
                # 家庭申请单次签证不能使用信用卡
                if application_type == 'FAMILY' and visa_duration in ['SINGLE', 'single', '单次'] and economic_material == 'credit_card':
                    materials = ["家庭申请单次签证不能使用信用卡，请使用存款/理财证明或其他财力证明"]
                elif economic_material == 'deposit_single':
                    materials = ["10万元以上存款/理财证明原件（需要是可验证银行开具的存款/理财证明）"]
                elif economic_material == 'deposit_three':
                    materials = ["50万元以上存款/理财证明原件（需要是可验证银行开具的存款/理财证明）"]
                elif economic_material == 'deposit_five':
                    materials = ["100万元以上存款/理财证明原件（需要是可验证银行开具的存款/理财证明）"]
                elif economic_material == 'credit_card':
                    materials = [
                        "信用卡正反面复印件（自行遮挡CVV码）",
                        "信用卡有效性证明（近三个月电子账单截图或POS机回单）"
                    ]
                # 上海领区工资流水选项
                elif economic_material == 'salary_single':
                    materials = [
                        "近期12个月可认定为工资的可验证银行账户对账单（统计年收入10万以上）",
                        "备注：近期6个月工资项流水需要是连续的"
                    ]
                elif economic_material == 'salary_three':
                    materials = [
                        "近期12个月可认定为工资的可验证银行账户对账单（统计年收入20万以上）",
                        "备注：近期6个月工资项流水需要是连续的"
                    ]
                elif economic_material == 'salary_five':
                    materials = [
                        "近期12个月可认定为工资的可验证银行账户对账单（统计年收入50万以上）",
                        "备注：近期6个月工资项流水需要是连续的"
                    ]
                else:
                    materials = ["存款/理财证明或其他财力证明"]
            else:
                materials = ["存款/理财证明或其他财力证明"]
        elif process_type == 'STUDENT':
            # 特定大学生单次办理无需财力证明
            return []
        elif process_type == 'SIMPLIFIED':
            # 新政简化三年办理需要提供历史签证证明材料而非财力证明
            materials = [
                "近三年两次日本签证的签证发放通知书复印件（非特大单次）",
                "两次的入境许可贴纸复印件（如在旧护照上，需额外复印旧护照首页）",
                "近期5年出入境记录复印件"
            ]
            return materials
        else:
            # 其他情况下根据身份类型选择默认的财力证明材料
            if identity_type == 'EMPLOYED':
                materials = ["银行存款/理财证明（建议10万元以上）或活期存折复印件"]
            elif identity_type == 'STUDENT':
                materials = ["父母银行存款/理财证明（建议10万元以上）或活期存折复印件"]
            elif identity_type == 'RETIRED':
                materials = ["银行存款/理财证明（建议10万元以上）或活期存折复印件"]
            elif identity_type == 'FREELANCE':
                materials = ["银行存款/理财证明（建议10万元以上）或活期存折复印件"]
            elif identity_type == 'CHILD':
                materials = ["监护人银行存款/理财证明（建议10万元以上）或活期存折复印件"]
        
        return materials
    
    def _get_residence_materials(self, residence_proof_needed, form_data=None):
        """获取居住证明材料"""
        if not residence_proof_needed:
            return []
        
        residence_materials = []
        
        # 如果有表单数据，检查领区
        if form_data:
            residence_consulate = form_data.get('residenceConsulate', '').lower()
            hukou_consulate = form_data.get('hukouConsulate', '').lower()
            
            # 上海领区特有的居住证明材料
            if residence_consulate == 'shanghai' and residence_consulate != hukou_consulate:
                residence_materials.append('以下居住证明材料（全部需要提供）：')
                shanghai_options = [
                    "居住证双面复印件（上海居住证需额外附上密码）",
                    "近期一年的社保（社保单最低要近期6个月缴纳在上海领区内）",
                    "近期一年的纳税证明（税单最低要近期6个月缴纳在上海领区内）"
                ]
                for i, option in enumerate(shanghai_options, 1):
                    residence_materials.append(f"{i}. {option}")
                
                return residence_materials
        
        # 默认居住证明材料（适用于北京和其他领区）
        residence_materials.append('以下居住证明材料（其中之一）：')
        # 使用最新的居住证明材料选项
        options = [
            "派出所开具的居住证确认单（原件）",
            "工作居住证确认单（可复印或扫描）",
            "居住证卡片原件（需提供原件）"
        ]
        for i, option in enumerate(options, 1):
            residence_materials.append(f"{i}. {option}")
        
        return residence_materials
    
    def _get_family_materials(self, has_family, residence_proof_needed):
        """获取家属材料"""
        family_materials = []
        if has_family and 'familyApplications' in self.config:
            # 重新定义家属材料的格式
            family_materials = [
                "基本材料内的1、2、3、4项",
                "与主申请人的关系证明材料（如结婚证、出生证明、户口本等）"
            ]
            
            # 不再在家属材料中添加居住证明说明，统一在居住证明材料部分处理
        return family_materials
    
    def process_family_members_residence_proof(self, form_data, main_applicant_needs_proof=False):
        """处理家庭成员的居住证明需求"""
        family_residence_notes = []
        family_members = form_data.get('familyMembers', [])
        
        if not family_members or not isinstance(family_members, list):
            return family_residence_notes
        
        # 获取主申请人的居住地领区
        main_residence_consulate = form_data.get('residenceConsulate', '').lower()
        
        for i, member in enumerate(family_members, 1):
            if isinstance(member, dict):
                residence_consulate = member.get('residenceConsulate')
                hukou_consulate = member.get('hukouConsulate')
                
                # 检查家庭成员是否需要居住证明
                if residence_consulate and hukou_consulate and residence_consulate != hukou_consulate:
                    relation = member.get('relation', '')
                    relation_text = ''
                    
                    if relation == 'SPOUSE':
                        relation_text = '主申请人的配偶'
                    elif relation == 'PARENT':
                        relation_text = '主申请人的父母'
                    elif relation == 'CHILD':
                        relation_text = '主申请人的子女'
                    else:
                        relation_text = f'家庭成员{i}'
                    
                    # 根据主申请人是否需要居住证明调整文本
                    if main_applicant_needs_proof:
                        family_residence_notes.append(f"{relation_text}也需要提供居住证明材料")
                    else:
                        family_residence_notes.append(f"{relation_text}需要提供居住证明材料")
                        
                    # 如果是上海领区，添加特殊提示
                    if main_residence_consulate == 'shanghai':
                        family_residence_notes.append(f"{relation_text}需要提供上海领区特有的全部居住证明材料")
        
        return family_residence_notes
    
    def _get_other_materials(self, form_data, visa_duration):
        """获取其他材料"""
        # 添加指定的其他材料
        other_materials = []
        
        # 特殊处理新政简化三年办理方式
        process_type = form_data.get('processType')
        identity_type = form_data.get('identityType')
        application_type = form_data.get('applicationType')
        residence_consulate = form_data.get('residenceConsulate', '').lower()
        
        # 为不同身份类型的申请人使用家庭成员经济材料申请添加特定材料
        if application_type == 'ECONOMIC':
            if identity_type == 'EMPLOYED':
                # 在职人员需要提供税单
                other_materials.append("近一年的个人所得税税单（从去年到今年相同月份）")
                other_materials.append("如果税单右下角盖章是在外领区，需要额外提供领区内的营业执照副本复印件")
            elif identity_type == 'FREELANCER' or identity_type == 'FREELANCE':
                # 自由职业者需要提供的材料
                other_materials.append("个税app无需开具的截图")
                other_materials.append("收入来源说明")
                other_materials.append("相关附件证明")
            elif identity_type == 'RETIRED':
                # 退休人员需要提供的材料
                other_materials.append("退休证复印件")
        
        if process_type == 'SIMPLIFIED':
            other_materials.append("和纸质照片一致的电子版照片")
            other_materials.append("提供的签证发放通知书必须是本人的，且已赴日旅行")
        else:
            other_materials.append("和纸质照片一致的电子版照片")
        
        # 处理退休人员家庭成员的退休证要求
        family_members = form_data.get('familyMembers', [])
        if family_members and isinstance(family_members, list):
            for i, member in enumerate(family_members, 1):
                # 处理退休人员家庭成员
                if isinstance(member, dict) and member.get('identityType') == 'RETIRED':
                    relation = member.get('relation', '')
                    relation_text = ''
                    
                    if relation == 'SPOUSE':
                        relation_text = '主申请人的配偶'
                    elif relation == 'PARENT':
                        relation_text = '主申请人的父母'
                    elif relation == 'CHILD':
                        relation_text = '主申请人的子女'
                    else:
                        relation_text = f'家庭成员{i}'
                    
                    # 添加退休证复印件要求
                    other_materials.append(f"{relation_text}（{i}）需要提供退休证复印件")
                
                # 处理自由职业或无业人员家庭成员
                if isinstance(member, dict) and (member.get('identityType') == 'FREELANCE' or member.get('identityType') == 'UNEMPLOYED'):
                    relation = member.get('relation', '')
                    relation_text = ''
                    
                    if relation == 'SPOUSE':
                        relation_text = '主申请人的配偶'
                    elif relation == 'PARENT':
                        relation_text = '主申请人的父母'
                    elif relation == 'CHILD':
                        relation_text = '主申请人的子女'
                    else:
                        relation_text = f'家庭成员{i}'
                    
                    # 添加自由职业或无业情况说明要求
                    identity_type = member.get('identityType')
                    identity_text = '自由职业' if identity_type == 'FREELANCE' else '无业'
                    other_materials.append(f"{relation_text}（{i}）需要写{identity_text}情况说明+情况说明相关证明材料")
        
        # 重新编号材料项目
        numbered_materials = []
        for i, item in enumerate(other_materials, 1):
            numbered_materials.append(f"{i}. {item}")
        
        return numbered_materials 