# config.py
import os
from dotenv import load_dotenv

# ✅ 1️⃣ 加载 .env 文件（本地开发用；Cloud Run 会直接用环境变量）
load_dotenv()

# ✅ 2️⃣ 定义配置类
class Settings:
    # 优先用 Cloud Run 环境变量 DATABASE_URL，
    # 如果没有就 fallback 到本地 SQLite 文件，这样容器也能启动。
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

    # 保留 SECRET_KEY（默认值防止 None）
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")

    # 环境标志（可选）
    ENV = os.getenv("ENV", "dev")

# ✅ 3️⃣ 创建全局配置对象
settings = Settings()
