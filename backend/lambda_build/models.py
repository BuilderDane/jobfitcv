from typing import Optional, List
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Column, JSON


class MatchRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # 原因解释：有时IDE会将utcnow划掉，是因为被认为是一个"可变的默认参数"，推荐方式是使用datetime.now(timezone.utc)
    # 这样可以确保生成的时间包含明确的时区信息，避免时区相关bug（特别是长期维护的软件推荐带时区信息）。
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # 和 MatchPreviewRequest 对齐
    cv_text: str
    job_description: str

    # 和 MatchPreviewResponse 对齐
    cv_skills: list[str] = Field(sa_column=Column(JSON))
    jd_skills: list[str] = Field(sa_column=Column(JSON))

    covered_skills: list[str] = Field(sa_column=Column(JSON))
    missing_skills: list[str] = Field(sa_column=Column(JSON))

    match_score: float
    coverage_ratio: float
    overall_score: float

    strengths: list[str] = Field(sa_column=Column(JSON))
    gaps: list[str] = Field(sa_column=Column(JSON))
    suggestions: list[str] = Field(sa_column=Column(JSON))

    # 预留
    user_id: Optional[str] = None
