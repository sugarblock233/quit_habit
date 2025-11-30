# 习惯戒除应用 - Quit Habit Tracker

一款简洁、高效的习惯戒除追踪应用，帮助你记录和管理戒除目标。

## 🎯 核心特点

- **默认成功机制**：采用"默认成功，主动标记失败"的设计理念，减少打卡负担
- **日历视图**：直观的日历展示，成功显示为绿色，失败显示为红色
- **移动端优化**：完美适配手机浏览器，随时随地记录
- **失败原因记录**：每次失败都可记录原因，帮助反思和改进
- **统计分析**：显示连续成功天数、最近失败日期等关键数据

## 📋 功能清单

- ✅ 创建多个习惯目标
- ✅ 设置习惯开始日期
- ✅ 按月查看日历视图
- ✅ 标记并记录失败原因
- ✅ 编辑/删除失败记录
- ✅ 查看连续成功天数
- ✅ 响应式设计，支持移动端

## 🚀 快速开始

### 前置要求

- Python 3.8+
- pip

### 安装步骤

1. **克隆或下载项目**

```bash
cd /root/quit_habit
```

2. **创建虚拟环境（推荐）**

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 Windows: venv\Scripts\activate
```

3. **安装依赖**

```bash
pip install -r requirements.txt
```

4. **配置环境变量**

```bash
cp .env.example .env
# 编辑 .env 文件，设置你的配置（可选）
```

5. **运行应用**

```bash
python app.py
```

或使用启动脚本：

```bash
chmod +x start.sh
./start.sh
```

6. **访问应用**

打开浏览器访问：`http://localhost:5000`

在手机上访问：`http://你的服务器IP:5000`

## 📁 项目结构

```
quit_habit/
├── app.py                  # Flask 应用主文件
├── models.py              # 数据库模型
├── config.py              # 配置文件
├── requirements.txt       # Python 依赖
├── .env.example          # 环境变量示例
├── start.sh              # 启动脚本
├── templates/            # HTML 模板
│   ├── index.html       # 主页（习惯列表）
│   └── habit_detail.html # 习惯详情页（日历）
└── static/              # 静态资源
    └── css/
        └── style.css    # 样式文件
```

## 🗄️ 数据库设计

### habits 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String | 习惯名称 |
| description | Text | 习惯描述 |
| start_date | Date | 开始日期 |
| created_at | DateTime | 创建时间 |

### habit_records 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| habit_id | Integer | 关联习惯ID |
| date | Date | 记录日期 |
| status | String | 状态（默认 'fail'） |
| reason | Text | 失败原因 |
| created_at | DateTime | 创建时间 |

## 🔌 API 接口

### 习惯管理
- `GET /api/habits` - 获取所有习惯
- `POST /api/habits` - 创建新习惯
- `GET /api/habits/<id>` - 获取单个习惯
- `DELETE /api/habits/<id>` - 删除习惯

### 日历与记录
- `GET /api/habits/<id>/calendar?year=2024&month=1` - 获取日历数据
- `POST /api/habits/<id>/records` - 标记失败
- `PUT /api/records/<id>` - 更新失败记录
- `DELETE /api/records/<id>` - 删除失败记录

## 🚢 生产环境部署

### 使用 Gunicorn

1. 安装 Gunicorn

```bash
pip install gunicorn
```

2. 启动应用

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 使用 Nginx 反向代理

配置示例 `/etc/nginx/sites-available/quit_habit`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /root/quit_habit/static;
    }
}
```

### 使用 Systemd 服务

创建 `/etc/systemd/system/quit_habit.service`:

```ini
[Unit]
Description=Quit Habit Tracker
After=network.target

[Service]
User=root
WorkingDirectory=/root/quit_habit
Environment="PATH=/root/quit_habit/venv/bin"
ExecStart=/root/quit_habit/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl start quit_habit
sudo systemctl enable quit_habit
```

## 🔒 安全配置

### 快速启用密码保护

如果要将应用部署到公网，强烈建议启用密码保护：

```bash
# 运行安全配置向导
./setup_security.sh

# 或手动设置密码
echo "APP_PASSWORD=your-strong-password" >> .env
```

启用密码后，访问应用需要先登录。

### 完整安全方案

详细的安全配置请查看 [SECURITY.md](SECURITY.md)，包括：
- 基础密码保护
- HTTPS 配置
- IP 白名单
- 防暴力破解
- VPN 访问
- 最佳安全实践

### 安全建议

1. **修改 SECRET_KEY**：在 `.env` 文件中设置强密码
2. **启用密码保护**：设置 `APP_PASSWORD`
3. **使用 HTTPS**：配置 SSL 证书（Let's Encrypt）
4. **配置防火墙**：只开放必要端口
5. **定期备份**：备份 `quit_habit.db` 数据库文件

## 🛠️ 故障排查

### 数据库问题
如果遇到数据库错误，删除现有数据库重新创建：
```bash
rm quit_habit.db
python app.py  # 会自动创建新数据库
```

### 端口被占用
修改 `app.py` 中的端口号，或者杀掉占用进程：
```bash
lsof -ti:5000 | xargs kill -9
```

## 📝 开发计划

- [ ] 数据导出功能（CSV/JSON）
- [ ] 统计报表与图表
- [ ] Telegram/微信提醒
- [ ] 多用户支持
- [ ] 暗黑模式
- [ ] PWA 支持（离线访问）

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，请提交 GitHub Issue。

---

**祝你成功戒除不良习惯，养成更好的生活方式！** 💪
