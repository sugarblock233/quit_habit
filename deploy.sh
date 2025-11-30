#!/bin/bash

# 生产环境部署脚本

echo "🚀 开始部署习惯戒除应用..."

# 1. 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 2. 激活虚拟环境并安装依赖
echo "📥 安装依赖..."
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn  # 生产环境服务器

# 3. 配置环境变量
if [ ! -f ".env" ]; then
    echo "⚙️  创建配置文件..."
    cp .env.example .env
    echo "警告: 请编辑 .env 文件并设置 SECRET_KEY"
fi

# 4. 初始化数据库
echo "🗄️  初始化数据库..."
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# 5. 安装 systemd 服务
echo "⚡ 配置系统服务..."
sudo cp quit_habit.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable quit_habit
sudo systemctl start quit_habit

# 6. 配置 Nginx（可选）
if command -v nginx &> /dev/null; then
    echo "🌐 配置 Nginx..."
    sudo cp nginx.conf /etc/nginx/sites-available/quit_habit
    sudo ln -sf /etc/nginx/sites-available/quit_habit /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl reload nginx
    echo "✅ Nginx 配置完成"
else
    echo "⚠️  未检测到 Nginx，跳过 Web 服务器配置"
    echo "   应用将直接在 http://localhost:5000 运行"
fi

# 7. 检查服务状态
echo ""
echo "🎉 部署完成！"
echo ""
echo "📊 服务状态："
sudo systemctl status quit_habit --no-pager | head -10

echo ""
echo "📝 有用的命令："
echo "  查看日志: sudo journalctl -u quit_habit -f"
echo "  重启服务: sudo systemctl restart quit_habit"
echo "  停止服务: sudo systemctl stop quit_habit"
echo ""
echo "🌐 访问应用："
if command -v nginx &> /dev/null; then
    echo "  http://your-server-ip/"
else
    echo "  http://your-server-ip:5000/"
fi
