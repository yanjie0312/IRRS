import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 从环境变量读取配置
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "")
DB_NAME = os.getenv("DB_NAME", "irrs_db")
INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME")

# Cloud Run + Cloud SQL 推荐使用 Unix Socket 路径
# host="/cloudsql/<project>:<region>:<instance>"
DB_SOCKET_DIR = f"/cloudsql/{INSTANCE_CONNECTION_NAME}"

# 构造连接字符串（PostgreSQL）
SQLALCHEMY_DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@/{DB_NAME}?host={DB_SOCKET_DIR}"
)

# 创建 SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

# 创建 session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM 基类
Base = declarative_base()


# 依赖函数（用于 FastAPI 路由中自动注入）
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
