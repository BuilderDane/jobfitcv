from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum  

from sqlmodel import Session, select
from db import engine

from schemas import MatchPreviewRequest, MatchPreviewResponse
from services.matching import analyze_match
from db import init_db, get_session
from repositories.match_repo import save_match_record
from models import MatchRecord


# 创建 FastAPI 应用
app = FastAPI(
    title="JobFitCV API",
    version="0.1.0"
)

# 延迟初始化数据库，避免在 Lambda 启动时出错
# 使用 startup 事件，在应用启动时初始化数据库
@app.on_event("startup")
async def startup_event():
    init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "JobFitCV backend auto-updated via CI/CD!!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/meta")
def get_meta():
    return {
        "app": "JobFitCV",
        "version": "0.1.0",
        "description": "API for matching CVs to job descriptions."
    }

@app.get("/db/health")
def db_health():
    """简单检查数据库是否可用 + 看看现在有多少条 MatchRecord"""
    try:
        with Session(engine) as s:
            # 只做一个很轻量的查询
            rows = s.exec(select(MatchRecord)).all()
            return {
                "status": "ok",
                "records_count": len(rows),
            }
    except Exception as e:
        # 如果连不上 / 查询出错，就返回 error
        return {
            "status": "error",
            "detail": str(e),
        }


@app.post("/match/preview", response_model=MatchPreviewResponse)
def preview_match(payload: MatchPreviewRequest):
    # 1. 调用匹配服务，拿到结果
    data = analyze_match(
        cv_text=payload.cv_text,
        jd_text=payload.job_description,
    )

    # 2. 打开一个数据库 Session，写入 MatchRecord
    with get_session() as session:
        save_match_record(
            session=session,
            payload=payload,
            result=data,
            user_id=None,  # 以后接入登录系统再填真实用户
        )

    # 3. 再把结果返回给前端
    return MatchPreviewResponse(**data)

handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)