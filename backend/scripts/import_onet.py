import os
import re
import csv
from pathlib import Path
from typing import Dict, Tuple, Optional, Iterable, List

import psycopg2
from psycopg2.extras import execute_values


# ---------- Helpers: find files by keywords ----------

def find_file(data_dir: Path, patterns: List[str]) -> Optional[Path]:
    files = list(data_dir.glob("*"))
    lower = {f.name.lower(): f for f in files}
    # 先按 pattern 逐个匹配
    for p in patterns:
        for name, f in lower.items():
            if p in name:
                return f
    return None


def open_tsv(path: Path) -> Iterable[Dict[str, str]]:
    # O*NET 多为 tab 分隔，且有表头
    with path.open("r", encoding="utf-8-sig", newline="") as fp:
        reader = csv.DictReader(fp, delimiter="\t")
        for row in reader:
            yield {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in row.items()}


def norm_scale_name(name: str) -> str:
    # 统一尺度名：importance / level
    s = name.strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def infer_type_from_element_id(element_id: str) -> str:
    # O*NET Content Model 的 Element ID 前缀可大致判断类型
    # 1.A.* Abilities, 2.A.* Skills, 2.C.* Knowledge, 4.A/4.C Work Activities
    if element_id.startswith("1.A"):
        return "ability"
    if element_id.startswith("2.A"):
        return "skill"
    if element_id.startswith("2.C"):
        return "knowledge"
    if element_id.startswith("4."):
        return "activity"
    return "skill"


# ---------- DB ----------

DDL_HINT = """
你需要先建好表：
occupations(onetsoc_code pk, title, description)
skills(skill_id pk, name unique, type)
occupation_skill(onetsoc_code fk, skill_id fk, scale, value, pk(onetsoc_code, skill_id, scale))
kb_chunks(chunk_id pk, source, onetsoc_code nullable, skill_id nullable, title, content)
"""

def get_conn():
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        raise RuntimeError("DATABASE_URL not set.\n" + DDL_HINT)
    return psycopg2.connect(dsn)


# ---------- Import steps ----------

def load_content_model_reference(path: Path) -> Dict[str, str]:
    # Element ID -> Element Name
    m: Dict[str, str] = {}
    for row in open_tsv(path):
        eid = row.get("Element ID") or row.get("ElementId") or row.get("ElementID")
        name = row.get("Element Name") or row.get("ElementName") or row.get("Element")
        if eid and name:
            m[eid] = name
    return m


def load_scales_reference(path: Path) -> Dict[str, str]:
    # Scale ID -> Scale Name
    m: Dict[str, str] = {}
    for row in open_tsv(path):
        sid = row.get("Scale ID") or row.get("ScaleId") or row.get("ScaleID")
        name = row.get("Scale Name") or row.get("ScaleName") or row.get("Scale")
        if sid and name:
            m[sid] = norm_scale_name(name)
    return m


def upsert_occupations(conn, occ_path: Path):
    rows = []
    for r in open_tsv(occ_path):
        code = r.get("O*NET-SOC Code") or r.get("O*NET-SOC Code ") or r.get("O*NET-SOC")
        title = r.get("Title")
        desc = r.get("Description")
        if code and title:
            rows.append((code, title, desc))

    sql = """
    insert into occupations(onetsoc_code, title, description)
    values %s
    on conflict (onetsoc_code) do update
      set title = excluded.title,
          description = excluded.description
    """
    with conn.cursor() as cur:
        execute_values(cur, sql, rows, page_size=2000)
    conn.commit()
    print(f"✅ occupations upserted: {len(rows)}")


def get_or_create_skill_ids(conn, items: List[Tuple[str, str]]) -> Dict[Tuple[str, str], int]:
    """
    items: [(name, type)]
    return: {(name,type): skill_id}
    """
    # 1) 先插入（去重）
    uniq = {(n, t) for n, t in items if n}
    if not uniq:
        return {}

    insert_sql = """
    insert into skills(name, type)
    values %s
    on conflict (name) do update set type = excluded.type
    returning skill_id, name, type
    """
    # 注意：on conflict(name) 只按 name 唯一，因此 type 用 update 以最新为准（生产上你也可改为不覆盖）
    with conn.cursor() as cur:
        execute_values(cur, insert_sql, list(uniq), page_size=2000)
        inserted = cur.fetchall()

    conn.commit()

    # 2) 再查一次确保拿到所有 skill_id
    with conn.cursor() as cur:
        cur.execute("select skill_id, name, type from skills")
        all_rows = cur.fetchall()

    mapping: Dict[Tuple[str, str], int] = {}
    # name 唯一，所以以 name 为主；type 仅作辅助
    by_name = {name: sid for sid, name, _ in all_rows}
    for name, typ in uniq:
        mapping[(name, typ)] = by_name[name]
    return mapping


def import_ksa_file(conn, path: Path, element_name_map: Dict[str, str], scale_name_map: Dict[str, str], source_label: str):
    """
    Skills.txt / Knowledge.txt / Abilities.txt / Work Activities.txt
    常见列：O*NET-SOC Code, Element ID, Scale ID, Data Value
    """
    raw = []
    skill_items = []

    for r in open_tsv(path):
        code = r.get("O*NET-SOC Code") or r.get("O*NET-SOC")
        element_id = r.get("Element ID") or r.get("ElementID")
        scale_id = r.get("Scale ID") or r.get("ScaleID")
        val = r.get("Data Value") or r.get("DataValue") or r.get("Value")

        if not (code and element_id and scale_id and val):
            continue

        name = element_name_map.get(element_id)
        if not name:
            continue

        scale = scale_name_map.get(scale_id, scale_id.lower())
        typ = infer_type_from_element_id(element_id)

        # 记录：稍后写 occupation_skill
        raw.append((code, name, typ, scale, float(val)))
        skill_items.append((name, typ))

    # 1) skills 表：确保 name 存在
    id_map = get_or_create_skill_ids(conn, skill_items)

    # 2) occupation_skill 表：写关系
    rows = []
    for code, name, typ, scale, val in raw:
        sid = id_map.get((name, typ)) or id_map.get((name, "skill"))
        if sid:
            rows.append((code, sid, scale, val))

    sql = """
    insert into occupation_skill(onetsoc_code, skill_id, scale, value)
    values %s
    on conflict (onetsoc_code, skill_id, scale) do update
      set value = excluded.value
    """
    with conn.cursor() as cur:
        execute_values(cur, sql, rows, page_size=5000)

    conn.commit()
    print(f"✅ {source_label} imported: occupation_skill rows={len(rows)}")


def import_task_statements(conn, path: Path):
    """
    Task Statements：用于 RAG chunk（自然语言非常有用）
    常见列：O*NET-SOC Code, Task, Task ID（不同版本略有差异）
    """
    rows = []
    for r in open_tsv(path):
        code = r.get("O*NET-SOC Code") or r.get("O*NET-SOC")
        task = r.get("Task") or r.get("Task Statement") or r.get("TaskStatement")
        task_id = r.get("Task ID") or r.get("TaskID")

        if task:
            title = f"Task {task_id}" if task_id else "Task"
            rows.append(("tasks", code, None, title, task))

    sql = """
    insert into kb_chunks(source, onetsoc_code, skill_id, title, content)
    values %s
    """
    with conn.cursor() as cur:
        execute_values(cur, sql, rows, page_size=5000)

    conn.commit()
    print(f"✅ task statements chunks inserted: {len(rows)}")


def import_tools_technology(conn, path: Path):
    """
    Tools and Technology：也放进 kb_chunks，后续 embedding 检索会很好用
    常见列：O*NET-SOC Code, Tool/Technology Name（列名可能略不同）
    """
    rows = []
    for r in open_tsv(path):
        code = r.get("O*NET-SOC Code") or r.get("O*NET-SOC")
        name = (
            r.get("Tool Name")
            or r.get("Technology Name")
            or r.get("Tools and Technology")
            or r.get("T2 Name")
            or r.get("Name")
        )
        if name:
            rows.append(("tools_tech", code, None, "Tool/Technology", name))

    sql = """
    insert into kb_chunks(source, onetsoc_code, skill_id, title, content)
    values %s
    """
    with conn.cursor() as cur:
        execute_values(cur, sql, rows, page_size=5000)

    conn.commit()
    print(f"✅ tools/tech chunks inserted: {len(rows)}")


def main():
    data_dir = Path(os.environ.get("ONET_DIR", "data/onet")).resolve()
    if not data_dir.exists():
        raise RuntimeError(f"ONET_DIR not found: {data_dir}")

    # 自动找文件（允许文件名差异）
    occ = find_file(data_dir, ["occupation data"])
    cmr = find_file(data_dir, ["content model reference"])
    scales = find_file(data_dir, ["scales reference"])

    skills = find_file(data_dir, ["skills"])
    knowledge = find_file(data_dir, ["knowledge"])
    abilities = find_file(data_dir, ["abilities"])
    activities = find_file(data_dir, ["work activities"])
    tasks = find_file(data_dir, ["task statements"])
    tools = find_file(data_dir, ["tools and technology", "tools & technology", "technology"])

    print("📦 Using files:")
    for k, v in {
        "Occupation Data": occ,
        "Content Model Reference": cmr,
        "Scales Reference": scales,
        "Skills": skills,
        "Knowledge": knowledge,
        "Abilities": abilities,
        "Work Activities": activities,
        "Task Statements": tasks,
        "Tools & Technology": tools,
    }.items():
        print(f" - {k}: {v.name if v else 'NOT FOUND'}")

    if not (occ and cmr and scales):
        raise RuntimeError("Missing required reference files: Occupation Data / Content Model Reference / Scales Reference")

    element_name_map = load_content_model_reference(cmr)
    scale_name_map = load_scales_reference(scales)

    conn = get_conn()
    try:
        upsert_occupations(conn, occ)

        if skills:
            import_ksa_file(conn, skills, element_name_map, scale_name_map, "Skills")
        if knowledge:
            import_ksa_file(conn, knowledge, element_name_map, scale_name_map, "Knowledge")
        if abilities:
            import_ksa_file(conn, abilities, element_name_map, scale_name_map, "Abilities")
        if activities:
            import_ksa_file(conn, activities, element_name_map, scale_name_map, "Work Activities")

        if tasks:
            import_task_statements(conn, tasks)
        if tools:
            import_tools_technology(conn, tools)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
