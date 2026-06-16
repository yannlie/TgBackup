# TgBackup

<div align="center">

**🚀 最强大的 Telegram 媒体备份工具**

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Docker Hub](https://img.shields.io/docker/v/yannlie/tgbackup?label=Docker%20Hub&logo=docker)](https://hub.docker.com/r/yannlie/tgbackup)
[![GitHub Release](https://img.shields.io/github/v/release/yannlie/TgBackup)](https://github.com/yannlie/TgBackup/releases)

**转发即下载 · 自动备份 · 多云盘支持 · 轻量简洁**

[快速开始](#-快速开始) · [功能特性](#-功能特性) · [使用文档](#-使用方式) · [配置指南](#-配置)

</div>

---

## ✨ 功能特性

### 🎯 核心功能

| 功能 | 说明 |
|------|------|
| **🚀 转发即下载** | 转发消息给 Bot 自动下载 - 零配置，超简单！ |
| **☁️ 多云盘支持** | 支持 OneDrive、Google Drive、阿里云盘等 60+ 云存储 |
| **📡 多频道监听** | 同时监听多个频道/群组，自动下载新消息 |
| **🔍 智能过滤** | 按日期、文件类型、大小、扩展名过滤 |
| **🤖 Bot 控制** | 核心命令完整控制所有功能 |
| **📁 灵活路径** | 自定义目录结构和文件命名规则 |
| **🐳 Docker 部署** | 一行命令部署，支持 amd64/arm64 |
| **🎯 轻量简洁** | Ponytail 优化，代码精简 65% |

### 🆕 v1.3 新功能

- ✅ **YAML 配置支持** - 更易读的配置格式
- ✅ **Rclone 集成** - 支持 60+ 云存储服务
- ✅ **下载过滤器** - 按条件自动过滤消息
- ✅ **路径自定义** - 灵活的文件组织方式
- ✅ **Ponytail 优化** - 代码精简 65%，更快更稳定

---

## 🚀 快速开始

### Docker 部署（推荐）

```bash
# 1. 创建配置目录
mkdir -p /docker/tgbackup/{config,downloads,sessions,logs}

# 2. 创建配置文件
cat > /docker/tgbackup/config/telegram_config.json << 'EOF'
{
  "api_id": YOUR_API_ID,
  "api_hash": "YOUR_API_HASH",
  "phone": "+86YOUR_PHONE",
  "bot_token": "YOUR_BOT_TOKEN",
  "admin_ids": [YOUR_USER_ID],
  "channels": [],
  "media_types": ["photo", "video", "document", "audio"]
}
EOF

# 3. 启动容器
docker run -d --name tgbackup \
  --restart unless-stopped \
  -v /docker/tgbackup/config:/app/config \
  -v /docker/tgbackup/downloads:/app/downloads \
  -v /docker/tgbackup/sessions:/app/sessions \
  -v /docker/tgbackup/logs:/app/logs \
  yannlie/tgbackup:latest

# 4. 查看日志
docker logs -f tgbackup
```

### 获取配置参数

1. **API ID/Hash**: 访问 https://my.telegram.org/apps
2. **Bot Token**: 与 [@BotFather](https://t.me/BotFather) 对话创建 Bot
3. **User ID**: 与 [@userinfobot](https://t.me/userinfobot) 对话获取

---

## 📖 使用方式

### 方式 1: 转发下载（最简单）

```
1. 启动 Bot
2. 转发任意消息（视频/图片/文档）给 Bot
3. 自动下载！✅
```

### 方式 2: 频道监听（自动化）

```bash
# 编辑配置文件
nano /docker/tgbackup/config/telegram_config.json
```

```json
{
  "channels": [
    {
      "chat_id": "@channel_name",
      "last_read_message_id": 0,
      "download_filter": "message_date >= 2024-01-01"
    }
  ]
}
```

```bash
# 重启容器
docker restart tgbackup
```

### 方式 3: Bot 命令（远程控制）

| 命令 | 说明 |
|------|------|
| `/start` | 显示欢迎消息 |
| `/help` | 查看所有命令 |
| `/status` | 查看下载统计 |
| `/list` | 列出所有频道 |
| `/pause` | 暂停监听 |
| `/resume` | 恢复监听 |
| `/clear` | 清理缓存 |
| `/config` | 查看配置 |

---

## ☁️ 云盘配置

### OneDrive / Google Drive / 阿里云盘（Rclone）

**推荐使用 Rclone - 支持 60+ 云存储！**

#### 1. 安装 Rclone

```bash
curl https://rclone.org/install.sh | sudo bash
```

#### 2. 配置云盘

```bash
rclone config
```

**配置 OneDrive 示例：**
```
n) New remote
name> onedrive
Storage> onedrive
client_id> [回车]
client_secret> [回车]
region> 1
# 按提示授权...
```

**配置阿里云盘示例：**
```
n) New remote
name> aliyun
Storage> aliyundrive
token> [从阿里云盘获取]
```

#### 3. 测试连接

```bash
rclone lsd onedrive:
rclone mkdir onedrive:/TgBackup
```

#### 4. 更新配置

```json
{
  "upload_rclone": {
    "enable": true,
    "remote_dir": "onedrive:/TgBackup",
    "before_upload_zip": false,
    "after_upload_delete": false
  }
}
```

#### 5. 重启容器（挂载 rclone 配置）

```bash
docker run -d --name tgbackup \
  --restart unless-stopped \
  -v /docker/tgbackup/config:/app/config \
  -v /docker/tgbackup/downloads:/app/downloads \
  -v /docker/tgbackup/sessions:/app/sessions \
  -v /docker/tgbackup/logs:/app/logs \
  -v /root/.config/rclone:/root/.config/rclone:ro \
  yannlie/tgbackup:latest
```

**支持的云存储：**
- OneDrive
- Google Drive
- Dropbox
- 阿里云盘
- 百度网盘
- 天翼云盘
- Amazon S3
- 以及 60+ 更多...

---

## ⚙️ 配置

### 基础配置（JSON）

```json
{
  "api_id": 12345678,
  "api_hash": "your_api_hash",
  "phone": "+8612345678900",
  "bot_token": "your_bot_token",
  "admin_ids": [123456789],
  
  "channels": [],
  "media_types": ["photo", "video", "document", "audio"],
  "file_size_limit": 2147483648,
  "extensions_whitelist": [],
  "extensions_blacklist": [".exe", ".bat"]
}
```

### 高级配置（YAML）

**推荐使用 YAML - 更易读！**

创建 `config/telegram_config.yaml`:

```yaml
# Telegram 凭证
api_id: 12345678
api_hash: "your_api_hash"
phone: "+8612345678900"
bot_token: "your_bot_token"
admin_ids:
  - 123456789

# 多频道配置
channels:
  - chat_id: "@channel1"
    last_read_message_id: 0
    download_filter: "message_date >= 2024-01-01"
  
  - chat_id: "@channel2"
    last_read_message_id: 0

# 文件路径自定义
file_path_prefix:
  - chat_title      # 频道名
  - media_datetime  # 日期

file_name_prefix:
  - message_id      # 消息ID
  - file_name       # 文件名

date_format: "%Y_%m"  # 2024_06

# 云盘上传
upload_rclone:
  enable: true
  remote_dir: "onedrive:/TgBackup"
  before_upload_zip: false
  after_upload_delete: false
```

### 配置选项说明

| 选项 | 说明 | 示例 |
|------|------|------|
| `api_id` | Telegram API ID | `12345678` |
| `api_hash` | Telegram API Hash | `"abc123..."` |
| `phone` | 登录手机号 | `"+8612345678900"` |
| `bot_token` | Bot Token | `"123:ABC..."` |
| `admin_ids` | 管理员 User ID 列表 | `[123456789]` |
| `channels` | 监听的频道列表 | 见示例 |
| `media_types` | 下载的媒体类型 | `["photo", "video"]` |
| `file_size_limit` | 文件大小限制（字节） | `2147483648` (2GB) |
| `extensions_whitelist` | 扩展名白名单 | `[".mp4", ".jpg"]` |
| `extensions_blacklist` | 扩展名黑名单 | `[".exe"]` |
| `download_filter` | 下载过滤器表达式 | 见下方 |

### 下载过滤器

```yaml
download_filter: "message_date >= 2024-01-01 and file_size < 10485760"
```

**支持的条件：**
- `message_date >= 2024-01-01` - 日期范围
- `message_id > 1000` - 消息 ID
- `file_size < 10485760` - 文件大小（字节）

---

---

## 🔧 常见问题

### Q: 如何获取频道 ID？

**方法 1：使用 Web Telegram**
1. 访问 https://web.telegram.org/?legacy=1#/im
2. 打开频道，查看 URL：
   - `p=@channel_name` → 使用 `@channel_name`
   - `p=c1234567890` → 使用 `-1001234567890`

**方法 2：使用 Bot**
1. 与 [@username_to_id_bot](https://t.me/username_to_id_bot) 对话
2. 转发频道消息或发送频道链接

### Q: 下载的文件在哪里？

Docker 部署：`/docker/tgbackup/downloads/`

本地部署：`./downloads/`

### Q: 如何更新到最新版？

```bash
docker pull yannlie/tgbackup:latest
docker stop tgbackup && docker rm tgbackup
# 重新运行 docker run 命令
```

### Q: 转发视频提示"文件已存在或不符合过滤条件"？

检查配置文件中的 `media_types` 是否包含 `"video"`：

```json
{
  "media_types": ["photo", "video", "document", "audio"]
}
```

### Q: OneDrive Token 过期怎么办？

推荐切换到 Rclone（更稳定）：

参考 [云盘配置](#️-云盘配置)

---

## 📂 项目结构

```
TgBackup/
├── telegram_downloader.py        # 核心下载器
├── telegram_bot_controller.py    # Bot 控制器
├── config_loader.py              # 配置加载器 (优化: 141→117行)
├── path_generator.py             # 路径生成器 (优化: 188→147行)
├── download_filter.py            # 下载过滤器 (优化: 136→92行)
├── rclone_uploader.py            # Rclone 上传器
├── tg_to_onedrive.py             # OneDrive 上传器
├── utils.py                      # 工具函数 (新增)
├── config/
│   └── telegram_config.json      # 配置文件
└── requirements.txt              # Python 依赖
```

**Ponytail 优化**: 应用"最好的代码是你从未写过的代码"理念，精简 65% 代码

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📜 更新日志

### v1.3.0 (2024-06-16)

**重大更新 - 借鉴优秀开源项目 + Ponytail 优化**

**新功能：**
- ✅ YAML 配置支持（更易读）
- ✅ Rclone 云盘支持（60+ 云存储）
- ✅ 多频道数组配置
- ✅ 文件路径自定义
- ✅ 下载过滤器（按日期/ID/大小）

**Ponytail 优化：**
- ✅ 代码精简 65%（减少 420 行）
- ✅ 移除冗余 Web 监控（Bot 已有 /status）
- ✅ 简化配置加载器（标准库替代）
- ✅ 简化路径生成器（函数替代类）
- ✅ 简化下载过滤器（operator 模块）
- ✅ 统一工具函数（utils.py）
- ✅ 移除 Flask 依赖

**Bug 修复：**
- ✅ 修复视频过滤 Bug
- ✅ 修复 /clear 内存清理 Bug
- ✅ 修复配置加载路径问题

### v1.2.0

- ✅ 转发下载功能
- ✅ Bot 命令控制
- ✅ OneDrive 上传
- ✅ 多频道监听

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- 感谢 [tangyoha/telegram_media_downloader](https://github.com/tangyoha/telegram_media_downloader) 提供的优秀设计思路
- 感谢 [Telethon](https://github.com/LonamiWebs/Telethon) 提供的 Telegram 客户端库
- 感谢 [Rclone](https://rclone.org/) 提供的云存储同步工具

---

<div align="center">

**⭐ 如果觉得有用，请给个 Star！**

Made with ❤️ by [yannlie](https://github.com/yannlie)

</div>
