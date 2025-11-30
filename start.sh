#!/bin/bash

# 习惯戒除应用启动脚本

echo "🎯 启动习惯戒除应用..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装/更新依赖
echo "📥 安装依赖..."
pip install -r requirements.txt

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚙️  创建配置文件..."
    cp .env.example .env
    echo "请编辑 .env 文件设置你的配置"
fi

# 启动应用
echo "🚀 启动应用..."
echo "访问地址: http://localhost:5000"
echo "按 Ctrl+C 停止应用"
echo ""

python app.py
