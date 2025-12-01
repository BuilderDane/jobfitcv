from pydantic import BaseModel
from typing import List


class MatchPreviewRequest(BaseModel):
    cv_text: str
    job_description: str


class MatchPreviewResponse(BaseModel):
    match_score: float              # 纯语义分（LLM）
    strengths: list[str]
    gaps: list[str]
    suggestions: list[str]
    cv_skills: list[str]
    jd_skills: list[str]
    coverage_ratio: float           # 技能覆盖率 0~1
    covered_skills: list[str]       # 已覆盖的 JD 技能
    missing_skills: list[str]       # JD 想要但 CV 里没有
    overall_score: float            # 组合后的总评分 0~1
