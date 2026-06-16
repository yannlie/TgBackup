# 快速开始

5 分钟快速部署 TgBackup！

## 🎯 准备工作

### 1. 获取 Telegram API

访问 https://my.telegram.org/apps

1. 使用你的手机号登录
2. 点击 "API development tools"
3. 创建应用，获得：
   - `api_id`（数字）
   - `api_hash`（字符串）

### 2. 创建 Telegram Bot

与 [@BotFather](https://t.me/BotFather) 对话：

```
/newbot
→ 输入 Bot 名称（如：My TgBackup Bot）
→ 输入 Bot 用户名（如：mytgbackup_bot）
→ 获得 bot_token（如：123456:ABC-DEF...）
```

### 3. 获取你的 User ID

与 [@userinfobot](https://t.me/userinfobot) 对话：

```
/start
→ 获得你的 User ID（如：123456789）
```

---

## 🚀 部署

### 方式 1: Docker（推荐）

```bash
# 1. 拉取镜像
docker pull yannlie/tgbackup:latest

# 2. 创建目录
mkdir -p ~/tgbackup/{config,downloads,sessions,logs}
cd ~/tgbackup

# 3. 创建配置文件
cat > config/telegram_config.json << 'EOF'
{
  "api_id": 12345678,
  "api_hash": "your_api_hash_here",
  "phone": "+8613800138000",
  "channels": [],
  "download_path": "./downloads",
  "media_types": ["photo", "video", "document", "audio"],
  "file_size_limit": 2147483648,
  "auto_upload": false,
  "bot_token": "123456:ABC-DEF...",
  "admin_ids": [123456789]
}
EOF

# 4. 编辑配置
nano config/telegram_config.json
# 填入你的 api_id, api_hash, phone, bot_token, admin_ids

# 5. 首次登录（获取 session）
docker run -it --rm \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/sessions:/app/sessions \
  yannlie/tgbackup:latest python telegram_downloader.py

# 输入验证码后按 Ctrl+C 退出

# 6. 启动服务（使用 Bot 控制）
docker run -d \
  --name tgbackup \
  --restart unless-stopped \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/sessions:/app/sessions \
  -v $(pwd)/logs:/app/logs \
  yannlie/tgbackup:latest

# 7. 查看日志
docker logs -f tgbackup
```

### 方式 2: docker-compose

```bash
# 1. 创建目录
mkdir -p ~/tgbackup/{config,downloads,sessions,logs}
cd ~/tgbackup

# 2. 创建 docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  tgbackup:
    image: yannlie/tgbackup:latest
    container_name: tgbackup
    restart: unless-stopped
    volumes:
      - ./config:/app/config
      - ./downloads:/app/downloads
      - ./sessions:/app/sessions
      - ./logs:/app/logs
    environment:
      - TZ=Asia/Shanghai
EOF

# 3. 创建配置（同上）

# 4. 首次登录
docker-compose run --rm tgbackup python telegram_downloader.py

# 5. 启动服务
docker-compose up -d

# 6. 查看日志
docker-compose logs -f
```

---

## ✅ 验证安装

### 1. 检查容器状态

```bash
docker ps
# 应该看到 tgbackup 容器在运行
```

### 2. 查看日志

```bash
docker logs tgbackup
# 应该看到 "Bot 控制器已启动"
```

### 3. 测试 Bot

在 Telegram 中：
1. 搜索你的 Bot（用户名）
2. 点击 "Start" 或发送 `/start`
3. 应该收到欢迎消息

---

## 🎉 开始使用

### 转发下载（最简单）

1. 在任何聊天中，找到一个包含媒体的消息
2. 长按消息 → 转发 → 选择你的 Bot
3. Bot 会自动下载该媒体文件！

### 浏览历史

```
/browse @channel_name
```

Bot 会显示该频道最近的媒体消息列表

### 精确下载

```
/download 12345
```

下载指定消息 ID 的媒体

---

## 📂 文件位置

| 目录 | 内容 |
|------|------|
| `config/` | 配置文件 |
| `downloads/` | 下载的文件 |
| `sessions/` | Telegram session 文件 |
| `logs/` | 日志文件 |

---

## 🔧 常用命令

```bash
# 查看日志
docker logs -f tgbackup

# 重启服务
docker restart tgbackup

# 停止服务
docker stop tgbackup

# 更新到最新版本
docker pull yannlie/tgbackup:latest
docker stop tgbackup
docker rm tgbackup
# 然后重新 run

# 进入容器调试
docker exec -it tgbackup bash
```

---

## ❓ 遇到问题？

- 📖 查看 [常见问题](FAQ.md)
- 📖 查看 [常见错误](Common-Errors.md)
- 🐛 [提交 Issue](https://github.com/yannlie/TgBackup/issues)

---

## 下一步

- 📖 [Bot 命令大全](Bot-Commands.md) - 学习所有命令
- 📖 [配置指南](Configuration-Guide.md) - 详细配置说明
- 📖 [OneDrive 配置](OneDrive-Setup.md) - 启用云端备份

---

**🎊 恭喜！你已经成功部署 TgBackup！**
