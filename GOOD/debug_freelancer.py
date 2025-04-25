import logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

from document_generator import DocumentGenerator
import json

# 模拟日志中的请求数据
form_data = {
    "residenceConsulate": "shanghai",
    "hukouConsulate": "shanghai",
    "applicationType": "FAMILY",
    "identityType": "EMPLOYED",
    "visaType": "THREE",  # 确保与日志相同
    "processType": "NORMAL",
    "economicMaterial": "salary_three",  # 添加经济材料类型
    "familyMembers": [
        {
            "identityType": "FREELANCE",
            "name": "家庭成员1",
            "residenceConsulate": "shanghai", 
            "hukouConsulate": "shanghai"
        }
    ]
}

# 打印请求数据以调试
print("==== 请求数据 ====")
print(json.dumps(form_data, indent=2, ensure_ascii=False))

# 创建文档生成器
dg = DocumentGenerator({})

# 生成材料清单
result = dg.generate_document_list(form_data)

# 打印生成的材料清单
print("\n==== 生成的材料清单 ====")
print(json.dumps(result, indent=2, ensure_ascii=False))

# 检查自由职业者标识是否被正确设置
print("\n==== 自由职业者检查 ====")
print(f"主申请人是自由职业: {form_data.get('identityType') == 'FREELANCER'}")

has_freelancer = False
for member in form_data.get("familyMembers", []):
    if isinstance(member, dict) and member.get("identityType") == "FREELANCER":
        has_freelancer = True
        print(f"发现自由职业家庭成员(FREELANCER): {member.get('name')}")
        
# 检查FREELANCE标识
has_freelance = False
for member in form_data.get("familyMembers", []):
    if isinstance(member, dict) and member.get("identityType") == "FREELANCE":
        has_freelance = True
        print(f"发现自由职业家庭成员(FREELANCE): {member.get('name')}")
        
print(f"家庭中有自由职业者(FREELANCER): {has_freelancer}")
print(f"家庭中有自由职业者(FREELANCE): {has_freelance}")
print(f"其他材料中包含自由职业相关要求: {any('自由职业' in item for item in result.get('其他材料', []))}")

# 直接检查other_materials.py中的检测逻辑
print("\n==== 直接检查逻辑 ====")

# 模拟other_materials.py中的检测逻辑
has_freelancer_direct = False
# 检查主申请人是否为自由职业者
identity_type = form_data.get('identityType', '')
if identity_type == 'FREELANCER':
    has_freelancer_direct = True
    print("主申请人是自由职业者")

# 检查家属申请中是否有自由职业者
application_type = form_data.get('applicationType', '')
if application_type == 'FAMILY':
    family_members = form_data.get('familyMembers', [])
    for member in family_members:
        if isinstance(member, dict) and member.get('identityType') == 'FREELANCER':
            has_freelancer_direct = True
            print(f"家庭成员中有自由职业者(FREELANCER): {member.get('name', '未命名')}")
        if isinstance(member, dict) and member.get('identityType') == 'FREELANCE':
            print(f"家庭成员中有自由职业者(FREELANCE): {member.get('name', '未命名')}")

print(f"直接检查结果 - 有自由职业者(FREELANCER): {has_freelancer_direct}")

# 添加额外日志，检查处理过程
print("\n==== 检查处理过程 ====")
from document_generator.other_materials import OtherMaterialsGenerator
other_generator = OtherMaterialsGenerator({})
other_materials = other_generator.get_materials(form_data)
print(f"other_materials直接调用结果: {other_materials}") 