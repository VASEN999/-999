import re
import json
import sys

def read_log_file(filename):
    """读取并显示日志文件内容"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"读取文件出错: {e}")
        return None

def find_family_application_logs(content):
    """查找家庭申请的相关日志"""
    # 匹配家庭申请的日志行
    family_pattern = r'applicationType": "FAMILY"'
    family_logs = re.findall(r'(.{0,200}' + family_pattern + r'.{0,1000})', content)
    
    # 查找familyMembers的日志
    member_pattern = r'家庭成员数量: (\d+)'
    member_logs = re.findall(r'(.{0,50}' + member_pattern + r'.{0,500})', content)
    
    # 查找材料清单的日志
    materials_pattern = r'生成的材料清单: OrderedDict\(\{(.+?)\}\)'
    materials_logs = re.findall(materials_pattern, content, re.DOTALL)
    
    # 查找自由职业相关的日志
    freelancer_pattern = r'自由职业'
    freelancer_logs = re.findall(r'(.{0,100}' + freelancer_pattern + r'.{0,100})', content)
    
    return {
        'family_applications': family_logs,
        'member_counts': member_logs,
        'materials': materials_logs,
        'freelancer_mentions': freelancer_logs
    }

if __name__ == "__main__":
    log_file = "app_log.txt"
    if len(sys.argv) > 1:
        log_file = sys.argv[1]
    
    print(f"解析日志文件: {log_file}")
    content = read_log_file(log_file)
    
    if content:
        print(f"日志文件大小: {len(content)} 字节")
        logs = find_family_application_logs(content)
        
        print(f"\n找到 {len(logs['family_applications'])} 个家庭申请日志")
        for i, log in enumerate(logs['family_applications'], 1):
            print(f"{i}. {log.strip()}")
        
        print(f"\n找到 {len(logs['member_counts'])} 个家庭成员数量日志")
        for i, log in enumerate(logs['member_counts'], 1):
            print(f"{i}. {log.strip()}")
        
        print(f"\n找到 {len(logs['freelancer_mentions'])} 个自由职业相关日志")
        for i, log in enumerate(logs['freelancer_mentions'], 1):
            print(f"{i}. {log.strip()}")
        
        print(f"\n找到 {len(logs['materials'])} 个材料清单日志")
        for i, log in enumerate(logs['materials'][:3], 1):  # 只显示前3个，可能很长
            print(f"{i}. {log[:200]}... (截断)")
    else:
        print("无法读取日志文件") 