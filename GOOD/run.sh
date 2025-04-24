#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # 无颜色

echo -e "${GREEN}正在启动日本签证材料清单生成器...${NC}"

# 检查Python是否已安装
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未检测到Python，请先安装Python 3.7或更高版本。${NC}"
    exit 1
fi

# 检查是否存在虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}正在创建虚拟环境...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}错误: 创建虚拟环境失败。${NC}"
        exit 1
    fi
fi

# 激活虚拟环境并安装依赖
echo -e "${YELLOW}正在准备环境...${NC}"
source venv/bin/activate
pip install -r requirements.txt

# 启动应用
echo -e "${GREEN}正在启动应用...${NC}"
python app.py

# 如果应用异常退出
if [ $? -ne 0 ]; then
    echo -e "${RED}应用异常退出，退出代码: $?${NC}"
    read -p "按任意键继续..." key
fi

# 退出虚拟环境
deactivate 