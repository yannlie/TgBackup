# Docker 部署指南

## 🐳 Docker 部署

### 快速开始

#### 1. 准备配置文件

```bash
# 复制配置模板
cp telegram_config.example.json telegram_config.json
cp onedrive_config.example.json onedrive_config.json

# 编辑配置文件
nano telegram_config.json
nano onedrive_config.json
```

**telegram_config.json 最小配置**：
```json
{
  "api_id": "12345678",
  "api_hash": "your_api_hash",
  "phone": "+8613800138000",
  "channels": ["@channel1"],
  "download_path": "/app/downloads",
  "auto_upload": true,
  "bot_token": "123456:ABC-DEF...",
  "admin_ids": [123456789]
}
```

#### 2. 构建镜像

```bash
docker build -t tg-downloader .
```

#### 3. 首次登录（获取 session）

```bash
# 临时运行容器进行首次登录
docker run -it --rm \
  -v $(pwd)/telegram_config.json:/app/config/telegram_config.json \
  -v $(pwd)/sessions:/app/sessions \
  tg-downloader python telegram_downloader.py

# 按提示输入验证码完成登录
# Ctrl+C 退出后，session 已保存
```

#### 4. 启动服务

```bash
# 使用 docker-compose（推荐）
docker-compose up -d

# 或使用 docker run
docker run -d \
  --name tg-downloader \
  --restart unless-stopped \
  -v $(pwd)/telegram_config.json:/app/config/telegram_config.json \
  -v $(pwd)/onedrive_config.json:/app/config/onedrive_config.json \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/sessions:/app/sessions \
  tg-downloader
```

### Docker Compose 使用

#### 启动服务
```bash
docker-compose up -d
```

#### 查看日志
```bash
# 实时日志
docker-compose logs -f

# 查看最近 100 行
docker-compose logs --tail=100
```

#### 停止服务
```bash
docker-compose down
```

#### 重启服务
```bash
docker-compose restart
```

#### 更新镜像
```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose up -d --build
```

### 目录结构

```
.
├── docker-compose.yml          # Docker Compose 配置
├── Dockerfile                  # Docker 镜像构建文件
├── telegram_config.json        # Telegram 配置（需创建）
├── onedrive_config.json        # OneDrive 配置（需创建）
├── downloads/                  # 下载目录（自动创建）
├── logs/                       # 日志目录（自动创建）
└── sessions/                   # Session 文件（自动创建）
    ├── bot_session.session
    └── downloader_session.session
```

### 配置说明

#### docker-compose.yml

**服务模式选择**：

1. **telegram-downloader**（主服务）
   - 监听频道并下载
   - 自动上传 OneDrive
   - 支持 Bot 控制

2. **onedrive-uploader**（可选服务）
   - 独立的目录监听上传器
   - 仅在需要时启用

```bash
# 启用可选服务
docker-compose --profile standalone up -d
```

#### 环境变量

在 `docker-compose.yml` 中可配置：

```yaml
environment:
  - TZ=Asia/Shanghai              # 时区
  - PYTHONUNBUFFERED=1            # Python 输出缓冲
  - LOG_LEVEL=INFO                # 日志级别
```

#### 资源限制

默认限制：
- CPU: 最大 2 核，预留 0.5 核
- 内存: 最大 2GB，预留 512MB

修改限制：
```yaml
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 4G
```

### 高级配置

#### 自定义网络

```yaml
networks:
  tg-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.25.0.0/16
```

#### 使用外部配置

```yaml
volumes:
  - /path/to/your/config:/app/config
  - /mnt/storage/downloads:/app/downloads
```

#### 多实例部署

```yaml
services:
  tg-downloader-1:
    build: .
    container_name: tg-downloader-1
    volumes:
      - ./config1:/app/config
      - ./downloads1:/app/downloads

  tg-downloader-2:
    build: .
    container_name: tg-downloader-2
    volumes:
      - ./config2:/app/config
      - ./downloads2:/app/downloads
```

### Bot 控制功能

#### 配置 Bot

1. 与 @BotFather 对话创建 Bot
2. 获取 Bot Token
3. 获取你的 User ID（使用 @userinfobot）
4. 在 `telegram_config.json` 添加：

```json
{
  "bot_token": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
  "admin_ids": [123456789]
}
```

5. 重启容器：
```bash
docker-compose restart
```

#### Bot 命令

与你的 Bot 对话，使用以下命令：

- `/start` - 显示帮助
- `/status` - 查看运行状态
- `/stats` - 查看统计信息
- `/list` - 列出监听频道
- `/add @channel` - 添加频道
- `/remove @channel` - 移除频道
- `/pause` - 暂停下载
- `/resume` - 恢复下载
- `/config` - 查看配置

### 故障排查

#### 查看容器状态
```bash
docker-compose ps
```

#### 查看详细日志
```bash
docker-compose logs -f telegram-downloader
```

#### 进入容器调试
```bash
docker-compose exec telegram-downloader bash

# 容器内检查
ls -la /app/config
cat /app/logs/tg_downloader.log
python -c "import telethon; print('OK')"
```

#### 常见问题

**1. 容器启动后立即退出**
```bash
# 查看退出原因
docker-compose logs telegram-downloader

# 常见原因：配置文件错误、权限问题
```

**2. 无法连接 Telegram**
```bash
# 检查网络
docker-compose exec telegram-downloader ping -c 3 telegram.org

# 可能需要配置代理
environment:
  - HTTP_PROXY=http://proxy:port
  - HTTPS_PROXY=http://proxy:port
```

**3. 文件下载后无法上传**
```bash
# 检查 OneDrive 配置
docker-compose exec telegram-downloader cat /app/config/onedrive_config.json

# 检查网络和 token
docker-compose logs telegram-downloader | grep -i "onedrive\|upload"
```

**4. Session 文件丢失**
```bash
# 确保 sessions 目录挂载正确
docker-compose down
rm -rf ./sessions/*
docker-compose up -d

# 重新登录
docker-compose exec -it telegram-downloader python telegram_downloader.py
```

### 性能优化

#### 1. 使用本地存储
```yaml
volumes:
  - /mnt/fast-ssd/downloads:/app/downloads
```

#### 2. 调整并发
```python
# 修改代码或通过环境变量
environment:
  - DOWNLOAD_WORKERS=5
```

#### 3. 日志轮转
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "5"
```

### 安全建议

1. **保护配置文件**
```bash
chmod 600 telegram_config.json onedrive_config.json
```

2. **使用 secrets（生产环境）**
```yaml
secrets:
  telegram_config:
    file: ./telegram_config.json
  onedrive_config:
    file: ./onedrive_config.json

services:
  telegram-downloader:
    secrets:
      - telegram_config
      - onedrive_config
```

3. **定期备份 session**
```bash
# 定时备份
crontab -e
0 2 * * * cp -r /path/to/sessions /backup/sessions-$(date +\%Y\%m\%d)
```

### 监控和维护

#### Prometheus 监控（可选）
```yaml
services:
  telegram-downloader:
    ports:
      - "8080:8080"  # Metrics 端口
```

#### 自动重启策略
```yaml
restart: unless-stopped  # 默认
# 或
restart: always
# 或
restart: on-failure:3
```

#### 健康检查
```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import os; exit(0 if os.path.exists('/app/logs/tg_downloader.log') else 1)"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### 升级指南

#### 平滑升级
```bash
# 1. 拉取最新代码
git pull

# 2. 备份配置和数据
cp -r downloads downloads.bak
cp -r sessions sessions.bak

# 3. 重新构建
docker-compose build

# 4. 重启服务
docker-compose up -d

# 5. 检查日志
docker-compose logs -f
```

#### 回滚
```bash
docker-compose down
git checkout <previous-commit>
docker-compose up -d --build
```

---

## 📊 生产部署示例

### 使用 Nginx 反向代理（如需 Web 界面）

```nginx
server {
    listen 80;
    server_name tg-downloader.yourdomain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 使用 systemd 管理

```ini
# /etc/systemd/system/tg-downloader.service
[Unit]
Description=Telegram Downloader
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/tg-downloader
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down

[Install]
WantedBy=multi-user.target
```

启用服务：
```bash
sudo systemctl enable tg-downloader
sudo systemctl start tg-downloader
```

---

需要其他配置或有问题请参考 [FAQ.md](FAQ.md)
