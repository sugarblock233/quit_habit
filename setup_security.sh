#!/bin/bash

# 快速安全配置脚本

echo "🔒 习惯戒除应用 - 安全配置向导"
echo "================================"
echo ""

# 检查是否已配置
if grep -q "^APP_PASSWORD=.\+" /root/quit_habit/.env 2>/dev/null; then
    echo "⚠️  检测到已设置密码"
    read -p "是否要重新配置？(y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "已取消"
        exit 0
    fi
fi

echo "请选择安全配置方案："
echo ""
echo "1) 基础密码保护（推荐，适合个人使用）"
echo "2) 生成强随机密码"
echo "3) 自定义密码"
echo "4) 禁用密码保护（仅本地使用）"
echo ""
read -p "请选择 [1-4]: " choice

case $choice in
    1)
        echo ""
        read -sp "请输入密码: " password1
        echo ""
        read -sp "请再次确认: " password2
        echo ""
        
        if [ "$password1" != "$password2" ]; then
            echo "❌ 两次密码不一致"
            exit 1
        fi
        
        if [ ${#password1} -lt 8 ]; then
            echo "❌ 密码长度至少 8 位"
            exit 1
        fi
        
        password="$password1"
        ;;
    
    2)
        password=$(openssl rand -base64 16)
        echo ""
        echo "🔑 已生成强随机密码："
        echo "   $password"
        echo ""
        echo "⚠️  请妥善保存此密码！"
        echo ""
        read -p "按回车继续..."
        ;;
    
    3)
        echo ""
        read -sp "请输入自定义密码: " password
        echo ""
        
        if [ ${#password} -lt 8 ]; then
            echo "❌ 密码长度至少 8 位"
            exit 1
        fi
        ;;
    
    4)
        password=""
        echo ""
        echo "⚠️  警告：禁用密码保护后，任何人都可以访问应用"
        read -p "确定要继续吗？(y/N) " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "已取消"
            exit 0
        fi
        ;;
    
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

# 更新 .env 文件
if [ -f "/root/quit_habit/.env" ]; then
    # 删除旧的 APP_PASSWORD 配置
    sed -i '/^APP_PASSWORD=/d' /root/quit_habit/.env
else
    cp /root/quit_habit/.env.example /root/quit_habit/.env
fi

# 添加新配置
echo "APP_PASSWORD=$password" >> /root/quit_habit/.env

# 生成强 SECRET_KEY
if ! grep -q "^SECRET_KEY=.\{20,\}" /root/quit_habit/.env 2>/dev/null; then
    secret_key=$(openssl rand -base64 32)
    sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$secret_key|" /root/quit_habit/.env
    echo "✅ 已生成新的 SECRET_KEY"
fi

echo ""
echo "✅ 安全配置完成！"
echo ""

if [ -n "$password" ]; then
    echo "🔐 访问密码已设置"
    echo ""
    echo "下次访问应用时需要输入密码"
else
    echo "⚠️  密码保护已禁用"
fi

echo ""
echo "重启应用以应用更改："
echo "  开发环境: Ctrl+C 停止后重新运行 ./start.sh"
echo "  生产环境: sudo systemctl restart quit_habit"
echo ""

# 询问是否立即重启（如果是 systemd 服务）
if systemctl is-active --quiet quit_habit 2>/dev/null; then
    read -p "是否立即重启服务？(Y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        sudo systemctl restart quit_habit
        echo "✅ 服务已重启"
    fi
fi

echo ""
echo "📖 更多安全配置选项请查看: SECURITY.md"
