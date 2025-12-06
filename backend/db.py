from sqlmodel import SQLModel, create_engine, Session
import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
# 这样在本地开发时，Python 就能读取到 .env 文件中的配置了
load_dotenv()


# ---------- 1. 环境检测：是不是在 Lambda 里？ ----------

def is_lambda_environment() -> bool:
    """
    检测当前代码是不是跑在 AWS Lambda 环境中
    只要这些环境变量里有任意一个存在，就认为是在 Lambda 里
    """
    lambda_indicators = [
        "LAMBDA_TASK_ROOT",           # Lambda 任务根目录
        "AWS_EXECUTION_ENV",          # AWS 执行环境标识
        "AWS_LAMBDA_FUNCTION_NAME",   # Lambda 函数名
        "_LAMBDA_TELEMETRY_LOG_FD",   # Lambda 遥测日志文件描述符
    ]
    return any(os.getenv(name) for name in lambda_indicators)


# ---------- 2. 决定 DATABASE_URL ----------

def get_database_url() -> str:
    """
    按优先级决定用哪个数据库地址：

    1. 如果设置了 DATABASE_URL 环境变量 -> 用它（以后连接 RDS Postgres 就用这条）
    2. 如果在 Lambda 环境 -> 用 /tmp 下的 sqlite 文件（唯一可写目录）
    3. 否则（本地开发） -> 用当前目录下的 jobfitcv.db
    """
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    if is_lambda_environment():
        # Lambda 环境：用 /tmp 目录
        return "sqlite:////tmp/jobfitcv.db"

    # 本地开发环境
    return "sqlite:///./jobfitcv.db"


DATABASE_URL = get_database_url()


# ---------- 3. 创建全局 engine（连接工厂） ----------

# SQLite 需要特殊的 connect_args，Postgres 等不需要
engine_kwargs = {"echo": False}
if DATABASE_URL.startswith("sqlite"):
    # 这个配置只对 sqlite 有意义：允许多个线程共享同一个连接
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)


# ---------- 4. 对外暴露：拿 Session + 初始化数据库 ----------

def get_session() -> Session:
    """
    拿一个 Session 出来，用完你自己 with 关闭：
    with get_session() as session:
        ...
    """
    return Session(engine)


def init_db() -> None:
    """
    初始化数据库：根据 SQLModel 定义的模型，在数据库里建表
    """
    # 延迟导入，避免循环引用
    from models import MatchRecord

    # 把所有 SQLModel.table=True 的模型同步到数据库
    SQLModel.metadata.create_all(engine)