from flask import Flask, render_template, request, jsonify, make_response
import os
import json
import logging
import datetime
from collections import OrderedDict
from document_generator import DocumentGenerator
from risk_assessment import RiskAssessmentService
from document_generator.pdf_generator import PDFGenerator
import urllib.parse

app = Flask(__name__)

# 生产环境配置
app.config['ENV'] = 'production'
app.config['DEBUG'] = False

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app_log.txt')
    ]
)
logger = app.logger

# 加载配置文件
def load_config():
    """加载材料配置文件"""
    config_path = os.path.join(app.static_folder, 'js', 'document_config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("配置文件未找到: %s", config_path)
        return {}
    except json.JSONDecodeError:
        logger.error("配置文件格式错误")
        return {}

# 全局配置对象和服务
document_config = load_config()
document_generator = DocumentGenerator(document_config)
risk_service = RiskAssessmentService(document_config)
pdf_generator = PDFGenerator(document_config)  # 初始化PDF生成器

# 定义材料显示顺序
section_order = ['基本信息', '基本材料', '学籍/学历证明', '学籍/学历证明及情况说明', '工作证明', '财力证明', '居住证明材料', '家属材料', '其他材料']

@app.route('/')
def index():
    """渲染主页"""
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate_documents():
    """处理签证材料清单生成请求"""
    
    try:
        form_data = request.json
        if not form_data:
            logger.warning("没有提交表单数据")
            return jsonify({
                "error": "没有提交表单数据"
            }), 400
            
        # 检查居住地领区，如果选择了"其他领区"，返回错误
        residence_consulate = form_data.get('residenceConsulate', '')
        if residence_consulate == 'other':
            logger.warning("用户选择了其他领区")
            return jsonify({
                "error": "目前暂不支持在其他领区申请日本签证，请选择北京或上海领区。"
            }), 400
            
        # 记录请求数据，用于调试
        logger.info("收到材料清单生成请求: %s", json.dumps({
            'residence': form_data.get('residenceConsulate'),
            'hukou': form_data.get('hukouConsulate'),
            'applicationType': form_data.get('applicationType'),
            'visaType': form_data.get('visaType'),
            'processType': form_data.get('processType')
        }, ensure_ascii=False))
        
        # 如果是家庭申请，记录家庭成员信息
        if form_data.get('applicationType') == 'FAMILY':
            family_members = form_data.get('familyMembers', [])
            logger.info(f"家庭申请，家庭成员数量: {len(family_members)}")
            for i, member in enumerate(family_members):
                if isinstance(member, dict):
                    logger.info(f"家庭成员{i+1}: 居住地={member.get('residenceConsulate')}, 户籍地={member.get('hukouConsulate')}")
            
        # 生成材料清单
        document_list = document_generator.generate_document_list(form_data)
        
        # 记录生成的居住证明材料部分，便于调试
        if '居住证明材料' in document_list:
            logger.info("生成的居住证明材料:")
            for item in document_list['居住证明材料']:
                logger.info(f"  {item}")
        
        return jsonify(document_list)
        
    except Exception as e:
        app.logger.error("生成材料清单时出错: %s", str(e), exc_info=True)
        return jsonify({
            "error": f"生成材料清单时出错: {str(e)}"
        }), 500

@app.route('/risk_assessment_guide', methods=['GET'])
def risk_assessment_guide():
    """获取风险评估指南"""
    try:
        guide = risk_service.get_risk_assessment_guide()
        return jsonify(guide)
    except Exception as e:
        logger.exception("获取风险评估指南时发生错误: %s", str(e))
        return jsonify({
            'status': 'error',
            'error': f'服务器错误: {str(e)}'
        }), 500

@app.route('/api/generate_pdf', methods=['POST'])
def generate_pdf():
    """生成PDF材料清单"""
    try:
        form_data = request.json if request.is_json else request.form.to_dict()
        logger.debug("收到PDF生成请求，原始表单数据: %s", str(form_data))
        
        if not form_data:
            logger.warning("没有提交表单数据")
            return jsonify({
                "error": "没有提交表单数据"
            }), 400
        
        # 处理从表单传来的JSON字符串数据
        for key in form_data:
            if isinstance(form_data[key], str):
                try:
                    # 尝试解析可能的JSON字符串
                    if form_data[key].startswith('[') or form_data[key].startswith('{'):
                        form_data[key] = json.loads(form_data[key])
                except json.JSONDecodeError:
                    # 如果不是有效的JSON，保持原样
                    pass
        
        # 特殊处理家庭成员信息
        if form_data.get('applicationType') == 'FAMILY':
            family_members = form_data.get('familyMembers', [])
            logger.debug(f"处理家庭申请: 家庭成员数据类型 {type(family_members)}")
            
            # 如果家庭成员是字符串，尝试解析
            if isinstance(family_members, str):
                try:
                    family_members = json.loads(family_members)
                    form_data['familyMembers'] = family_members
                    logger.debug(f"成功解析家庭成员字符串: {family_members}")
                except json.JSONDecodeError:
                    logger.error(f"无法解析家庭成员字符串: {family_members}")
            
            # 记录家庭成员数量和信息
            logger.debug(f"家庭成员数量: {len(family_members)}")
            for i, member in enumerate(family_members):
                logger.debug(f"家庭成员 {i+1}: {member}")
        
        # 检查并处理economicMaterial参数
        economic_material = form_data.get('economicMaterial')
        if economic_material:
            logger.debug(f"检测到经济材料选项: {economic_material}")
        
        logger.debug("处理后的表单数据: %s", str(form_data))
            
        # 检查居住地领区
        residence_consulate = form_data.get('residenceConsulate', '')
        if residence_consulate == 'other':
            logger.warning("用户选择了其他领区")
            return jsonify({
                "error": "目前暂不支持在其他领区申请日本签证，请选择北京或上海领区。"
            }), 400
        
        # 检查必要的经济材料字段
        process_type = form_data.get('processType', '')
        application_type = form_data.get('applicationType', '')
        if process_type == 'NORMAL' and application_type not in ['BINDING', 'ECONOMIC'] and not form_data.get('economicMaterial'):
            logger.warning("PDF请求缺少经济材料类型字段")
            return jsonify({
                "error": "使用普通经济材料办理时，请选择一种经济材料类型"
            }), 400
        
        try:
            # 生成材料清单
            document_list = document_generator.generate_document_list(form_data)
            
            # 记录生成的材料清单，便于调试
            logger.debug("为PDF生成的材料清单: %s", document_list)
            # 详细记录生成的材料清单内容
            logger.debug("详细材料清单内容:")
            for section_name, materials in document_list.items():
                logger.debug("部分: %s", section_name)
                for item in materials:
                    logger.debug("  - %s", item)
        except Exception as e:
            logger.error("生成材料清单时出错: %s", str(e), exc_info=True)
            return jsonify({
                "error": f"生成材料清单时出错: {str(e)}"
            }), 500
        
        try:
            # 生成PDF
            pdf_content = pdf_generator.generate_pdf(document_list, form_data)
            
            # 生成文件名
            current_date = datetime.datetime.now().strftime('%Y%m%d')
            
            # 修复文件名编码问题 - 使用URL编码处理中文字符
            filename = f"visa_document_list_{current_date}.pdf"
            encoded_filename = urllib.parse.quote(f"日本签证材料清单_{current_date}.pdf")
            
            # 返回PDF文件
            response = make_response(pdf_content)
            response.headers['Content-Type'] = 'application/pdf'
            # 使用不同的Content-Disposition格式支持多种浏览器
            response.headers['Content-Disposition'] = f'inline; filename="{filename}"; filename*=UTF-8\'\'{encoded_filename}'
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            logger.debug("PDF生成成功，文件名: %s", filename)
            return response
        except Exception as e:
            logger.error("生成PDF文件时出错: %s", str(e), exc_info=True)
            return jsonify({
                "error": f"生成PDF文件时出错: {str(e)}"
            }), 500
        
    except Exception as e:
        app.logger.error("PDF生成过程中发生未知错误: %s", str(e), exc_info=True)
        return jsonify({
            "error": f"PDF生成过程中发生未知错误: {str(e)}"
        }), 500