from sqlmodel import SQLModel, create_engine, Session
import os

# 1. 数据库地址
# 优先从环境变量 DATABASE_URL 读；
# 如果没有，就用一个本地的 SQLite 文件 jobfitcv.db
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./jobfitcv.db")

# 2. 创建一个全局的数据库引擎（engine）
#    可以理解成：数据库“连接工厂”
engine = create_engine(
    DATABASE_URL,
    echo=False,                      # True 的话会在终端打印 SQL 语句（调试时可以打开）
    connect_args={"check_same_thread": False},  # SQLite 在多线程下需要这个配置
)


# 3. get_session：每次要操作数据库时，拿一个 Session 出来
#    Session 就像是“这次访问数据库的小通道”
def get_session() -> Session:
    return Session(engine)


# 4. init_db：初始化数据库（创建表）
def init_db():
    # 这里延迟导入 MatchRecord，避免循环引用
    from models import MatchRecord

    # 根据 SQLModel 定义的所有 table=True 的模型，自动在数据库里建表
    SQLModel.metadata.create_all(engine)
