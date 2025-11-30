import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """应用配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-me'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///quit_habit.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
