# TgBackup

<div align="center">

**最简单、最灵活的 Telegram 媒体备份工具**

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Docker Hub](https://img.shields.io/docker/v/yannlie/tgbackup?label=Docker%20Hub&logo=docker)](https://hub.docker.com/r/yannlie/tgbackup)
[![Docker Pulls](https://img.shields.io/docker/pulls/yannlie/tgbackup?logo=docker)](https://hub.docker.com/r/yannlie/tgbackup)
[![GitHub Release](https://img.shields.io/github/v/release/yannlie/TgBackup)](https://github.com/yannlie/TgBackup/releases)

[English](#) | [中文文档](#)

</div>

---

## ✨ 核心特性

### 🚀 转发即下载
无需配置，直接转发消息给 Bot 自动下载 - 就这么简单！

### 📋 历史浏览
浏览频道历史消息，查看文件列表，精确选择下载

### ☁️ OneDrive 集成
自动上传到 OneDrive，支持大文件分块上传

### 🤖 Bot 远程控制
28+ 命令完整控制，随时随地管理

### 🐳 一键部署
Docker 一行命令部署，支持 amd64 和 arm64

---

## 🎯 三种使用方式

### 方式 1: 转发下载（最简单）

```
1. 启动 Bot
2. 转发消息给 Bot
3. 自动下载！
```

**适合**: 临时下载、零配置使用

### 方式 2: 浏览 + 精确下载（最灵活）

```
/browse @channel      # 浏览历史消息
/download 12345       # 下载指定消息
```

**适合**: 按需下载、节省空间

### 方式 3: 自动监听（最省心）

```json
{
  "channels": ["@channel1", "@channel2"]
}
```

**适合**: 24/7 自动备份

---

## ⚡ 快速开始

### 使用 Docker（推荐）

```bash
# 1. 拉取镜像
docker pull yannlie/tgbackup:latest

# 2. 准备配置
mkdir -p config downloads sessions
wget https://raw.githubusercontent.com/yannlie/TgBackup/main/telegram_config.example.json -O config/telegram_config.json

# 编辑配置文件，填入:
# - api_id 和 api_hash (从 https://my.telegram.org/apps 获取)
# - phone (你的手机号)
# - bot_token (从 @BotFather 获取)
# - admin_ids (与 @userinfobot 对话获取你的 ID)

# 3. 首次登录
docker run -it --rm \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/sessions:/app/sessions \
  yannlie/tgbackup:latest python telegram_downloader.py

# 输入验证码后按 Ctrl+C 退出

# 4. 启动服务
docker run -d --name tgbackup \
  --restart unless-stopped \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/sessions:/app/sessions \
  yannlie/tgbackup:latest

# 5. 开始使用
# 在 Telegram 中找到你的 Bot，转发任意媒体消息给它！
```

### 使用 docker-compose

```yaml
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
    environment:
      - TZ=Asia/Shanghai
```

```bash
docker-compose up -d
```

---

## 📱 Bot 命令速查

### 基础命令
```
/start              启动信息
/help               详细帮助
/status             运行状态
/stats              下载统计
```

### 下载控制
```
转发消息            直接下载媒体
/browse @channel    浏览历史消息
/download 12345     下载指定消息
/recent 10          查看最近下载
/history @ch 100    批量下载历史
```

### 频道管理
```
/list               列出频道
/add @channel       添加频道
/remove @channel    移除频道
/test @channel      测试连接
/info @channel      频道信息
```

### 系统管理
```
/pause              暂停下载
/resume             恢复下载
/disk               磁盘空间
/logs               查看日志
/config             查看配置
/backup             备份配置
```

---

## 💡 使用示例

### 场景 1: 临时下载文件

```
你在群里看到一个有用的视频

→ 转发给 Bot
→ Bot: "✅ 下载完成！文件: video.mp4，大小: 150MB"
```

### 场景 2: 浏览并选择下载

```
/browse @resource_channel

Bot: 显示最近 20 条消息列表
- 消息 12345: 🎥 Python教程.mp4 (200MB)
- 消息 12344: 📄 文档.pdf (5MB)
...

/download 12345

Bot: "✅ 下载完成！"
```

### 场景 3: 自动备份频道

```json
{
  "channels": ["@backup_channel"]
}
```

启动后自动监听，新消息自动下载并上传 OneDrive。

---

## 🎨 核心功能

### ✅ 媒体下载
- 支持照片、视频、文档、音频
- 文件大小/类型/扩展名过滤
- 智能去重，避免重复下载
- 断点续传

### ✅ OneDrive 集成
- 自动上传到 OneDrive
- 大文件分块上传（支持最大 250GB）
- 保留目录结构
- 可选上传后删除本地文件

### ✅ Bot 控制
- 28+ 命令完整控制
- 转发消息自动下载
- 历史消息浏览
- 精确消息下载
- 实时状态监控

### ✅ 灵活配置
- channels 可选（可为空）
- 多种下载方式
- 详细的过滤规则
- 完整的日志系统

---

## 📚 文档

- [快速开始](docs/Quick-Start.md)
- [Bot 命令大全](docs/Bot-Commands.md)
- [配置指南](docs/Configuration-Guide.md)
- [转发下载教程](docs/Forward-Download.md)
- [常见问题](FAQ.md)
- [开发路线图](ROADMAP.md)

---

## 🆚 为什么选择 TgBackup？

| 功能 | TgBackup | 其他工具 |
|------|----------|---------|
| **转发下载** | ✅ 原生支持 | ❌ 不支持 |
| **历史浏览** | ✅ 完整列表 | ❌ 仅批量 |
| **零配置使用** | ✅ channels 可选 | ❌ 必须配置 |
| **OneDrive 集成** | ✅ 原生支持 | ⚠️ 需要额外工具 |
| **Bot 控制** | ✅ 28+ 命令 | ⚠️ 功能简单 |
| **Docker 镜像** | ✅ 官方多平台 | ⚠️ 需自己构建 |
| **中文文档** | ✅ 完整详细 | ⚠️ 仅有 README |

---

## 🔧 配置说明

### 最小配置

```json
{
  "api_id": 12345678,
  "api_hash": "your_api_hash",
  "phone": "+8613800138000",
  "channels": [],
  "bot_token": "123456:ABC-DEF...",
  "admin_ids": [123456789]
}
```

### 配置项说明

| 配置项 | 必填 | 说明 |
|--------|------|------|
| `api_id` | ✅ | 从 https://my.telegram.org/apps 获取 |
| `api_hash` | ✅ | 从 https://my.telegram.org/apps 获取 |
| `phone` | ✅ | 你的手机号（国际格式：+86...） |
| `channels` | ❌ | 监听的频道列表（可为空） |
| `bot_token` | ⭐ | Bot Token，强烈推荐配置 |
| `admin_ids` | ⭐ | 管理员 User ID 列表 |

⭐ = 推荐配置，启用 Bot 远程控制功能

**详细配置**: 参考 [配置指南](../../wiki/配置指南)

---

## 🚀 高级功能

### OneDrive 自动上传

配置 `onedrive_config.json`：

```json
{
  "client_id": "your_client_id",
  "client_secret": "your_client_secret",
  "refresh_token": "your_refresh_token",
  "base_path": "/TG_Media"
}
```

获取 Token：
```bash
python get_refresh_token.py
```

**详细步骤**: 参考 [OneDrive 配置](../../wiki/OneDrive配置)

---

## 📊 项目状态

- ✅ 核心功能：完整
- ✅ Bot 控制：28+ 命令
- ✅ Docker 支持：多平台
- ✅ 文档：完整
- ✅ 测试：通过
- 🔄 持续更新中

---

## 🗺️ 开发路线图

### v1.2（当前）
- ✅ 转发下载功能
- ✅ 历史浏览
- ✅ 精确下载
- ✅ 统一配置

### v1.3（计划中）
- 🔄 Web 管理界面
- 🔄 邮件通知
- 🔄 多账号支持

**完整路线图**: [ROADMAP.md](ROADMAP.md)

---

## 🤝 参与贡献

欢迎贡献代码、报告问题或提出建议！

- [报告 Bug](../../issues/new?template=bug_report.md)
- [功能建议](../../issues/new?template=feature_request.md)
- [贡献指南](CONTRIBUTING.md)

---

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。

---

## 🙏 致谢

- [Telethon](https://github.com/LonamiWebs/Telethon) - 优秀的 Telegram 客户端库
- [Watchdog](https://github.com/gorakhargosh/watchdog) - 文件系统监听

---

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yannlie/TgBackup&type=Date)](https://star-history.com/#yannlie/TgBackup&Date)

---

<div align="center">

**如果这个项目对你有帮助，请给个 Star ⭐**

[GitHub](https://github.com/yannlie/TgBackup) · [Docker Hub](https://hub.docker.com/r/yannlie/tgbackup) · [问题反馈](../../issues)

</div>
