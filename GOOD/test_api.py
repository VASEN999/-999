"""
测试API请求
"""
import requests
import json
import sys
import time

def test_family_application():
    """测试家庭申请的API请求"""
    
    # 生成唯一的请求ID，方便在日志中追踪
    request_id = int(time.time())
    
    # 准备请求数据
    form_data = {
        'requestId': f'test-{request_id}',  # 添加请求ID
        'residenceConsulate': 'beijing',
        'hukouConsulate': 'shanghai',
        'applicationType': 'FAMILY',
        'visaType': 'THREE',  # 三年多次签证
        'processType': 'NORMAL',
        'identityType': 'EMPLOYED',  # 主申请人是在职人员
        'familyMembers': [
            {
                'name': '家庭成员1',
                'residenceConsulate': 'beijing',
                'hukouConsulate': 'beijing',  # 不需要居住证明
                'identityType': 'RETIRED'
            },
            {
                'name': '家庭成员2',
                'residenceConsulate': 'beijing',
                'hukouConsulate': 'shanghai',  # 需要居住证明
                'identityType': 'STUDENT'
            }
        ]
    }
    
    # 发送请求
    try:
        print(f"发送请求 ID: {request_id}")
        print("请求数据:")
        print(json.dumps(form_data, ensure_ascii=False, indent=2))
        print("-" * 60)
        
        response = requests.post('http://localhost:5000/api/generate', json=form_data)
        response.raise_for_status()
        
        # 获取结果
        result = response.json()
        
        # 打印结果
        print("API 响应:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 检查居住证明材料
        if '居住证明材料' in result:
            print("\n居住证明材料部分:")
            for item in result['居住证明材料']:
                print(f"  - {item}")
        else:
            print("\n没有找到居住证明材料部分")
        
        # 检查的居住证明材料是否包含预期的内容
        if '居住证明材料' in result:
            first_line = result['居住证明材料'][0] if result['居住证明材料'] else ""
            if "主申请人, 家庭成员2" in first_line:
                print("\n测试结果: ✅ 成功 - 居住证明材料正确显示需要证明的家庭成员")
            else:
                print(f"\n测试结果: ❌ 失败 - 居住证明材料没有正确显示需要证明的家庭成员: '{first_line}'")
        
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    test_family_application() 