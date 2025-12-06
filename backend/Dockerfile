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

# Lambda 入口点配置
# 告诉 Lambda 运行哪个函数：main.py 文件中的 handler 变量
# 格式：文件名.变量名
CMD ["main.handler"]