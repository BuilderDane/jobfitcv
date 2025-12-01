# JobFitCV - Match Preview API 设计说明（V0）

## 1. 接口目的（Purpose）

提供一个 **快速预览** CV 与 Job Description 匹配度的接口，用于：
- 给用户一个直观的匹配分数（match_score）
- 点出主要优势（strengths）
- 点出明显缺口 / 风险（gaps）
- 提供可操作的优化建议（suggestions）

这个接口不负责「用户登录」「存储数据」，只做一件事：
> 输入 CV 文本 + JD 文本 → 输出结构化的匹配分析结果。

从系统设计角度看，它是一个 **“匹配分析服务（matching service）”** 的对外入口。

---

## 2. 请求与响应结构（Contract）

### 请求（Request）

- Method: `POST`
- Path: `/match/preview`
- Body（JSON）：

```json
{
  "cv_text": "string, CV 的纯文本内容",
  "job_description": "string, JD 的纯文本内容"
}
