from flask import Flask, render_template, request, jsonify, make_response
import os
import json
import logging
from collections import OrderedDict
from document_generator import DocumentGenerator
from risk_assessment import RiskAssessmentService

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)