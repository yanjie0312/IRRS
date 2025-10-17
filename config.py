import os
from dotenv import load_dotenv

# 1️⃣ 读取 .env 文件
load_dotenv()

# 2️⃣ 定义配置类
class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    ENV = os.getenv("ENV", "dev")

# 3️⃣ 创建全局配置对象
settings = Settings()
