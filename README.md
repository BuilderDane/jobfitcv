# JobFitCV

JobFitCV is an AI-powered CV–Job matching platform that helps job seekers understand role requirements, identify skill gaps, and generate tailored CVs and cover letters.

This project is built as a capstone transition project from Product Designer to Full-Stack AI Product Engineer, focusing on real system design, cloud architecture, and AI integration, not demo-level prototyping.

## Why This Project

Most AI CV tools:

- Rewrite text without explaining why
- Lack structure, transparency, and skill-gap analysis
- Are not designed as real, deployable systems

JobFitCV focuses on:

- Structured JD ↔ CV analysis
- Explainable AI outputs (diffs, gaps, strengths)
- Production-minded architecture
- End-to-end ownership: frontend, backend, cloud, and AI

## Core Features (MVP)

- **CV Parsing**: PDF / DOCX / TXT support
- **Job Description Analysis**: Structured requirement extraction
- **Structured Matching Output**:
  - Key JD requirements
  - Relevant CV experience
  - Gaps / mismatches
  - Potential strengths
- **AI-Generated Tailored CV**: Customized resume generation
- **Explainable Diff**: Added / modified / missing sections
- **Cover Letter Generation**: Automated cover letter creation
- **Growth Insights**: Recommendations on skills to learn next

## Tech Stack

### Frontend

- **Framework**: Next.js + TypeScript
- **Deployment**: AWS Amplify
- **Focus**: Clarity, editability, explainability

### Backend

- **Framework**: FastAPI (Python)
- **Development**: Local-first approach
- **Deployment**: AWS Lambda-based APIs (MVP stage)

### AI Layer

- **Approach**: LLM-based structured analysis
- **Process**: Multi-step reasoning (analysis → rewrite → diff)
- **Future**: Designed for agent-based orchestration

### Cloud (AWS)

This project intentionally uses AWS to demonstrate production readiness:

- **AWS Amplify**: Frontend CI/CD
- **AWS Lambda**: Backend API (MVP)
- **Amazon S3**: File storage (CVs, PDFs)
- **DynamoDB**: Task state & analysis results (MVP)
- **AWS Secrets Manager**: API keys management
- **CloudWatch**: Logging & monitoring

> **Note**: RDS / ECS / Fargate are intentionally not used in MVP to reduce complexity and cost during learning-by-doing.

## Environment Strategy

The system is designed with clear environment separation:

### Local

- FastAPI development server
- No cloud dependencies
- No database (or SQLite if needed)

### AWS Dev

- Lambda + DynamoDB + S3
- Used for real deployment practice

### Production (Future)

- Optional upgrade to RDS / ECS
- Only when real traffic or scale requires it

## Project Structure

```
jobfitcv/
├── backend/        # FastAPI backend
├── frontend/       # Next.js frontend
├── docs/           # Architecture, notes, decisions
├── .github/        # CI / workflows
├── README.md
└── DEPLOYMENT.md
```
