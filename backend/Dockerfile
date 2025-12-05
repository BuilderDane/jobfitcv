FROM public.ecr.aws/lambda/python:3.11

# 复制依赖文件
COPY requirements.txt /var/task/

RUN pip install --upgrade pip && \
    pip install -r /var/task/requirements.txt

# 只复制我们真正需要的代码
COPY main.py /var/task/
COPY db.py /var/task/
COPY schemas.py /var/task/
COPY models.py /var/task/
COPY repositories /var/task/repositories
COPY services /var/task/services

# Lambda 入口
# 对于 AWS Lambda Python 容器镜像，使用环境变量指定 handler
ENV _HANDLER=main.handler
CMD ["main.handler"]