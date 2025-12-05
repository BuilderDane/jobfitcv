from sqlmodel import SQLModel, create_engine, Session
import os

# 1. 数据库地址
# 优先从环境变量 DATABASE_URL 读；
# 如果没有，检测是否在 Lambda 环境中（使用多个 Lambda 环境变量判断）
# Lambda 环境：使用 /tmp 目录（唯一可写目录）
# 本地开发环境：使用当前目录

def is_lambda_environment():
    """检测是否在 AWS Lambda 环境中"""
    # Lambda 环境会有这些环境变量之一
    lambda_indicators = [
        "LAMBDA_TASK_ROOT",      # Lambda 任务根目录
        "AWS_EXECUTION_ENV",     # AWS 执行环境
        "AWS_LAMBDA_FUNCTION_NAME",  # Lambda 函数名
        "_LAMBDA_TELEMETRY_LOG_FD",  # Lambda 遥测日志文件描述符
    ]
    return any(os.getenv(indicator) for indicator in lambda_indicators)

if os.getenv("DATABASE_URL"):
    DATABASE_URL = os.getenv("DATABASE_URL")
elif is_lambda_environment():
    # Lambda 环境：使用 /tmp 目录（唯一可写目录）
    DATABASE_URL = "sqlite:////tmp/jobfitcv.db"
else:
    # 本地开发环境
    DATABASE_URL = "sqlite:///./jobfitcv.db"

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
