import re
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def normalize_skill(raw: str) -> str:
    """
    把技能 token 统一成比较干净的形式：
    - 去掉前后空格
    - 全部小写
    - 去掉常见尾巴词（framework, experience, skills, knowledge 等）
    - 去掉多余标点
    """
    if not raw:
        return ""

    s = raw.strip().lower()

    # 去掉标点
    s = re.sub(r"[.,;:()]", "", s)

    # 常见无意义尾巴词（可以以后慢慢扩展）
    stop_words = [
        "experience",
        "experiences",
        "skills",
        "skill",
        "framework",
        "frameworks",
        "tools",
        "tooling",
        "knowledge",
        "background",
        "associate",
        "certification",
    ]

    # 按空格拆词，再去掉这些尾巴词
    tokens = [t for t in s.split() if t not in stop_words]

    normalized = " ".join(tokens).strip()
    return normalized




def analyze_match(cv_text: str, jd_text: str) -> dict:
    """
    使用 Chat Completions + JSON 模式，输出稳定 JSON：
    {
      "match_score": float,
      "strengths": [...],
      "gaps": [...],
      "suggestions": [...]
    }
    """

    system_prompt = """
You are a senior AI hiring assistant.
You compare a candidate CV with a job description and output a structured JSON
describing the match quality.
    """.strip()

    user_prompt = f"""
Analyze the following CV and Job Description and return ONLY a JSON object
with the following fields:

{{
  "match_score": number (0.0-1.0),
  "strengths": string[],
  "gaps": string[],
  "suggestions": string[],
  "cv_skills": string[],
  "jd_skills": string[]
}}

Definitions:
- "cv_skills": a flat list of key skills, tools, technologies, and domains explicitly or strongly implied in the CV.
- "jd_skills": a flat list of key skills, tools, technologies, and domains explicitly required or strongly preferred in the JD.
- Do not include soft fluff like "team player" unless it is clearly a requirement.

Rules:
- Output valid JSON only (no explanations, no code fences).
- match_score must be between 0.0 and 1.0.
- strengths/gaps/suggestions must be arrays of short, clear sentences.
- cv_skills/jd_skills should be short skill tokens like "Python", "FastAPI", "microservices", not long sentences.

CV:
{cv_text}

JD:
{jd_text}
""".strip()

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )

    content = resp.choices[0].message.content
    # JSON 模式下这里应该是纯 JSON 字符串
    data = json.loads(content)
    
    cv_skills = data["cv_skills"]
    jd_skills = data["jd_skills"]

    cv_set = set()
    for s in cv_skills:
        n = normalize_skill(s)
        if n:
            cv_set.add(n)

    jd_set = set()
    for s in jd_skills:
        n = normalize_skill(s)
        if n:
            jd_set.add(n)


    covered = sorted(jd_set & cv_set)
    missing = sorted(jd_set - cv_set)

    if len(jd_set) > 0:
        coverage_ratio = len(covered) / len(jd_set)
    else:
        coverage_ratio = 0.0

    semantic_score = float(data["match_score"])
    overall_score = 0.65 * semantic_score + 0.35 * coverage_ratio

    return {
        "match_score": semantic_score,
        "strengths": data["strengths"],
        "gaps": data["gaps"],
        "suggestions": data["suggestions"],
        "cv_skills": cv_skills,
        "jd_skills": jd_skills,
        "coverage_ratio": coverage_ratio,
        "covered_skills": list(covered),
        "missing_skills": list(missing),
        "overall_score": overall_score,
    }


    

