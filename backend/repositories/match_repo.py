from sqlmodel import Session
from models import MatchRecord
from schemas import MatchPreviewRequest  # 从 schemas 模块导入，避免循环导入


def save_match_record(
    session: Session,
    payload: MatchPreviewRequest,
    result: dict,
    user_id: str | None = None,
) -> MatchRecord:
    """
    把一次匹配的输入 + 输出存进数据库。
    """
    record = MatchRecord(
        cv_text=payload.cv_text,
        job_description=payload.job_description,
        cv_skills=result["cv_skills"],
        jd_skills=result["jd_skills"],
        covered_skills=result["covered_skills"],
        missing_skills=result["missing_skills"],
        match_score=result["match_score"],
        coverage_ratio=result["coverage_ratio"],
        overall_score=result["overall_score"],
        strengths=result["strengths"],
        gaps=result["gaps"],
        suggestions=result["suggestions"],
        user_id=user_id,
    )

    session.add(record)
    session.commit()
    session.refresh(record)
    return record
