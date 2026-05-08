FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# 使用官方PyPI镜像（海外加速）
RUN pip install --no-cache-dir -i https://pypi.python.org/simple -r requirements.txt

COPY app.py .
COPY static/ ./static/

EXPOSE 80

CMD ["python", "app.py"]