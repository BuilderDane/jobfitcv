# 1. 选一个和 Lambda 一样的 Python 运行环境（官方镜像）
FROM public.ecr.aws/lambda/python:3.11

# 2. 把依赖清单复制进去
COPY requirements.txt  .

# 3. 安装依赖到镜像里（注意：这里是在 Linux 里装，避免平台问题）
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 4. 把你的应用代码复制进去
COPY . .

# 5. 告诉 Lambda：入口函数在 main.py 里的 handler 变量
#    对应 Python 模块路径 "main.handler"
CMD ["main.handler"]