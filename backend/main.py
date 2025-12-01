from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from schemas import MatchPreviewRequest, MatchPreviewResponse
from services.matching import analyze_match
from db import init_db, get_session
from repositories.match_repo import save_match_record



app = FastAPI(
    title="JobFitCV API",
    version="0.1.0"
)

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
    return {"message": "Hello from JobFitCV backend!"}

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

