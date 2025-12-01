# JobFitCV - Matching Service V2 架构说明

## 1. 目标

在 V2 中，Matching Service 提供两个维度的信号：

1. **LLM 语义匹配分**  
   - 字段：`match_score`
   - 模型综合 CV + JD 的语义理解给出的评分

2. **技能覆盖度（基于结构化技能列表）**  
   - 字段：`coverage_ratio`, `covered_skills`, `missing_skills`
   - 基于 `cv_skills` 和 `jd_skills` 做集合运算，度量硬匹配情况

前端展示两个视角：
- 上层：一个整体的匹配感受（Match score + Skill coverage）
- 下层：详细的 strengths / gaps / suggestions / skills

---

## 2. 当前 V2 数据流（简化）

用户浏览器  
→ 前端 Next.js 页面  
→ 调用 `POST /match/preview`  
→ FastAPI 路由（只转发、不做业务）  
→ `services.matching.analyze_match`：

1. 调用 LLM（Chat Completions, JSON 模式），生成：
   - `match_score`
   - `strengths`, `gaps`, `suggestions`
   - `cv_skills`, `jd_skills`

2. 在代码里对 `cv_skills` / `jd_skills` 做集合运算：
   - `covered_skills = jd ∩ cv`
   - `missing_skills = jd - cv`
   - `coverage_ratio = |covered| / |jd|`

3. 返回统一的 `MatchPreviewResponse` JSON 给前端。

---

## 3. V2 的“硬匹配”特点

当前的 `coverage_ratio` 属于 **规则层 / keyword 层**：

- 使用的是 **exact match**（大小写规整 + 去空格）
- 优点：简单、确定、容易解释
- 缺点：不理解同义词、缩写、相似概念

所以会出现现象：
- CV 和 JD 都在讲 “RAG / LLM / Agentic AI”，
- 但只要技能 token 不完全相同，就不算覆盖，
- 导致 coverage_ratio 看起来偏低。

这是设计上的 trade-off：  
> 先有一个保守、透明的硬指标，再计划语义增强。

---

## 4. 未来 V3/V4 升级方向（草图）

在保持当前接口不变的前提下，可以增加内部组件：

1. **Skill Normalizer Service**
   - 把类似 `"LangChain framework"` → `"langchain"`
   - `"Azure AI Engineer Associate"` → `"azure ai engineer associate"`
   - 可以基于小词典 + LLM 归一化

2. **Semantic Skill Matching Service**
   - 使用向量 embedding 或 LLM，对技能做语义相似度计算：
     - 例如：`"RL"` ≈ `"reinforcement learning"`
     - `"transformer models"` ≈ `"LLM architectures"`
   - 输出语义层的 `semantic_coverage_ratio`

3. **Final Scoring Service**
   - 组合多个信号：
     - `model_score`（LLM 主观分）
     - `coverage_ratio`（硬匹配）
     - `semantic_coverage_ratio`（语义匹配）
   - 得出更稳定、更可解释的总分。

对外 contract 仍然是：
`POST /match/preview -> MatchPreviewResponse`  
内部可以自由演进为多微服务协作。

---

## 5. 小结

- V2 的 `coverage_ratio` 是“字面硬匹配”，不懂语义，这是**有意选择**。
- V2 已经具备：
  - 结构化技能抽取
  - 集合运算 + 缺失技能列表
  - LLM + 规则混合的 hybrid matching 思路
- 下一阶段，可以在不改 API 的前提下，引入：
  - 归一化 / 词典
  - 语义相似度（embedding / LLM）
  - 更专业的 scoring 策略
