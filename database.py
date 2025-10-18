# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import settings
import os

# ✅ 1. 给 DATABASE_URL 一个安全的默认值（防止 env 没配置时报错）
DATABASE_URL = getattr(settings, "DATABASE_URL", None) or os.getenv("DATABASE_URL", "sqlite:///./app.db")

# ✅ 2. 为 SQLite 加上 connect_args，其他数据库则不加
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# ✅ 3. 加上 pool_pre_ping=True，避免连接池中断
engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)

# ✅ 4. 创建 session 工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ 5. 声明 Base
class Base(DeclarativeBase):
    pass

# ✅ 6. 提供依赖注入函数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
