"""环境配置：全部从环境变量读取，本地默认 SQLite。"""
import os

# 本地开发默认 SQLite（零配置）；上线改成 MySQL，例如：
# mysql+pymysql://nailong:woshinailong@192.9.169.184:3306/project_8?charset=utf8mb4
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# 前端联调地址
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")

# 一致性预期指数只统计置信度 >= 该值的观点
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.6"))

APP_NAME = "AI 期货研报观点分析"
API_PREFIX = "/api/v1"
