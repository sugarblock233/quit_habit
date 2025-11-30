import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """应用配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-me'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///quit_habit.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 安全配置
    APP_PASSWORD = os.environ.get('APP_PASSWORD')  # 如果设置了密码，则启用登录
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'  # 生产环境使用 HTTPS
    SESSION_COOKIE_HTTPONLY = True  # 防止 XSS 攻击
    SESSION_COOKIE_SAMESITE = 'Lax'  # 防止 CSRF 攻击
    PERMANENT_SESSION_LIFETIME = 2592000  # Session 有效期 30 天
