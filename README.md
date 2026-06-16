# TG Media to OneDrive 完整解决方案

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub Actions](https://github.com/yannlie/tg-to-onedrive-uploader/workflows/Python%20Code%20Quality/badge.svg)](https://github.com/yannlie/tg-to-onedrive-uploader/actions)

**完整的 Telegram 媒体下载 + OneDrive 自动上传解决方案**

## 🎯 两种使用模式

### 模式 1：Telegram 实时下载器（推荐！⭐）
**[telegram_downloader.py](telegram_downloader.py)** - 监听频道/群组，实时下载并自动上传到 OneDrive

✨ **特性**：
- 🔄 监听多个频道/群组的新消息
- 📥 自动下载照片、视频、文档、音频
- 🎯 按类型、大小、扩展名过滤
- 📁 按频道自动分类
- 🚀 下载完成自动上传 OneDrive
- 📖 [详细文档 →](TELEGRAM_README.md)

### 模式 2：目录监听上传器
**[tg_to_onedrive.py](tg_to_onedrive.py)** - 监听本地目录，文件下载完成后自动上传

✨ **特性**：
- 👀 监听本地下载目录
- ⏱️ 智能判断文件下载完成
- 📤 自动上传到 OneDrive
- 适合配合第三方下载工具使用

## ✨ 功能特性

### 核心功能
✅ **自动监听** - 实时检测下载目录的新文件  
✅ **智能判断** - 文件稳定后才上传（避免上传未完成的文件）  
✅ **大文件支持** - >4MB 自动分块上传，支持最大 250GB  
✅ **断点续传** - 自动重试失败的上传  
✅ **去重机制** - 基于文件哈希避免重复上传  
✅ **保留结构** - 自动保留子目录结构  
✅ **详细日志** - 完整的操作日志和统计信息

### 高级功能 (v2.0)
🎯 **文件过滤** - 按扩展名、大小过滤文件  
📊 **统计报告** - 实时上传统计（成功率、流量等）  
🗑️ **自动清理** - 上传成功后可选自动删除本地文件  
⚙️ **命令行参数** - 灵活的配置和运行选项  
🧪 **单元测试** - 完整的测试覆盖  
🤖 **CI/CD** - GitHub Actions 自动化

## 安装依赖

```bash
pip install watchdog requests urllib3
```

## 配置步骤

### 1. 注册 Azure 应用

1. 访问 [Azure 应用注册](https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade)
2. 点击「新注册」
   - 名称：随意填写（如 "TG_OneDrive_Uploader"）
   - 支持的账户类型：选择「任何组织目录(任何 Azure AD 目录 - 多租户)中的帐户和个人 Microsoft 帐户」
   - 重定向 URI：选择「Web」，填写 `http://localhost:8080`
3. 记录「应用程序(客户端) ID」（即 `CLIENT_ID`）

### 2. 创建客户端密码

1. 进入刚创建的应用 → 左侧菜单「证书和密码」
2. 点击「新客户端密码」
3. 描述随意填，过期时间建议选「24 个月」
4. **立即复制「值」**（即 `CLIENT_SECRET`），离开页面后无法再查看！

### 3. 添加 API 权限

1. 左侧菜单「API 权限」→ 点击「添加权限」
2. 选择「Microsoft Graph」→「委托的权限」
3. 搜索并勾选：
   - `Files.ReadWrite.All` - 完全访问用户文件
   - `offline_access` - 维护数据访问权限
4. 点击「添加权限」

### 4. 获取 Refresh Token

1. 编辑 `get_refresh_token.py`，填入刚才获取的 `CLIENT_ID` 和 `CLIENT_SECRET`

```python
CLIENT_ID = 'your_client_id_here'
CLIENT_SECRET = 'your_client_secret_here'
```

2. 运行脚本：

```bash
python get_refresh_token.py
```

3. 浏览器会自动打开授权页面，登录你的 Microsoft 账号并授权
4. 授权成功后，`onedrive_config.json` 会自动生成

### 5. 配置下载目录

编辑 `tg_to_onedrive.py`，修改监听目录：

```python
WATCH_PATH = 'd:/telegram_downloads'  # 改为你的 telegram_media_downloader 下载目录
```

## 使用方法

### 基本用法

```bash
# 使用默认配置
python tg_to_onedrive.py

# 指定配置文件
python tg_to_onedrive.py --config my_config.json

# 指定监听目录
python tg_to_onedrive.py --watch-path /path/to/downloads

# 上传成功后自动删除本地文件
python tg_to_onedrive.py --auto-delete

# 设置日志级别
python tg_to_onedrive.py --log-level DEBUG

# 查看帮助
python tg_to_onedrive.py --help
```

### 高级配置

在 `onedrive_config.json` 中添加更多选项：

```json
{
  "client_id": "你的客户端ID",
  "client_secret": "你的客户端密码",
  "refresh_token": "你的刷新令牌",
  "base_path": "/TG_Media",
  "watch_path": "d:/telegram_downloads",
  "chunk_size": 10,
  "min_stable_time": 5,
  "excluded_extensions": [".tmp", ".part", ".txt"],
  "min_file_size": 1048576,
  "max_file_size": 268435456000
}
```

**配置说明**：
- `base_path`: OneDrive 存储路径
- `watch_path`: 监听目录（可被命令行参数覆盖）
- `chunk_size`: 分块大小（MB），默认 10MB
- `min_stable_time`: 文件稳定时间（秒），默认 5 秒
- `excluded_extensions`: 排除的文件扩展名列表
- `min_file_size`: 最小文件大小（bytes），默认 0
- `max_file_size`: 最大文件大小（bytes），默认 250GB

程序会持续运行，监听下载目录的变化。

### 与 telegram_media_downloader 配合使用

1. 下载并配置 [telegram_media_downloader](https://github.com/tangyoha/telegram_media_downloader)

2. 在其配置文件中设置下载目录与本脚本的 `WATCH_PATH` 一致

3. 先启动 `tg_to_onedrive.py`，再启动 `telegram_media_downloader`

4. 当 TG 有新文件下载完成时，会自动上传到 OneDrive 的 `/TG_Media` 目录

## 配置说明

### onedrive_config.json

```json
{
  "client_id": "你的客户端ID",
  "client_secret": "你的客户端密码",
  "refresh_token": "你的刷新令牌",
  "base_path": "/TG_Media"
}
```

- `base_path`: OneDrive 中的存储目录，可修改为任意路径

### 日志文件

- `tg_to_onedrive.log`: 运行日志
- `uploaded_files.json`: 已上传文件记录（用于去重）

## 工作原理

```
┌─────────────────────────┐
│ telegram_media_downloader│
│   下载文件到本地         │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   Watchdog 监听器        │
│   检测文件创建/修改      │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   稳定性检测             │
│   (5秒无修改=下载完成)   │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   去重检查               │
│   (文件名+大小)          │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   OneDrive 上传          │
│   小文件: 直接上传       │
│   大文件: 分块上传       │
└─────────────────────────┘
```

## 常见问题

### Q: 授权失败，提示 redirect_uri 不匹配？
A: 确保 Azure 应用注册中的重定向 URI 完全是 `http://localhost:8080`（不能有多余斜杠）

### Q: 上传失败，提示 401 Unauthorized？
A: Token 可能已过期，删除 `onedrive_config.json` 重新运行 `get_refresh_token.py`

### Q: 文件还在下载中就开始上传了？
A: 可调整稳定时间，在 `DownloadHandler.__init__` 中修改 `min_stable_time`（默认 5 秒）

### Q: 想上传到 OneDrive 的不同目录？
A: 修改 `onedrive_config.json` 中的 `base_path`

### Q: 可以监听多个下载目录吗？
A: 可以，在 `main()` 函数中创建多个 `observer` 和 `handler`

## 高级功能

### 后台运行（Linux/macOS）

使用 `screen` 或 `tmux`：

```bash
screen -S tg_uploader
python tg_to_onedrive.py
# 按 Ctrl+A, D 退出 screen
```

### 开机自启动（Windows）

创建批处理文件 `start_uploader.bat`：

```batch
@echo off
cd /d "d:\vs code\1"
python tg_to_onedrive.py
```

将其快捷方式放到：`C:\Users\你的用户名\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`

### 开机自启动（Linux systemd）

创建服务文件 `/etc/systemd/system/tg-uploader.service`：

```ini
[Unit]
Description=TG to OneDrive Auto Uploader
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/script
ExecStart=/usr/bin/python3 /path/to/tg_to_onedrive.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启用服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable tg-uploader
sudo systemctl start tg-uploader
```

## 许可证

MIT License

---

**提示**: 搭配 [onedrive-cf-index-ng](https://github.com/lyc8503/onedrive-cf-index-ng) 可以实现在线浏览和分享上传的文件。
