# 安全配置指南

## 🔒 安全层级方案

根据你的需求，提供三个安全级别的方案：

---

## 方案一：基础密码保护（推荐，简单有效）

### 特点
- 单用户模式，一个密码保护整个应用
- 实现简单，开销小
- 适合个人使用

### 实现方式
已在应用中内置，使用步骤：

1. **设置访问密码**
   编辑 `.env` 文件：
   ```bash
   APP_PASSWORD=your-strong-password-here
   ```

2. **重启应用**
   ```bash
   sudo systemctl restart quit_habit
   ```

3. **首次访问需要输入密码**
   - 访问任何页面会跳转到登录页
   - 输入密码后，session 保持 30 天
   - 可以手动登出

---

## 方案二：IP 白名单（最严格）

### 特点
- 只允许特定 IP 访问
- 在 Nginx 层面拦截
- 最高安全级别

### Nginx 配置

编辑 `/etc/nginx/sites-available/quit_habit`：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # IP 白名单
    allow 你的家庭IP;
    allow 你的办公室IP;
    allow 你的手机运营商IP段;  # 例如: 123.45.0.0/16
    deny all;  # 拒绝其他所有IP

    location / {
        proxy_pass http://127.0.0.1:5000;
        # ... 其他配置
    }
}
```

重启 Nginx：
```bash
sudo nginx -t && sudo systemctl reload nginx
```

**缺点**：移动网络 IP 经常变化，可能不方便

---

## 方案三：HTTPS + 密码 + 防暴力破解（推荐生产环境）

### 1. 配置 HTTPS（必须）

使用 Let's Encrypt 免费证书：

```bash
# 安装 Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# 获取证书（自动配置 Nginx）
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### 2. 启用密码保护

在 `.env` 中设置：
```bash
APP_PASSWORD=your-strong-password
LOGIN_ATTEMPTS_LIMIT=5  # 最多尝试次数
LOGIN_BLOCK_TIME=3600   # 封禁时间（秒）
```

### 3. 配置防火墙

```bash
# 只开放必要端口
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 4. 配置 Fail2Ban（防暴力破解）

```bash
# 安装
sudo apt install fail2ban

# 创建配置
sudo nano /etc/fail2ban/jail.local
```

添加内容：
```ini
[quit-habit]
enabled = true
port = http,https
filter = quit-habit
logpath = /var/log/nginx/quit_habit_access.log
maxretry = 5
bantime = 3600
findtime = 600
```

创建过滤规则：
```bash
sudo nano /etc/fail2ban/filter.d/quit-habit.conf
```

添加：
```ini
[Definition]
failregex = ^<HOST>.*"POST /api/login HTTP.*" 401
ignoreregex =
```

重启 Fail2Ban：
```bash
sudo systemctl restart fail2ban
```

---

## 方案四：VPN 访问（最安全，但复杂）

### 特点
- 通过 VPN 连接到服务器
- 应用无需公网暴露
- 适合技术用户

### 推荐方案
- **WireGuard**: 现代、快速、简单
- **Tailscale**: 零配置的 WireGuard
- **OpenVPN**: 传统方案

### 配置 WireGuard（简化版）

```bash
# 安装
sudo apt install wireguard

# 生成密钥
wg genkey | tee privatekey | wg pubkey > publickey

# 配置服务器
sudo nano /etc/wireguard/wg0.conf

# 配置客户端（手机安装 WireGuard App）
# 扫描二维码连接
```

应用监听在 `localhost:5000`，通过 VPN 访问

---

## 🛡️ 通用安全建议

### 1. 强密码策略
```bash
# 生成强密码
openssl rand -base64 32
```

### 2. 定期备份
```bash
# 添加到 crontab
0 2 * * * /root/quit_habit/backup.sh
```

### 3. 监控日志
```bash
# 查看访问日志
sudo tail -f /var/log/nginx/quit_habit_access.log

# 查看应用日志
sudo journalctl -u quit_habit -f
```

### 4. 更新系统
```bash
# 定期更新
sudo apt update && sudo apt upgrade -y
```

### 5. 限制 SSH 访问
```bash
# 编辑 SSH 配置
sudo nano /etc/ssh/sshd_config

# 建议设置：
PermitRootLogin no          # 禁止 root 登录
PasswordAuthentication no   # 只用密钥登录
Port 2222                   # 改变默认端口
```

---

## 📊 安全方案对比

| 方案 | 安全性 | 易用性 | 复杂度 | 推荐场景 |
|------|--------|--------|--------|----------|
| 基础密码 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | 个人使用 |
| IP 白名单 | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | 固定 IP |
| HTTPS+密码+Fail2Ban | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | **推荐** |
| VPN | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | 技术用户 |

---

## 🚀 快速实施（5分钟方案）

**推荐：HTTPS + 密码保护**

```bash
# 1. 设置密码
echo "APP_PASSWORD=$(openssl rand -base64 16)" >> /root/quit_habit/.env

# 2. 安装证书（需要域名）
sudo certbot --nginx -d your-domain.com

# 3. 重启应用
sudo systemctl restart quit_habit

# 完成！现在你的应用：
# ✅ 使用 HTTPS 加密传输
# ✅ 需要密码才能访问
# ✅ 密码存储加密
```

---

## ⚠️ 紧急情况

### 忘记密码
```bash
# 重置密码
echo "APP_PASSWORD=new-password" >> /root/quit_habit/.env
sudo systemctl restart quit_habit
```

### 被锁定
```bash
# 清除登录限制
rm /root/quit_habit/instance/login_attempts.json
sudo systemctl restart quit_habit
```

### 查看登录日志
```bash
# 查看谁在尝试访问
sudo grep "POST /api/login" /var/log/nginx/quit_habit_access.log
```

---

## 📝 安全检查清单

部署前检查：

- [ ] 设置了强密码（至少 16 字符）
- [ ] 启用了 HTTPS
- [ ] 修改了 SECRET_KEY
- [ ] 配置了防火墙
- [ ] 数据库文件不在 git 中
- [ ] .env 文件不在 git 中
- [ ] 定期备份已设置
- [ ] SSH 使用密钥登录
- [ ] 系统已更新到最新
- [ ] 查看了登录日志

---

**建议**：对于个人使用，"方案三：HTTPS + 密码 + Fail2Ban" 是最佳平衡点。既安全又不失便利性。
