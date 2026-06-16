# 项目文件说明

## 📂 项目结构

```
tg-to-onedrive-uploader/
│
├── 📁 核心程序 (Python)
│   ├── telegram_downloader.py          # Telegram 媒体下载器（主程序）
│   ├── telegram_bot_controller.py      # Bot 远程控制器
│   ├── tg_to_onedrive.py              # OneDrive 自动上传器
│   ├── get_refresh_token.py           # OneDrive Token 获取工具
│   └── start.py                       # 启动向导
│
├── 📁 配置文件
│   ├── telegram_config.example.json    # Telegram 配置模板
│   └── onedrive_config.example.json    # OneDrive 配置模板
│
├── 📁 Docker 部署
│   ├── Dockerfile                      # Docker 镜像定义
│   ├── docker-compose.yml             # Docker Compose 编排
│   └── .dockerignore                  # Docker 忽略文件
│
├── 📁 部署脚本
│   ├── deploy.sh                      # Linux/macOS 一键部署
│   └── deploy.bat                     # Windows 一键部署
│
├── 📁 依赖管理
│   ├── requirements.txt               # OneDrive 上传器依赖
│   └── requirements_telegram.txt      # Telegram 下载器依赖
│
├── 📁 文档
│   ├── README.md                      # 主文档（使用指南）
│   ├── TELEGRAM_README.md             # Telegram 下载器详细文档
│   ├── DOCKER.md                      # Docker 部署详细指南
│   ├── FAQ.md                         # 常见问题解答
│   ├── CONTRIBUTING.md                # 贡献指南
│   ├── TEST_REPORT.md                 # 测试报告
│   └── PROJECT_STRUCTURE.md           # 本文件
│
├── 📁 测试
│   ├── test_uploader.py               # OneDrive 上传器单元测试
│   └── test_project.py                # 项目完整性测试
│
├── 📁 CI/CD (.github/workflows/)
│   ├── python-quality.yml             # 代码质量检查
│   ├── release.yml                    # 自动发布
│   └── update-deps.yml                # 依赖自动更新
│
└── 📁 其他
    ├── LICENSE                        # MIT 开源协议
    ├── .gitignore                     # Git 忽略文件
    └── push_to_github.bat             # Git 推送辅助脚本
```

---

## 📝 核心文件详解

### 1. telegram_downloader.py

**功能**: Telegram 媒体下载器主程序

**核心类**:
- `TelegramConfig` - 配置管理
- `MediaDownloader` - 媒体文件下载器
- `UploadFilter` - 文件过滤器
- `TelegramDownloaderBot` - 主控制器

**主要功能**:
- 监听多个频道/群组
- 自动下载媒体文件
- 文件类型过滤
- 自动上传 OneDrive
- 断点续传（去重）

**运行**:
```bash
python telegram_downloader.py
```

---

### 2. telegram_bot_controller.py

**功能**: Telegram Bot 远程控制器

**核心类**:
- `BotController` - Bot 命令处理器

**支持命令**:
- `/start` - 帮助信息
- `/status` - 查看状态
- `/stats` - 查看统计
- `/add` - 添加频道
- `/remove` - 移除频道
- `/list` - 列出频道
- `/pause` - 暂停下载
- `/resume` - 恢复下载
- `/config` - 查看配置

**运行**:
```bash
python telegram_bot_controller.py
```

**要求**:
- 配置 `bot_token`
- 配置 `admin_ids`

---

### 3. tg_to_onedrive.py

**功能**: OneDrive 自动上传器（独立运行）

**核心类**:
- `Config` - 配置管理
- `OneDriveUploader` - OneDrive 上传器
- `UploadFilter` - 文件过滤器
- `DownloadHandler` - 文件系统监听器

**主要功能**:
- 监听本地目录
- 检测文件变化
- 自动上传到 OneDrive
- 大文件分块上传
- 去重检查

**运行**:
```bash
python tg_to_onedrive.py --watch-path /path/to/downloads
```

**使用场景**:
- 配合第三方下载工具使用
- 独立的目录监听上传

---

### 4. get_refresh_token.py

**功能**: 获取 OneDrive Refresh Token

**工作流程**:
1. 启动本地 HTTP 服务器（端口 8080）
2. 打开浏览器进行 OAuth 授权
3. 接收授权码
4. 交换 Refresh Token
5. 自动生成 `onedrive_config.json`

**运行**:
```bash
python get_refresh_token.py
```

**前置要求**:
- 已在 Azure 创建应用
- 已获取 Client ID 和 Secret
- 已配置重定向 URI 为 `http://localhost:8080`

---

### 5. start.py

**功能**: 启动向导（交互式配置和启动）

**功能**:
- 检查依赖
- 创建配置文件
- 引导配置
- 选择运行模式

**运行**:
```bash
python start.py
```

**适合**:
- 首次使用
- 不熟悉命令行
- 需要引导式配置

---

## 📋 配置文件详解

### telegram_config.json

```json
{
  "api_id": 12345678,                    // Telegram API ID
  "api_hash": "xxx",                      // Telegram API Hash
  "phone": "+8613800138000",              // 手机号
  "channels": ["@channel"],               // 监听频道列表
  "download_path": "./downloads",         // 下载目录
  "media_types": ["photo", "video"],      // 媒体类型
  "file_size_limit": 2147483648,         // 文件大小限制（bytes）
  "extensions_whitelist": [],             // 扩展名白名单
  "extensions_blacklist": [".exe"],       // 扩展名黑名单
  "auto_upload": true,                    // 自动上传
  "delete_after_upload": false,           // 上传后删除
  "bot_token": "xxx",                     // Bot Token（可选）
  "admin_ids": [123456789]                // 管理员 ID（可选）
}
```

### onedrive_config.json

```json
{
  "client_id": "xxx",                     // Azure 应用客户端 ID
  "client_secret": "xxx",                 // Azure 应用客户端密码
  "refresh_token": "xxx",                 // OneDrive Refresh Token
  "base_path": "/TG_Media",              // OneDrive 存储路径
  "chunk_size": 10,                       // 分块大小（MB）
  "min_stable_time": 5,                   // 文件稳定时间（秒）
  "excluded_extensions": [".tmp"],        // 排除扩展名
  "min_file_size": 0,                     // 最小文件大小
  "max_file_size": 268435456000          // 最大文件大小（250GB）
}
```

---

## 🐳 Docker 文件详解

### Dockerfile

**基础镜像**: `python:3.11-slim`

**安装内容**:
- Python 依赖（requirements.txt + requirements_telegram.txt）
- 系统依赖（gcc, git）

**工作目录**: `/app`

**暴露端口**: 无（不需要）

**数据卷**:
- `/app/downloads` - 下载目录
- `/app/config` - 配置目录
- `/app/logs` - 日志目录

### docker-compose.yml

**服务**:

1. **telegram-downloader** (主服务)
   - 功能: Telegram 下载 + OneDrive 上传
   - 命令: `python telegram_bot_controller.py`
   - 自动重启: `unless-stopped`

2. **onedrive-uploader** (可选服务)
   - 功能: 独立的目录监听上传
   - 命令: `python tg_to_onedrive.py`
   - 启用: `--profile standalone`

**资源限制**:
- CPU: 最大 2 核，预留 0.5 核
- 内存: 最大 2GB，预留 512MB

---

## 📚 文档说明

### README.md
- 主文档
- 快速开始
- 安装部署
- 配置说明
- 使用场景
- 常见问题

### TELEGRAM_README.md
- Telegram 下载器详细文档
- 完整的功能说明
- 配置详解
- 使用示例

### DOCKER.md
- Docker 部署完整指南
- docker-compose 使用
- 生产部署建议
- 故障排查

### FAQ.md
- 50+ 常见问题
- 详细的解决方案
- 使用技巧

### CONTRIBUTING.md
- 贡献指南
- 代码规范
- Commit 规范
- 开发环境设置

---

## 🧪 测试文件

### test_uploader.py
- OneDrive 上传器单元测试
- 测试配置管理
- 测试文件过滤
- 测试上传功能

### test_project.py
- 项目完整性测试
- 语法检查
- 配置文件验证
- Docker 文件检查
- 文档完整性

---

## 🔄 CI/CD 工作流

### python-quality.yml
- 触发: Push / PR
- 功能: 代码质量检查
- 内容:
  - Python 3.8-3.12 多版本测试
  - Flake8 代码检查
  - Black 格式检查
  - Pylint 静态分析
  - Bandit 安全扫描

### release.yml
- 触发: 推送 tag (v*.*.*)
- 功能: 自动构建和发布
- 内容:
  - 构建可执行文件
  - 创建 Release
  - 上传构建产物

### update-deps.yml
- 触发: 每周一 + 手动
- 功能: 自动更新依赖
- 内容:
  - 检查依赖更新
  - 创建 PR

---

## 📊 依赖说明

### requirements.txt (OneDrive 上传器)
```
watchdog>=2.1.0       # 文件系统监听
requests>=2.28.0      # HTTP 请求
urllib3>=1.26.0       # HTTP 工具
```

### requirements_telegram.txt (Telegram 下载器)
```
telethon>=1.36.0      # Telegram 客户端库
```

---

## 🗂️ 运行时生成的文件

### 配置文件（用户创建）
- `telegram_config.json` - Telegram 配置
- `onedrive_config.json` - OneDrive 配置

### Session 文件（自动生成）
- `downloader_session.session` - Telegram 登录会话
- `bot_session.session` - Bot 登录会话

### 数据文件（自动生成）
- `downloaded_messages.json` - 已下载消息记录
- `uploaded_files.json` - 已上传文件记录

### 日志文件（自动生成）
- `tg_downloader.log` - 下载器日志
- `tg_to_onedrive.log` - 上传器日志

### 下载目录（自动创建）
- `downloads/` - 下载文件存储目录
  - `频道名/` - 按频道分类

---

## 🔒 安全文件（.gitignore）

已排除的敏感文件:
```
telegram_config.json      # Telegram 配置（含 API 密钥）
onedrive_config.json      # OneDrive 配置（含 Token）
*.session                 # Telegram Session（含登录信息）
downloaded_messages.json  # 下载记录
uploaded_files.json       # 上传记录
*.log                     # 日志文件
downloads/                # 下载目录
```

---

## 📞 获取帮助

- **使用问题**: 查看 [FAQ.md](FAQ.md)
- **Bug 报告**: 提交 [GitHub Issue](https://github.com/yannlie/tg-to-onedrive-uploader/issues)
- **功能建议**: 提交 [GitHub Discussion](https://github.com/yannlie/tg-to-onedrive-uploader/discussions)
- **贡献代码**: 参考 [CONTRIBUTING.md](CONTRIBUTING.md)

---

**最后更新**: 2024-06-16
