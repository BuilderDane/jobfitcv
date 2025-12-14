from fastapi import FastAPI
from pydantic import BaseModel
app = FastAPI(title="JobFitCV API", version="0.0.1")


PHRASES = [
    "user experience",
    "ui ux",
    "ui/ux",
    "product engineer",
    "product engineering",
    "ai product engineer",
]


# ---------- Data Models (Request / Response) ----------

class PreviewMatchRequest(BaseModel):
    cv_text: str
    jd_text: str


class PreviewMatchResponse(BaseModel):
    match_score: float
    strengths: list[str]
    gaps: list[str]
    suggestions: list[str]
    cv_skills: list[str]
    jd_skills: list[str]


# ---------- Helpers (MVP logic) ----------

def _extract_keywords(text: str) -> set[str]:
    text = text.lower()

    tokens: list[str] = []
    cur: list[str] = []

    for ch in text:
        if ch.isalnum() or ch in ["+", "-", "."]:
            cur.append(ch)
        else:
            if cur:
                tokens.append("".join(cur))
                cur = []
    if cur:
        tokens.append("".join(cur))

    # 基础停用词（结构词）
    stop = {
    # 结构词
    "and", "or", "the", "a", "an", "to", "of", "in", "on", "for", "with",
    # 代词/冠词/常见无信息词
    "i", "me", "my", "you", "your", "we", "our", "they", "their",
    "is", "am", "are", "was", "were", "be", "been", "being",
    "this", "that", "these", "those",
    # 常见动词（JD/CV里很容易污染结果）
    "looking", "build", "built", "use", "used", "using", "need", "needs",
    "want", "wants", "seeking", "seeks", "require", "requires", "required",
    "experience", "experiences",
}


    cleaned = set()
    for t in tokens:
        t = t.strip(".")          # 去尾部标点，如 cd.
        if len(t) < 2:
            continue
        if t in stop:
            continue
        cleaned.add(t)

    return cleaned



# ---------- Routes ----------

@app.get("/")
def root():
    return {"message": "JobFitCV API running. Go to /docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/preview-match", response_model=PreviewMatchResponse)
def preview_match(payload: PreviewMatchRequest):
    cv = payload.cv_text.strip()
    jd = payload.jd_text.strip()

    if not cv or not jd:
        return {
            "match_score": 0.0,
            "strengths": [],
            "gaps": ["cv_text and jd_text are required"],
            "suggestions": [],
            "cv_skills": [],
            "jd_skills": [],
        }

    cv_set = _extract_keywords(cv)
    jd_set = _extract_keywords(jd)

    overlap = cv_set & jd_set          # strengths: in both CV and JD
    missing = jd_set - cv_set          # gaps: in JD but not in CV

    # match_score = how much of JD keywords are covered by CV (0~1)
    match_score = len(overlap) / max(len(jd_set), 1)

    strengths = sorted(list(overlap))[:10]
    gaps = sorted(list(missing))[:10]
    suggestions = [f"Add evidence for: {k}" for k in gaps[:5]]

    return {
        "match_score": round(match_score, 2),
        "strengths": strengths,
        "gaps": gaps,
        "suggestions": suggestions,
        "cv_skills": sorted(list(cv_set))[:20],
        "jd_skills": sorted(list(jd_set))[:20],
    }
