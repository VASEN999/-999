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
        
        # 处理所有材料清单部分
        for section_name, materials in document_list.items():
            if not materials:
                continue
            
            # 基本信息部分需要特殊处理，以表格形式展示更美观
            if section_name == '基本信息':
                document_items.append(f'<h2 style="border-bottom: 1px solid #ccc; padding-bottom: 5px; margin-top: 25px;">{section_name}</h2>')
                document_items.append('<table style="width: 100%; border-collapse: collapse; margin: 15px 0 25px 0; box-shadow: 0 2px 3px rgba(0,0,0,0.1);">')
                
                for info_item in materials:
                    if ':' in info_item:
                        label, value = info_item.split(':', 1)
                        document_items.append(f'''<tr>
                            <td style="padding: 12px; border-bottom: 1px solid #eee; width: 30%; font-weight: bold; background-color: #f8f8f8;">{label}:</td>
                            <td style="padding: 12px; border-bottom: 1px solid #eee;">{value.strip()}</td>
                        </tr>''')
                    else:
                        document_items.append(f'''<tr>
                            <td colspan="2" style="padding: 12px; border-bottom: 1px solid #eee;">{info_item}</td>
                        </tr>''')
                
                document_items.append('</table>')
            else:
                document_items.append(f'<h2 style="border-bottom: 1px solid #ccc; padding-bottom: 5px; margin-top: 25px;">{section_name}</h2>')
                document_items.append('<ul style="margin: 15px 0 25px 20px; padding-left: 20px;">')
                for material in materials:
                    document_items.append(f'<li style="margin-bottom: 12px;">{material}</li>')
                document_items.append('</ul>')
        
        # 生成申请人详细信息确认部分
        applicant_details = self._generate_applicant_details(form_data)
        
        # 制作申请人信息部分
        info_items = [
            f'<p><strong>申请人姓名：</strong>{applicant_name}</p>',
            f'<p><strong>签证类型：</strong>{visa_type}</p>',
            f'<p><strong>申请人身份：</strong>{identity_type}</p>',
            f'<p><strong>申请领区：</strong>{consulate}</p>',
            f'<p><strong>生成日期：</strong>{generated_date}</p>'
        ]
        
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
        .info-box {{
            background-color: #f5f5f5;
            border: 1px solid #ddd;
            padding: 15px 20px;
            margin-bottom: 25px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .details-box {{
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            padding: 15px 20px;
            margin: 25px 0;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .info-box p {{
            margin: 8px 0;
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
    </style>
</head>
<body>
    <h1>日本签证申请材料清单</h1>
    
    <div class="info-box">
        {"".join(info_items)}
    </div>
    
    {applicant_details}
    
    {"".join(document_items)}
    
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
        
        details = ['<div class="details-box">']
        details.append('<h2 style="margin-top: 0;">申请人信息确认</h2>')
        details.append('<p>请确认以下申请人信息正确无误。</p>')
        
        # 主申请人信息
        details.append('<div class="details-section">')
        details.append('<h3>主申请人信息</h3>')
        
        # 居住地领区
        residence_consulate = form_data.get('residenceConsulate', '')
        residence_text = self._get_consulate_display(residence_consulate)
        details.append(f'<p class="member-detail"><strong>居住地领区: </strong>{residence_text}</p>')
        
        # 户籍所在地领区
        hukou_consulate = form_data.get('hukouConsulate', '')
        hukou_text = self._get_consulate_display(hukou_consulate)
        details.append(f'<p class="member-detail"><strong>户籍所在地领区: </strong>{hukou_text}</p>')
        
        # 申请人身份
        identity_type = form_data.get('identityType', '')
        identity_text = self._get_identity_type_display(identity_type)
        details.append(f'<p class="member-detail"><strong>申请人身份: </strong>{identity_text}</p>')
        
        # 是否曾经访问日本
        visited_japan = form_data.get('visitedJapan', False)
        visited_text = "是" if visited_japan else "否"
        details.append(f'<p class="member-detail"><strong>是否曾经访问日本: </strong>{visited_text}</p>')
        
        details.append('</div>')
        
        # 家庭成员信息
        family_members = form_data.get('familyMembers', [])
        if family_members:
            details.append('<div class="details-section">')
            details.append('<h3>家庭成员信息</h3>')
            
            for i, member in enumerate(family_members):
                details.append(f'<div class="family-member">')
                details.append(f'<h4>家庭成员 {i+1}</h4>')
                
                # 与主申请人关系
                relation = member.get('relation', '')
                relation_text = self._get_relation_display(relation)
                details.append(f'<p class="member-detail"><strong>与主申请人关系: </strong>{relation_text}</p>')
                
                # 身份类型
                member_identity = member.get('identityType', '')
                member_identity_text = self._get_identity_type_display(member_identity)
                details.append(f'<p class="member-detail"><strong>身份类型: </strong>{member_identity_text}</p>')
                
                # 居住地领区
                member_residence = member.get('residenceConsulate', '')
                member_residence_text = self._get_consulate_display(member_residence)
                details.append(f'<p class="member-detail"><strong>居住地领区: </strong>{member_residence_text}</p>')
                
                # 户籍所在地领区
                member_hukou = member.get('hukouConsulate', '')
                member_hukou_text = self._get_consulate_display(member_hukou)
                details.append(f'<p class="member-detail"><strong>户籍所在地领区: </strong>{member_hukou_text}</p>')
                
                details.append('</div>')
            
            details.append('</div>')
        
        # 申请详情
        details.append('<div class="details-section">')
        details.append('<h3>申请详情</h3>')
        
        # 申请类型
        application_type = form_data.get('applicationType', '')
        application_text = self._get_application_type_display(application_type)
        details.append(f'<p class="member-detail"><strong>申请类型: </strong>{application_text}</p>')
        
        # 办理方式
        process_type = form_data.get('processType', '')
        process_text = self._get_process_type_display(process_type)
        details.append(f'<p class="member-detail"><strong>办理方式: </strong>{process_text}</p>')
        
        # 签证类型
        visa_type = form_data.get('visaType', '')
        visa_text = self._get_visa_type_display(visa_type)
        details.append(f'<p class="member-detail"><strong>签证类型: </strong>{visa_text}</p>')
        
        details.append('</div>')
        
        details.append('</div>')
        return ''.join(details)
        
    def _get_relation_display(self, relation):
        """获取与主申请人关系显示名称"""
        relations = {
            'SPOUSE': '签证持有人的配偶',
            'PARENT': '签证持有人的父母',
            'CHILD': '签证持有人的子女',
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