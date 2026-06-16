FROM python:3.11-slim

LABEL maintainer="yannlie"
LABEL description="TgBackup - Telegram Media Backup Tool with OneDrive Support"

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt requirements_telegram.txt ./

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements_telegram.txt

# 复制应用代码
COPY telegram_downloader.py \
     telegram_bot_controller.py \
     tg_to_onedrive.py \
     get_refresh_token.py \
     ./

# 创建必要的目录
RUN mkdir -p /app/downloads /app/config /app/logs /app/sessions

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Shanghai

# 暴露端口（如果需要 Web 界面）
# EXPOSE 8080

# 数据卷
VOLUME ["/app/downloads", "/app/config", "/app/logs"]

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import os; exit(0 if os.path.exists('/app/logs/tg_downloader.log') else 1)"

# 默认命令
CMD ["python", "telegram_downloader.py"]
