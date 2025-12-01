# JobFitCV - 匹配记录数据模型（初版草案）

## 1. 核心实体：MatchRecord

每次用户点击一次「Preview Match」，就生成一条 MatchRecord。

字段（草案）：

- `id`: string  
  - 唯一 ID（例如 UUID）

- `created_at`: datetime  
  - 记录创建时间（UTC）

- `cv_raw`: text  
  - 用户输入的 CV 原始文本

- `jd_raw`: text  
  - 用户输入的 JD 原始文本

- `cv_skills`: string[]  
  - 从 CV 抽取的技能列表（LLM 输出）

- `jd_skills`: string[]  
  - 从 JD 抽取的技能列表（LLM 输出）

- `covered_skills`: string[]  
  - 技能交集（经过 normalize 后的 JD ∩ CV）

- `missing_skills`: string[]  
  - JD 想要但 CV 没覆盖的技能（JD - CV）

- `match_score`: float  
  - 语义匹配分（LLM）

- `coverage_ratio`: float  
  - 硬匹配技能覆盖率（0~1）

- `overall_score`: float  
  - 综合评分（0~1）

- `strengths`: string[]  
  - 优势点列表（LLM）

- `gaps`: string[]  
  - 缺口 / 风险点列表（LLM）

- `suggestions`: string[]  
  - 优化建议列表（LLM）

（未来可选字段）

- `user_id`: string | null  
  - 未来如果有登录系统，可以关联到用户

- `meta`: json  
  - 可选，预留给未来的 trace 信息（模型版本、prompt 版本、耗时、token 数等）

## 2. 未来存储形态（预告）

短期：
- 可以先用内存 / 本地文件 / SQLite 记录 MatchRecord

中期：
- 迁移到 Postgres（云服务），方便做查询和分析（例如「一段时间内的平均匹配分」）

长期：
- 作为 “matching-service” 的数据库表 `match_records`，
  供其它微服务（Analytics / Recommendation 等）读取。
