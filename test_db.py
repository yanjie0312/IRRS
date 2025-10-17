from sqlalchemy import create_engine, text
from config import settings

# 创建数据库引擎
engine = create_engine(settings.DATABASE_URL)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();")).fetchone()
        print("✅ 成功连接到数据库！")
        print("PostgreSQL 版本：", result[0])
except Exception as e:
    print("❌ 数据库连接失败：", e)
