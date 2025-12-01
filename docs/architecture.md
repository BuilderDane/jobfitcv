# JobFitCV - 系统结构（初版）

## 1. 整体结构（V0）

前端（浏览器里的 Web App）  
→ 调用 后端 API（FastAPI）  
→ 后端 再去调用 LLM / 各种服务（未来）

简单理解：

[User Browser]
    ↓ HTTP 请求 (JSON)
[Frontend - JobFitCV Web]
    ↓ 调用 API
[Backend - FastAPI @ /match/preview]
    ↓（未来：调用 LLM / 向量库）
[AI + 数据层]

## 2. 当前已经存在的 API

- `GET /`  
  用来测试后端是否跑起来。

- `GET /health`  
  健康检查：监控用，看服务活着没。

- `GET /meta`  
  返回当前应用的一些信息（名字、版本等）。

- `POST /match/preview`  
  输入：
  - `cv_text`: 简历文本
  - `job_description`: 职位 JD 文本

  输出（目前是假数据）：
  - `match_score`: 一个 0~1 之间的匹配分数
  - `summary`: 一段总结说明（后面会接到真 AI）

## 3. V0 的目标

- 前端可以把简历 + JD 文本发给 `/match/preview`
- 后端返回一个「结构稳定」的 JSON
- 以后只是不断升级这个 JSON 里的内容，而不是乱改接口形状
