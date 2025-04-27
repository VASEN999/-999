"""
日本签证材料清单生成器 - PDF生成模块
"""
from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader
import tempfile
import os
import datetime
import logging
import platform
import base64
import subprocess
import sys

logger = logging.getLogger(__name__)

class PDFGenerator:
    """PDF生成器类"""
    
    def __init__(self, config):
        """
        初始化PDF生成器
        
        Args:
            config: 配置数据字典
        """
        self.config = config
        # 确保PDF模板目录存在
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'pdf')
        if not os.path.exists(template_dir):
            os.makedirs(template_dir, exist_ok=True)
            logger.info("创建PDF模板目录: %s", template_dir)
        
        # 确保CSS目录存在
        css_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'css')
        if not os.path.exists(css_dir):
            os.makedirs(css_dir, exist_ok=True)
            logger.info("创建CSS目录: %s", css_dir)
        
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.css_path = os.path.join(css_dir, 'pdf_style.css')
        
        # 尝试安装wkhtmltopdf作为备用
        self._try_install_wkhtmltopdf()
        
    def _try_install_wkhtmltopdf(self):
        """尝试安装wkhtmltopdf作为备用PDF生成工具"""
        try:
            # 检查wkhtmltopdf是否已安装
            subprocess.run(['which', 'wkhtmltopdf'], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE)
            logger.debug("wkhtmltopdf已安装")
        except FileNotFoundError:
            logger.warning("wkhtmltopdf未安装，尝试安装...")
            try:
                # 尝试安装wkhtmltopdf
                subprocess.run(['sudo', 'apt-get', 'update'], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE)
                subprocess.run(['sudo', 'apt-get', 'install', '-y', 'wkhtmltopdf'], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE)
                logger.debug("wkhtmltopdf安装成功")
            except Exception as e:
                logger.error("安装wkhtmltopdf失败: %s", str(e))
        
    def generate_pdf(self, document_list, form_data):
        """
        生成PDF签证材料清单
        
        Args:
            document_list: 材料清单字典
            form_data: 用户表单数据
            
        Returns:
            生成的PDF内容
        """
        try:
            # 准备模板数据
            applicant_name = form_data.get('applicantName', '未命名申请人')
            visa_type = self._get_visa_type_display(form_data.get('visaType', ''))
            identity_type = self._get_identity_type_display(form_data.get('identityType', ''))
            consulate = self._get_consulate_display(form_data.get('residenceConsulate', ''))
            generated_date = datetime.datetime.now().strftime('%Y年%m月%d日')
            
            logger.debug("PDF模板数据: 申请人=%s, 签证类型=%s, 身份=%s, 领区=%s", 
                        applicant_name, visa_type, identity_type, consulate)
            
            # 确保familyMembers正确处理
            application_type = form_data.get('applicationType', '')
            if application_type == 'FAMILY':
                family_members = form_data.get('familyMembers', [])
                # 记录家庭成员信息
                logger.debug("家庭申请: 找到家庭成员数量: %s", len(family_members))
                logger.debug("家庭成员数据类型: %s", type(family_members))
                
                # 如果familyMembers是字符串，尝试解析为JSON
                if isinstance(family_members, str):
                    try:
                        import json
                        family_members = json.loads(family_members)
                        form_data['familyMembers'] = family_members
                        logger.debug("已将家庭成员字符串解析为对象: %s", family_members)
                    except Exception as e:
                        logger.error("无法解析家庭成员字符串: %s, 错误: %s", family_members, str(e))
                
                for i, member in enumerate(family_members):
                    logger.debug("家庭成员 %d: %s", i+1, member)
            
            # 显式打印document_list以便调试
            logger.debug("生成PDF的材料清单详情:")
            for section, items in document_list.items():
                logger.debug("部分: %s", section)
                for item in items:
                    logger.debug("  - %s", item)
            
            # 生成多种格式的HTML，尝试不同的方法
            html_content = self._generate_enhanced_html(document_list, applicant_name, visa_type, identity_type, consulate, generated_date, form_data)
            
            # 保存HTML到临时文件用于调试
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w', encoding='utf-8') as f:
                f.write(html_content)
                debug_html_path = f.name
                logger.debug("已保存HTML到临时文件: %s", debug_html_path)
            
            # 尝试多种方法生成PDF
            pdf_content = None
            
            # 方法1: 使用WeasyPrint直接生成
            try:
                logger.debug("尝试使用WeasyPrint直接生成PDF")
                html = HTML(string=html_content)
                pdf_content = html.write_pdf()
                logger.debug("WeasyPrint直接生成PDF成功")
                return pdf_content
            except Exception as e:
                logger.error("WeasyPrint直接生成PDF失败: %s", str(e))
                
                # 方法2: 尝试使用临时文件
                try:
                    logger.debug("尝试使用WeasyPrint从文件生成PDF")
                    pdf_content = HTML(filename=debug_html_path).write_pdf()
                    logger.debug("WeasyPrint从文件生成PDF成功")
                    return pdf_content
                except Exception as e2:
                    logger.error("WeasyPrint从文件生成PDF失败: %s", str(e2))
                    
                    # 方法3: 尝试使用wkhtmltopdf
                    try:
                        logger.debug("尝试使用wkhtmltopdf生成PDF")
                        output_pdf = debug_html_path.replace('.html', '.pdf')
                        subprocess.run(['wkhtmltopdf', debug_html_path, output_pdf], 
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                        
                        with open(output_pdf, 'rb') as f:
                            pdf_content = f.read()
                        logger.debug("wkhtmltopdf生成PDF成功")
                        return pdf_content
                    except Exception as e3:
                        logger.error("wkhtmltopdf生成PDF失败: %s", str(e3))
                        
                        # 所有方法都失败，抛出异常
                        raise Exception("所有PDF生成方法都失败")
                
        except Exception as e:
            logger.error("生成PDF时出错: %s", str(e), exc_info=True)
            raise
    
    def _generate_enhanced_html(self, document_list, applicant_name, visa_type, identity_type, consulate, generated_date, form_data=None):
        """生成增强的HTML版本，确保中文正确显示"""
        document_items = []
        
        # 记录表单数据中的经济材料选项和实际生成的财力证明内容
        logger.debug("PDF生成的经济材料选项: %s", form_data.get('economicMaterial') if form_data else None)
        logger.debug("PDF生成的处理方式: %s", form_data.get('processType') if form_data else None)
        
        # 如果document_list中有财力证明部分，记录它的实际内容
        if '财力证明' in document_list:
            logger.debug("实际PDF财力证明内容:")
            for item in document_list.get('财力证明', []):
                logger.debug("  - %s", item)
        
        # 处理所有材料清单部分，但跳过基本信息部分（已经在申请人信息确认中展示）
        for section_name, materials in document_list.items():
            if not materials or section_name == '基本信息':  # 跳过空部分和基本信息部分
                continue
            
            # 创建材料清单部分
            document_items.append(f'<div class="material-section">')
            document_items.append(f'<h2 style="border-bottom: 1px solid #ccc; padding-bottom: 5px; margin-top: 25px;">{section_name}</h2>')
            document_items.append('<ul style="margin: 15px 0 25px 20px; padding-left: 20px;">')
            
            # 使用document_list中的实际材料列表，确保与页面显示一致
            for material in materials:
                document_items.append(f'<li style="margin-bottom: 12px;">{material}</li>')
                
            document_items.append('</ul>')
            document_items.append('</div>')
        
        # 生成申请人详细信息确认部分
        applicant_details = self._generate_applicant_details(form_data)
        
        # 获取订单号，如果不存在则显示下划线供手写
        order_number = ""
        if form_data and form_data.get('orderNumber'):
            order_number = form_data.get('orderNumber')
        else:
            # 显示下划线，供打印后手写填写
            order_number = '<span style="display: inline-block; min-width: 200px; border-bottom: 1px solid #000;">&nbsp;</span>'
        
        # 检查是否加急
        is_urgent = False
        if form_data and form_data.get('isUrgent'):
            is_urgent_value = form_data.get('isUrgent')
            if isinstance(is_urgent_value, bool):
                is_urgent = is_urgent_value
            elif isinstance(is_urgent_value, str):
                is_urgent = is_urgent_value.lower() == 'true'
        
        # 现在制作顶部信息部分（不再单独显示基本信息部分）
        # 订单号单独一行，其他信息左右分布
        header_items = [
            f'<div class="order-number" style="flex: 1 0 100%; width: 100%; text-align: center; margin-bottom: 10px;"><strong>订单号：</strong>{order_number}</div>',
            f'<div class="header-item"><strong>签证类型：</strong>{visa_type}</div>',
            f'<div class="header-item"><strong>申请人身份：</strong>{identity_type}</div>',
            f'<div class="header-item"><strong>申请领区：</strong>{consulate}</div>',
            f'<div class="header-item"><strong>生成日期：</strong>{generated_date}</div>'
        ]
        
        # 创建加急印章样式
        urgent_stamp = """
        <div class="urgent-stamp" style="
            position: absolute;
            top: 10px;
            right: 30px;
            width: 100px;
            height: 100px;
            border: 3px solid #f44336;
            border-radius: 50%;
            transform: rotate(20deg);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #f44336;
            font-size: 28px;
            font-weight: bold;
            opacity: 0.85;
            text-align: center;
            line-height: 1;
            box-shadow: 0 0 5px rgba(0,0,0,0.2);
            z-index: 100;
        ">
        加急<br>处理
        </div>
        """ if is_urgent else ""
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <title>日本签证申请材料清单</title>
    <style>
        /* 定义多种字体，优先使用中文字体 */
        @font-face {{
            font-family: 'CustomFont';
            src: local('WenQuanYi Micro Hei'),
                 local('WenQuanYi Zen Hei'),
                 local('Noto Sans CJK SC'),
                 local('Microsoft YaHei'),
                 local('SimSun'),
                 local('SimHei'),
                 local('AR PL UMing CN'),
                 local('AR PL UKai CN');
        }}
        @page {{
            size: A4;
            margin: 2cm 1.5cm;
        }}
        html, body {{
            font-family: 'CustomFont', sans-serif;
            font-size: 16px;
            margin: 0;
            padding: 0;
        }}
        body {{
            padding: 20px;
            line-height: 1.6;
            color: #333;
            background-color: white;
        }}
        * {{
            font-family: 'CustomFont', sans-serif !important;
        }}
        h1 {{
            text-align: center;
            font-size: 26px;
            margin-bottom: 25px;
            color: #333;
            padding-bottom: 10px;
            border-bottom: 2px solid #666;
        }}
        h2 {{
            font-size: 20px;
            color: #333;
            margin-top: 25px;
            padding-bottom: 5px;
        }}
        h3 {{
            font-size: 18px;
            color: #444;
            margin-top: 15px;
            margin-bottom: 10px;
            padding-bottom: 3px;
            border-bottom: 1px solid #eee;
        }}
        p, li {{
            font-size: 16px;
            line-height: 1.6;
            margin-bottom: 10px;
        }}
        strong {{
            font-weight: bold;
        }}
        /* 顶部信息区域 */
        .document-header {{
            display: flex;
            flex-wrap: wrap;
            background-color: #f5f5f5;
            border: 1px solid #ddd;
            padding: 15px 20px;
            margin-bottom: 25px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .header-item {{
            flex: 1 0 50%;
            margin: 5px 0;
            min-width: 250px;
        }}
        /* 申请详情区域 */
        .details-box {{
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            padding: 15px 20px;
            margin: 25px 0;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        /* 材料清单区域 */
        .materials-container {{
            display: flex;
            flex-wrap: wrap;
        }}
        .material-section {{
            flex: 1 0 100%;
            padding-right: 15px;
        }}
        @media print {{
            .material-section {{
                flex: 0 0 100%;
                break-inside: avoid;
            }}
        }}
        .footer {{
            margin-top: 40px;
            text-align: center;
            font-size: 14px;
            color: #666;
            border-top: 1px solid #ccc;
            padding-top: 15px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        td {{
            padding: 8px 12px;
            vertical-align: top;
            border-bottom: 1px solid #eee;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        ul {{
            padding-left: 20px;
            margin: 15px 0;
        }}
        li {{
            margin-bottom: 10px;
            padding-left: 5px;
        }}
        .details-section {{
            margin-bottom: 20px;
        }}
        .family-member {{
            margin: 15px 0;
            padding: 10px;
            border: 1px solid #eee;
            border-radius: 4px;
            background-color: #fafafa;
        }}
        .family-member h4 {{
            margin: 0 0 10px 0;
            color: #555;
            font-size: 16px;
        }}
        .member-detail {{
            margin: 5px 0;
        }}
        /* 两栏布局 */
        .two-column {{
            display: flex;
            flex-wrap: wrap;
        }}
        .column {{
            flex: 1 0 50%;
            min-width: 300px;
            padding: 0 10px;
        }}
        /* 强调颜色 */
        .highlight {{
            color: #2C73D2;
        }}
        .text-warning {{
            color: #FFA500;
        }}
        /* 订单号样式 */
        .order-number {{
            font-size: 18px;
            padding: 5px 0;
            margin-bottom: 10px;
            border-bottom: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <h1 style="position: relative;">日本签证申请材料清单{urgent_stamp}</h1>
    
    <div class="document-header">
        {"".join(header_items)}
    </div>
    
    {applicant_details}
    
    <div class="materials-container">
        {"".join(document_items)}
    </div>
    
    <div class="footer">
        <p>本材料清单由GOOD系统自动生成，仅供参考。最终所需材料请以日本驻华使领馆官方要求为准。</p>
        <p>Generated by GOOD System on {generated_date}</p>
    </div>
</body>
</html>"""
        
        return html
        
    def _generate_applicant_details(self, form_data):
        """生成申请人详细信息部分"""
        if not form_data:
            return ""
        
        # 记录接收到的form_data类型和内容
        logger.debug("_generate_applicant_details接收到的form_data类型: %s", type(form_data))
        logger.debug("访问日本状态: %s, 类型: %s", form_data.get('previousVisit'), type(form_data.get('previousVisit')))
        
        # 处理previousVisit的布尔值转换
        def convert_to_bool(value):
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() == 'true'
            return False
        
        # 获取并转换主申请人的访问状态
        visited_japan = convert_to_bool(form_data.get('previousVisit', False))
        
        details = ['<div class="details-box">']
        details.append('<h2 style="margin-top: 0;">申请人信息确认</h2>')
        details.append('<p>请确认以下申请人信息正确无误。</p>')
        
        # 获取申请类型
        application_type = form_data.get('applicationType', '')
        family_members = form_data.get('familyMembers', [])
        
        # 如果familyMembers是字符串，尝试解析
        if isinstance(family_members, str):
            try:
                import json
                family_members = json.loads(family_members)
                logger.debug("已将字符串解析为家庭成员对象: %s", family_members)
            except Exception as e:
                logger.error("无法解析家庭成员字符串: %s, 错误: %s", family_members, str(e))
        
        # 如果是家庭申请且有家庭成员，使用表格布局
        if application_type == 'FAMILY' and family_members and len(family_members) > 0:
            logger.debug("家庭申请布局: 找到 %d 个家庭成员", len(family_members))
            
            # 创建表格布局
            details.append('<table class="family-table" style="width:100%; border-collapse: collapse; margin-top:20px;">')
            
            # 表头
            details.append('<tr>')
            details.append('<th style="border:1px solid #ddd; padding:10px; text-align:left; background-color:#f5f5f5;"></th>')
            details.append('<th style="border:1px solid #ddd; padding:10px; text-align:center; background-color:#f5f5f5;">主申请人</th>')
            
            for i in range(len(family_members)):
                details.append(f'<th style="border:1px solid #ddd; padding:10px; text-align:center; background-color:#f5f5f5;">家庭成员{i+1}</th>')
            
            details.append('</tr>')
            
            # 与主申请人关系行
            details.append('<tr>')
            details.append('<td style="border:1px solid #ddd; padding:10px; font-weight:bold; background-color:#f9f9f9;">与主申请人关系</td>')
            details.append('<td style="border:1px solid #ddd; padding:10px; text-align:center;">本人</td>')
            
            for member in family_members:
                relation = member.get('relation', '')
                relation_text = self._get_relation_display(relation)
                details.append(f'<td style="border:1px solid #ddd; padding:10px; text-align:center;">{relation_text}</td>')
            
            details.append('</tr>')
            
            # 居住地领区行
            details.append('<tr>')
            details.append('<td style="border:1px solid #ddd; padding:10px; font-weight:bold; background-color:#f9f9f9;">居住地领区</td>')
            
            residence_consulate = form_data.get('residenceConsulate', '')
            residence_text = self._get_consulate_display(residence_consulate)
            details.append(f'<td style="border:1px solid #ddd; padding:10px; text-align:center;">{residence_text}</td>')
            
            for member in family_members:
                member_residence = member.get('residenceConsulate', '')
                member_residence_text = self._get_consulate_display(member_residence)
                details.append(f'<td style="border:1px solid #ddd; padding:10px; text-align:center;">{member_residence_text}</td>')
            
            details.append('</tr>')
            
            # 户籍所在地领区行
            details.append('<tr>')
            details.append('<td style="border:1px solid #ddd; padding:10px; font-weight:bold; background-color:#f9f9f9;">户籍所在地领区</td>')
            
            hukou_consulate = form_data.get('hukouConsulate', '')
            hukou_text = self._get_consulate_display(hukou_consulate)
            details.append(f'<td style="border:1px solid #ddd; padding:10px; text-align:center;">{hukou_text}</td>')
            
            for member in family_members:
                member_hukou = member.get('hukouConsulate', '')
                member_hukou_text = self._get_consulate_display(member_hukou)
                details.append(f'<td style="border:1px solid #ddd; padding:10px; text-align:center;">{member_hukou_text}</td>')
            
            details.append('</tr>')
            
            # 申请人身份行
            details.append('<tr>')
            details.append('<td style="border:1px solid #ddd; padding:10px; font-weight:bold; background-color:#f9f9f9;">申请人身份</td>')
            
            identity_type = form_data.get('identityType', '')
            identity_text = self._get_identity_type_display(identity_type)
            details.append(f'<td style="border:1px solid #ddd; padding:10px; text-align:center;">{identity_text}</td>')
            
            for member in family_members:
                member_identity = member.get('identityType', '')
                member_identity_text = self._get_identity_type_display(member_identity)
                details.append(f'<td style="border:1px solid #ddd; padding:10px; text-align:center;">{member_identity_text}</td>')
            
            details.append('</tr>')
            
            # 是否曾经访问日本行
            details.append('<tr>')
            details.append('<td style="border:1px solid #ddd; padding:10px; font-weight:bold; background-color:#f9f9f9;">是否曾经访问日本</td>')
            
            # 主申请人的访问状态
            visited_text = "是" if visited_japan else "否"
            details.append(f'<td style="border:1px solid #ddd; padding:10px; text-align:center;">{visited_text}</td>')
            
            # 家庭成员的访问状态留空，添加下划线
            for _ in family_members:
                details.append('<td style="border:1px solid #ddd; padding:10px; text-align:center;">')
                details.append('<div style="display:inline-block; min-width:30px; border-bottom:1px solid #000;">&nbsp;</div>')
                details.append('</td>')
            
            details.append('</tr>')
            
            details.append('</table>')
            
            # 添加申请详情部分，使用美观的左右布局
            details.append('<div class="details-section" style="margin-top:25px; background-color:#f8f8f8; border-radius:8px; padding:15px;">')
            details.append('<h3 style="margin-top:0; border-bottom:1px solid #e0e0e0; padding-bottom:8px; margin-bottom:15px;">申请详情</h3>')
            
            # 计算申请人数
            applicant_count = 1 + len(family_members)
            
            # 使用表格布局确保左右对齐美观
            details.append('<table style="width:100%; border-collapse:collapse;">')
            details.append('<tr>')
            
            # 左侧栏
            details.append('<td style="width:50%; padding-right:15px; vertical-align:top;">')
            
            # 申请类型
            application_text = self._get_application_type_display(application_type)
            details.append(f'<p class="member-detail" style="margin:8px 0;"><strong style="display:inline-block; width:80px;">申请类型: </strong>{application_text}</p>')
            
            # 申请人数
            details.append(f'<p class="member-detail" style="margin:8px 0;"><strong style="display:inline-block; width:80px;">申请人数: </strong><span style="color:#2C73D2; font-weight:500;">{applicant_count}人</span></p>')
            
            details.append('</td>')  # 结束左侧栏
            
            # 右侧栏
            details.append('<td style="width:50%; padding-left:15px; vertical-align:top; border-left:1px dashed #ddd;">')
            
            # 办理方式
            process_type = form_data.get('processType', '')
            process_text = self._get_process_type_display(process_type)
            details.append(f'<p class="member-detail" style="margin:8px 0;"><strong style="display:inline-block; width:80px;">办理方式: </strong>{process_text}</p>')
            
            # 签证类型
            visa_type = form_data.get('visaType', '')
            visa_text = self._get_visa_type_display(visa_type)
            details.append(f'<p class="member-detail" style="margin:8px 0;"><strong style="display:inline-block; width:80px;">签证类型: </strong><span style="color:#2C73D2; font-weight:500;">{visa_text}</span></p>')
            
            details.append('</td>')  # 结束右侧栏
            details.append('</tr>')  # 结束行
            details.append('</table>')  # 结束表格
            details.append('</div>')  # 结束申请详情section
            
        else:
            # 使用两栏布局 (非家庭申请或无家庭成员时)
            details.append('<div class="two-column">')
            
            # 左侧栏 - 主申请人信息
            details.append('<div class="column">')
            details.append('<div class="details-section">')
            details.append('<h3>主申请人信息</h3>')
            
            # 居住地领区
            residence_consulate = form_data.get('residenceConsulate', '')
            residence_text = self._get_consulate_display(residence_consulate)
            details.append(f'<p class="member-detail"><strong>居住地领区: </strong><span class="highlight">{residence_text}</span></p>')
            
            # 户籍所在地领区
            hukou_consulate = form_data.get('hukouConsulate', '')
            hukou_text = self._get_consulate_display(hukou_consulate)
            details.append(f'<p class="member-detail"><strong>户籍所在地领区: </strong>{hukou_text}</p>')
            
            # 申请人身份
            identity_type = form_data.get('identityType', '')
            identity_text = self._get_identity_type_display(identity_type)
            details.append(f'<p class="member-detail"><strong>申请人身份: </strong>{identity_text}</p>')
            
            # 是否曾经访问日本
            visited_text = "是" if visited_japan else "否"
            details.append(f'<p class="member-detail"><strong>是否曾经访问日本: </strong>{visited_text}</p>')
            
            details.append('</div>')  # 结束主申请人信息section
            
            # 右侧栏 - 申请详情
            details.append('</div><div class="column">')  # 结束左侧栏，开始右侧栏
            
            # 申请详情部分，美化样式
            details.append('<div class="details-section" style="background-color:#f8f8f8; border-radius:8px; padding:15px;">')
            details.append('<h3 style="margin-top:0; border-bottom:1px solid #e0e0e0; padding-bottom:8px; margin-bottom:15px;">申请详情</h3>')
            
            # 使用表格布局确保左右对齐美观
            details.append('<table style="width:100%; border-collapse:collapse;">')
            details.append('<tr>')
            
            # 左侧栏
            details.append('<td style="width:50%; padding-right:15px; vertical-align:top;">')
            
            # 申请类型
            application_text = self._get_application_type_display(application_type)
            details.append(f'<p class="member-detail" style="margin:8px 0;"><strong style="display:inline-block; width:80px;">申请类型: </strong>{application_text}</p>')
            
            # 申请人数
            details.append(f'<p class="member-detail" style="margin:8px 0;"><strong style="display:inline-block; width:80px;">申请人数: </strong><span style="color:#2C73D2; font-weight:500;">1人</span></p>')
            
            details.append('</td>')  # 结束左侧栏
            
            # 右侧栏
            details.append('<td style="width:50%; padding-left:15px; vertical-align:top; border-left:1px dashed #ddd;">')
            
            # 办理方式
            process_type = form_data.get('processType', '')
            process_text = self._get_process_type_display(process_type)
            details.append(f'<p class="member-detail" style="margin:8px 0;"><strong style="display:inline-block; width:80px;">办理方式: </strong>{process_text}</p>')
            
            # 签证类型
            visa_type = form_data.get('visaType', '')
            visa_text = self._get_visa_type_display(visa_type)
            details.append(f'<p class="member-detail" style="margin:8px 0;"><strong style="display:inline-block; width:80px;">签证类型: </strong><span style="color:#2C73D2; font-weight:500;">{visa_text}</span></p>')
            
            details.append('</td>')  # 结束右侧栏
            details.append('</tr>')  # 结束行
            details.append('</table>')  # 结束表格
            
            details.append('</div>')  # 结束申请详情section
            details.append('</div>')  # 结束右侧栏
            details.append('</div>')  # 结束两栏布局
            
            # 家庭申请但无家庭成员的情况
            if application_type == 'FAMILY':
                details.append('<div class="details-section" style="clear: both; padding-top: 15px;">')
                details.append('<h3>家庭成员信息</h3>')
                details.append('<p class="text-warning"><i class="bi bi-exclamation-triangle-fill me-1"></i> 您选择了家庭申请，但未添加任何家庭成员。请确认是否需要添加家庭成员信息。</p>')
                details.append('</div>')  # 结束家庭成员section
        
        details.append('</div>')  # 结束details-box
        return ''.join(details)
        
    def _get_relation_display(self, relation):
        """获取与主申请人关系显示名称"""
        relations = {
            'SPOUSE': '主申请人的配偶',
            'PARENT': '主申请人的父母',
            'CHILD': '主申请人的子女',
            'OTHER': '其他亲属'
        }
        return relations.get(relation, relation)
        
    def _get_application_type_display(self, application_type):
        """获取申请类型显示名称"""
        application_types = {
            'INDIVIDUAL': '个人申请',
            'FAMILY': '家庭申请',
            'BINDING': '绑签申请',
            'ECONOMIC': '经济材料申请'
        }
        return application_types.get(application_type, application_type)
        
    def _get_process_type_display(self, process_type):
        """获取办理方式显示名称"""
        process_types = {
            'NORMAL': '常规办理',
            'SIMPLIFIED': '简化办理',
            'STUDENT': '留学生办理',
            'TAX': '税单办理'
        }
        return process_types.get(process_type, process_type)
    
    def _get_visa_type_display(self, visa_type):
        """获取签证类型显示名称"""
        visa_types = {
            'SINGLE': '单次签证',
            'THREE': '三年多次签证',
            'FIVE': '五年多次签证'
        }
        return visa_types.get(visa_type, '单次签证')
        
    def _get_identity_type_display(self, identity_type):
        """获取身份类型显示名称"""
        identity_types = {
            'EMPLOYED': '在职人员',
            'FREELANCER': '自由职业者',
            'STUDENT': '学生',
            'RETIRED': '退休人员'
        }
        return identity_types.get(identity_type, '一般申请人')
        
    def _get_consulate_display(self, consulate):
        """获取领区显示名称"""
        consulates = {
            'beijing': '北京',
            'shanghai': '上海',
            'guangzhou': '广州',
            'shenyang': '沈阳',
            'chongqing': '重庆'
        }
        return consulates.get(consulate.lower(), consulate) 