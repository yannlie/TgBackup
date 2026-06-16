# Telegram Media Downloader with OneDrive Auto Upload

一个强大的 Telegram 媒体自动下载和备份工具，支持实时监听频道/群组消息，自动下载媒体文件并上传到 OneDrive。

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)

## 🎯 核心特性

### 自动化下载
- 🔄 **实时监听** - 监听多个 Telegram 频道/群组，新消息实时响应
- 📥 **智能下载** - 自动下载照片、视频、文档、音频等所有媒体类型
- 🎯 **灵活过滤** - 按文件类型、大小、扩展名精确过滤
- 📁 **分类存储** - 按频道/群组自动分类，目录结构清晰

### 自动化备份
- ☁️ **OneDrive 集成** - 下载完成自动上传到 OneDrive
- 🚀 **大文件支持** - 智能分块上传，支持最大 250GB 文件
- 🔄 **断点续传** - 基于文件哈希的智能去重
- 🗑️ **空间管理** - 可选上传后自动删除本地文件

### 远程控制
- 🤖 **Bot 控制** - 通过 Telegram Bot 随时随地远程管理
- 📊 **实时监控** - 查看下载统计、运行状态
- ⚙️ **动态配置** - 远程添加/移除频道，暂停/恢复下载

### 生产就绪
- 🐳 **Docker 支持** - 完整的容器化部署方案
- 📝 **详细日志** - 完整的操作日志和错误追踪
- 🔧 **易于部署** - 一键部署脚本，开箱即用

---

## 📋 目录

- [快速开始](#-快速开始)
- [安装部署](#-安装部署)
  - [方式 1: Docker 部署（推荐）](#方式-1-docker-部署推荐)
  - [方式 2: Python 直接运行](#方式-2-python-直接运行)
- [配置说明](#-配置说明)
  - [Telegram 配置](#1-telegram-配置)
  - [OneDrive 配置](#2-onedrive-配置)
  - [高级配置](#3-高级配置)
- [Bot 远程控制](#-bot-远程控制)
- [使用场景](#-使用场景)
- [常见问题](#-常见问题)
- [项目架构](#-项目架构)

---

## 🚀 快速开始

### 前置要求

- Python 3.8+ 或 Docker
- Telegram 账号
- Microsoft 账号（用于 OneDrive）

### 最快 5 分钟部署

```bash
# 1. 克隆项目
git clone https://github.com/yannlie/tg-to-onedrive-uploader.git
cd tg-to-onedrive-uploader

# 2. 运行部署脚本
# Linux/macOS
bash deploy.sh

# Windows
deploy.bat
```

脚本会引导你完成：
1. ✅ 依赖检查和安装
2. ✅ 配置文件创建
3. ✅ Telegram 登录
4. ✅ 服务启动

---

## 📦 安装部署

### 方式 1: Docker 部署（推荐）

Docker 部署适合服务器长期运行，支持自动重启和资源管理。

#### 1.1 准备配置文件

```bash
# 复制配置模板
cp telegram_config.example.json telegram_config.json
cp onedrive_config.example.json onedrive_config.json

# 编辑配置（参考配置说明章节）
nano telegram_config.json
```

#### 1.2 构建镜像

```bash
docker build -t tg-downloader .
```

#### 1.3 首次登录

首次运行需要登录 Telegram 获取 session：

```bash
docker run -it --rm \
  -v $(pwd)/telegram_config.json:/app/config/telegram_config.json \
  -v $(pwd)/sessions:/app/sessions \
  tg-downloader python telegram_downloader.py
```

按提示输入手机验证码，登录成功后按 `Ctrl+C` 退出。

#### 1.4 启动服务

```bash
# 使用 docker-compose（推荐）
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

#### 1.5 常用命令

```bash
# 查看容器状态
docker-compose ps

# 重启服务
docker-compose restart

# 进入容器调试
docker-compose exec telegram-downloader bash

# 查看实时日志
docker-compose logs -f --tail=100
```

**详细 Docker 文档**: 参考 [DOCKER.md](DOCKER.md)

---

### 方式 2: Python 直接运行

适合开发测试或本地使用。

#### 2.1 安装依赖

```bash
# 安装 Telegram 下载器依赖
pip install -r requirements_telegram.txt

# 安装 OneDrive 上传器依赖
pip install -r requirements.txt
```

#### 2.2 配置文件

```bash
# 复制模板
cp telegram_config.example.json telegram_config.json
cp onedrive_config.example.json onedrive_config.json

# 编辑配置
nano telegram_config.json
```

#### 2.3 运行程序

**选项 A: 使用启动向导**
```bash
python start.py
```

**选项 B: 直接运行下载器**
```bash
python telegram_downloader.py
```

**选项 C: 启用 Bot 控制**
```bash
python telegram_bot_controller.py
```

---

## ⚙️ 配置说明

### 1. Telegram 配置

#### 1.1 获取 API 凭据

1. 访问 https://my.telegram.org/apps
2. 登录你的 Telegram 账号
3. 点击 "Create Application"
4. 填写应用信息（随意填写）
5. 获取 `api_id` 和 `api_hash`

#### 1.2 配置文件结构

**telegram_config.json**:

```json
{
  "api_id": "12345678",
  "api_hash": "abcdef1234567890abcdef1234567890",
  "phone": "+8613800138000",
  
  "channels": [
    "@channel_username",
    "https://t.me/joinchat/xxxxx",
    -1001234567890
  ],
  
  "download_path": "./downloads",
  "media_types": ["photo", "video", "document", "audio"],
  "file_size_limit": 2147483648,
  "extensions_whitelist": [],
  "extensions_blacklist": [".exe", ".bat", ".cmd"],
  "auto_upload": true,
  "delete_after_upload": false,
  
  "bot_token": "123456:ABC-DEF...",
  "admin_ids": [123456789]
}
```

#### 1.3 配置项说明

| 配置项 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `api_id` | 数字 | ✅ | Telegram API ID |
| `api_hash` | 字符串 | ✅ | Telegram API Hash |
| `phone` | 字符串 | ✅ | 手机号（国际格式：+86...） |
| `channels` | 数组 | ✅ | 监听的频道/群组列表 |
| `download_path` | 字符串 | ❌ | 下载目录（默认：./downloads） |
| `media_types` | 数组 | ❌ | 下载的媒体类型 |
| `file_size_limit` | 数字 | ❌ | 文件大小限制（bytes，默认 2GB） |
| `extensions_whitelist` | 数组 | ❌ | 扩展名白名单（留空不限制） |
| `extensions_blacklist` | 数组 | ❌ | 扩展名黑名单 |
| `auto_upload` | 布尔 | ❌ | 是否自动上传 OneDrive（默认 true） |
| `delete_after_upload` | 布尔 | ❌ | 上传后删除本地文件（默认 false） |
| `bot_token` | 字符串 | ❌ | Bot Token（启用 Bot 控制） |
| `admin_ids` | 数组 | ❌ | Bot 管理员 User ID 列表 |

#### 1.4 频道格式说明

支持三种格式：

```json
{
  "channels": [
    "@channel_username",           // 公开频道用户名
    "https://t.me/joinchat/xxx",   // 邀请链接
    -1001234567890                 // 频道 Chat ID（数字）
  ]
}
```

**如何获取频道 ID**:
1. 转发频道消息给 @userinfobot
2. Bot 会返回频道的 Chat ID

---

### 2. OneDrive 配置

#### 2.1 创建 Azure 应用

1. 访问 [Azure 应用注册](https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade)
2. 点击「新注册」
3. 填写信息:
   - **名称**: 随意（如 "TG_OneDrive_Uploader"）
   - **账户类型**: 选择「任何组织目录中的账户和个人 Microsoft 账户」
   - **重定向 URI**: 选择「Web」，填写 `http://localhost:8080`
4. 记录「应用程序(客户端) ID」

#### 2.2 创建客户端密码

1. 进入应用 → 左侧「证书和密码」
2. 点击「新客户端密码」
3. 描述随意填，过期时间建议「24 个月」
4. **立即复制「值」**（离开后无法再查看）

#### 2.3 添加 API 权限

1. 左侧「API 权限」→「添加权限」
2. 选择「Microsoft Graph」→「委托的权限」
3. 搜索并勾选:
   - `Files.ReadWrite.All`
   - `offline_access`
4. 点击「添加权限」

#### 2.4 获取 Refresh Token

```bash
# 编辑脚本填入 Client ID 和 Secret
nano get_refresh_token.py

# 运行获取 token
python get_refresh_token.py
```

浏览器会自动打开授权页面，登录并授权后，`onedrive_config.json` 会自动生成。

#### 2.5 OneDrive 配置文件

**onedrive_config.json**:

```json
{
  "client_id": "your-client-id",
  "client_secret": "your-client-secret",
  "refresh_token": "your-refresh-token",
  "base_path": "/TG_Media",
  "chunk_size": 10,
  "min_stable_time": 5
}
```

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `client_id` | Azure 应用客户端 ID | - |
| `client_secret` | Azure 应用客户端密码 | - |
| `refresh_token` | OneDrive 刷新令牌 | - |
| `base_path` | OneDrive 存储路径 | /TG_Media |
| `chunk_size` | 分块上传大小（MB） | 10 |
| `min_stable_time` | 文件稳定时间（秒） | 5 |

---

### 3. 高级配置

#### 3.1 过滤规则

**只下载视频**:
```json
{
  "media_types": ["video"],
  "extensions_whitelist": [".mp4", ".mkv", ".avi"]
}
```

**排除大于 1GB 的文件**:
```json
{
  "file_size_limit": 1073741824
}
```

**只下载图片和小视频**:
```json
{
  "media_types": ["photo", "video"],
  "file_size_limit": 104857600
}
```

#### 3.2 存储策略

**上传后自动删除本地文件**:
```json
{
  "auto_upload": true,
  "delete_after_upload": true
}
```

**只下载不上传**:
```json
{
  "auto_upload": false
}
```

#### 3.3 目录结构

下载的文件按频道自动分类：

```
downloads/
├── 频道A/
│   ├── photo_123456_20240615_143022.jpg
│   └── video_123457_20240615_143045.mp4
├── 频道B/
│   └── document_123458_20240615_143100.pdf
└── 群组C/
    └── audio_123459_20240615_143130.mp3
```

上传到 OneDrive 会保留此结构：

```
OneDrive:/TG_Media/
├── 频道A/
├── 频道B/
└── 群组C/
```

---

## 🤖 Bot 远程控制

通过 Telegram Bot 可以随时随地远程管理下载器。

### 配置 Bot

#### 1. 创建 Bot

与 @BotFather 对话：

```
/newbot
```

按提示完成，获得 Bot Token，格式如：`123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`

#### 2. 获取 User ID

与 @userinfobot 对话，它会返回你的 User ID

#### 3. 配置文件

在 `telegram_config.json` 中添加：

```json
{
  "bot_token": "123456:ABC-DEF...",
  "admin_ids": [123456789, 987654321]
}
```

支持多个管理员。

#### 4. 启动 Bot 控制器

```bash
# Python
python telegram_bot_controller.py

# Docker
docker-compose up -d
```

### Bot 命令

| 命令 | 功能 | 示例 |
|------|------|------|
| `/start` | 显示帮助信息 | `/start` |
| `/status` | 查看运行状态 | `/status` |
| `/stats` | 查看统计信息 | `/stats` |
| `/list` | 列出所有监听频道 | `/list` |
| `/add` | 添加监听频道 | `/add @new_channel` |
| `/remove` | 移除监听频道 | `/remove @old_channel` |
| `/pause` | 暂停下载 | `/pause` |
| `/resume` | 恢复下载 | `/resume` |
| `/config` | 查看当前配置 | `/config` |

### 使用示例

```
你: /status
Bot: 📊 系统状态
     
     状态: ✅ 运行中
     监听频道: 3 个
     运行时间: 运行中

你: /stats
Bot: 📈 统计信息
     
     ✅ 已下载: 156
     ☁️ 已上传: 152
     ❌ 失败: 4
     ⏭️ 跳过: 23
     📦 总下载: 3.2 GB

你: /add @new_channel
Bot: ✅ 已添加: 新频道
```

---

## 💡 使用场景

### 场景 1: 自动备份资源频道

**需求**: 自动备份某资源频道的所有视频到 OneDrive

**配置**:
```json
{
  "channels": ["@resource_channel"],
  "media_types": ["video"],
  "auto_upload": true,
  "delete_after_upload": true
}
```

**效果**: 频道发布新视频 → 自动下载 → 上传 OneDrive → 删除本地，全程自动化。

---

### 场景 2: 多频道图片收集

**需求**: 收集多个摄影频道的图片，本地存储

**配置**:
```json
{
  "channels": ["@photo_channel1", "@photo_channel2", "@photo_channel3"],
  "media_types": ["photo"],
  "auto_upload": false
}
```

**效果**: 自动下载所有频道的图片，按频道分类存储到本地。

---

### 场景 3: 服务器长期运行

**需求**: 在服务器上 24/7 运行，远程管理

**部署**:
```bash
docker-compose up -d
```

**配置**:
```json
{
  "bot_token": "...",
  "admin_ids": [your_id],
  "auto_upload": true
}
```

**效果**: 服务器自动运行，通过 Bot 随时查看状态和管理。

---

### 场景 4: 大文件自动分流

**需求**: 下载大文件到本地，小文件上传 OneDrive

**配置**:
```json
{
  "file_size_limit": 2147483648,
  "auto_upload": true
}
```

在 `onedrive_config.json` 中:
```json
{
  "min_file_size": 0,
  "max_file_size": 524288000
}
```

**效果**: 超过 500MB 的文件只下载不上传，小文件自动备份到云端。

---

## ❓ 常见问题

### Q1: 提示 "Phone number is not registered"？

**A**: 你的手机号还未注册 Telegram。请先在手机上注册 Telegram 账号。

---

### Q2: 如何获取频道 ID？

**A**: 有两种方法：

1. **使用 Bot**:
   - 转发频道消息给 @userinfobot
   - Bot 会返回频道 Chat ID

2. **使用代码**:
   ```python
   from telethon import TelegramClient
   
   client = TelegramClient('session', api_id, api_hash)
   
   async def get_id():
       await client.start()
       entity = await client.get_entity('@channel_username')
       print(entity.id)
   
   client.loop.run_until_complete(get_id())
   ```

---

### Q3: 如何监听私有频道？

**A**: 
1. 必须先加入该私有频道/群组
2. 使用频道链接或 ID 添加到配置
3. 运行程序时会自动验证权限

---

### Q4: 下载速度慢怎么办？

**A**: Telegram 有速率限制。如果触发限流：
- 程序会自动等待并重试
- 建议使用稳定的网络连接
- 大文件下载需要耐心等待

---

### Q5: OneDrive 上传失败？

**A**: 检查以下几点：
1. Refresh Token 是否过期（重新运行 `get_refresh_token.py`）
2. OneDrive 存储空间是否充足
3. 网络连接是否正常
4. 查看日志文件 `tg_downloader.log` 了解详细错误

---

### Q6: 如何停止程序？

**Python 运行**:
```bash
# 按 Ctrl+C
```

**Docker 运行**:
```bash
docker-compose down
```

---

### Q7: 如何设置开机自启？

**Linux (systemd)**:
```bash
# 创建服务文件
sudo nano /etc/systemd/system/tg-downloader.service

# 启用服务
sudo systemctl enable tg-downloader
sudo systemctl start tg-downloader
```

**Docker**:
```yaml
# docker-compose.yml 中已配置
restart: unless-stopped
```

---

### Q8: 可以同时运行多个实例吗？

**A**: 可以，但需要：
1. 使用不同的配置文件
2. 使用不同的 session 文件名
3. 监听不同的频道（避免重复下载）

---

### Q9: 如何查看日志？

**Python 运行**:
```bash
tail -f tg_downloader.log
```

**Docker 运行**:
```bash
docker-compose logs -f
```

---

### Q10: 程序崩溃了怎么办？

**A**: 
1. 查看日志文件找到错误信息
2. 检查网络连接
3. 检查磁盘空间
4. 如果是 Token 过期，重新获取
5. Docker 会自动重启（`restart: unless-stopped`）

更多问题请查看 [FAQ.md](FAQ.md)

---

## 🏗️ 项目架构

### 核心模块

```
telegram_downloader.py       # Telegram 下载器主程序
├── TelegramConfig          # 配置管理
├── MediaDownloader         # 媒体下载器
├── UploadFilter            # 上传过滤器
└── TelegramDownloaderBot   # 主控制器

telegram_bot_controller.py  # Bot 远程控制器
├── BotController           # Bot 命令处理
└── 命令处理器               # /start, /status, /stats等

tg_to_onedrive.py           # OneDrive 上传器
├── Config                  # 配置管理
├── OneDriveUploader        # 上传器
├── UploadFilter            # 文件过滤
└── DownloadHandler         # 文件监听

get_refresh_token.py        # Token 获取工具
start.py                    # 启动向导
```

### 数据流

```
Telegram 频道
    ↓
监听新消息
    ↓
过滤检查 (类型/大小/扩展名)
    ↓
下载媒体文件
    ↓
按频道分类存储
    ↓
上传到 OneDrive
    ↓
(可选) 删除本地文件
```

### 技术栈

- **Telegram 客户端**: Telethon
- **文件监听**: Watchdog
- **HTTP 请求**: Requests
- **容器化**: Docker, Docker Compose
- **日志**: Python logging
- **异步**: asyncio

---

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。

---

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

参考 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

---

## 📞 联系方式

- **GitHub Issues**: https://github.com/yannlie/tg-to-onedrive-uploader/issues
- **仓库地址**: https://github.com/yannlie/tg-to-onedrive-uploader

---

## 🙏 致谢

- [Telethon](https://github.com/LonamiWebs/Telethon) - 优秀的 Telegram 客户端库
- [Watchdog](https://github.com/gorakhargosh/watchdog) - 文件系统监听库

---

**⭐ 如果这个项目对你有帮助，请给个 Star！**
