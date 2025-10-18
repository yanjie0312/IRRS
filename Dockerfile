FROM python:3.12-slim
WORKDIR /app

# 预装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# Cloud Run 会注入 PORT 环境变量；默认 8080 以防本地测试
ENV PORT=8080
EXPOSE 8080

# 用 gunicorn 托管 uvicorn（绑定 0.0.0.0:$PORT）
CMD ["gunicorn","-w","2","-k","uvicorn.workers.UvicornWorker","main:app","-b","0.0.0.0:${PORT}"]
