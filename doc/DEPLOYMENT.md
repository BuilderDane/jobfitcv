# front-end deployment
## 1.AWS Amplify Hosting 托管 Next.js 前端
- GitHub 仓库连起来，做到 git push → 自动构建、自动部署
- 在 Amplify 里配置 环境变量，让前端可以安全地调用后端 API（FastAPI / ECS / API Gateway）

## 2. 大致的配置步骤回顾
- 创建 Amplify App & 连接 GitHub
选择你的 JobFitCV 前端仓库 + 主分支（main / master）

- 构建配置（build settings）
Amplify 识别到是 Next.js，会自动生成一份 amplify.yml
这一步的核心：本地能成功 npm run build
