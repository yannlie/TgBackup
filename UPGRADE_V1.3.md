# 🎉 TgBackup v1.3 - 重大更新

## ✨ 新增功能

### 1. 📝 YAML 配置支持
- ✅ 更易读的配置格式
- ✅ 支持注释
- ✅ 向后兼容 JSON
- ✅ 自动识别 `.yaml` / `.json`

### 2. 📡 多频道数组配置
- ✅ 支持同时监听多个频道
- ✅ 每个频道独立配置
- ✅ 支持频道级过滤器

### 3. 📁 文件路径自定义
- ✅ 灵活的目录结构
  - `chat_title` - 频道名称
  - `media_datetime` - 媒体日期
  - `media_type` - 媒体类型
- ✅ 自定义文件名前缀
  - `message_id` - 消息 ID
  - `file_name` - 原始文件名
  - `caption` - 消息标题
- ✅ 自定义日期格式

### 4. ☁️ Rclone 云盘支持
- ✅ 支持所有 rclone 兼容的云盘
  - Google Drive
  - Dropbox
  - Amazon S3
  - 阿里云盘
  - 百度网盘
  - ... 60+ 云存储
- ✅ 上传前压缩
- ✅ 上传后自动删除本地文件

### 5. 🔍 下载过滤器
- ✅ 按日期范围过滤
- ✅ 按消息 ID 过滤
- ✅ 按文件大小过滤
- ✅ 灵活的表达式语法

### 6. 🌐 Web 监控界面
- ✅ 实时查看下载统计
- ✅ 最近下载文件列表
- ✅ 运行状态监控
- ✅ 响应式设计

---

## 🚀 快速开始

### 配置文件示例 (YAML)

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
  
  - chat_id: -1001234567890
    last_read_message_id: 0
    download_filter: ""

# 文件路径自定义
file_path_prefix:
  - chat_title
  - media_datetime

file_name_prefix:
  - message_id
  - file_name

# Rclone 云盘上传
upload_rclone:
  enable: true
  remote_dir: "drive:/TgBackup"
  before_upload_zip: false
  after_upload_delete: false
  rclone_path: "rclone"

# Web 界面
web:
  enable: true
  host: "127.0.0.1"
  port: 5000
```

---

## 📦 使用方法

### 1. 使用 YAML 配置

```bash
# 复制示例配置
cp telegram_config.example.yaml config/telegram_config.yaml

# 编辑配置
nano config/telegram_config.yaml

# 运行（自动识别 YAML）
python telegram_downloader.py
```

### 2. Rclone 设置

```bash
# 安装 rclone
# Linux/Mac
curl https://rclone.org/install.sh | sudo bash

# Windows
# 下载: https://rclone.org/downloads/

# 配置远程存储
rclone config

# 测试连接
rclone lsd yourremote:

# 在配置文件中启用
upload_rclone:
  enable: true
  remote_dir: "yourremote:/path"
```

### 3. 使用过滤器

```yaml
channels:
  - chat_id: "@mychannel"
    download_filter: "message_date >= 2024-01-01 and message_date <= 2024-12-31"
  
  - chat_id: "@photos"
    download_filter: "file_size < 10485760"  # 小于 10MB
```

### 4. 访问 Web 界面

```bash
# 启动服务
python telegram_downloader.py

# 浏览器访问
http://localhost:5000
```

---

## 🆚 配置对比

### YAML vs JSON

**YAML (推荐)**
```yaml
api_id: 12345678
api_hash: "your_hash"
channels:
  - chat_id: "@channel"
    last_read_message_id: 0
```

**JSON (兼容)**
```json
{
  "api_id": 12345678,
  "api_hash": "your_hash",
  "channels": [
    {
      "chat_id": "@channel",
      "last_read_message_id": 0
    }
  ]
}
```

---

## 📊 文件路径示例

### 配置
```yaml
file_path_prefix:
  - chat_title
  - media_datetime
  - media_type

date_format: "%Y_%m"
```

### 结果
```
downloads/
├── TechChannel/
│   ├── 2024_06/
│   │   ├── video/
│   │   │   └── 12345 - tutorial.mp4
│   │   └── photo/
│   │       └── 12346 - screenshot.jpg
│   └── 2024_05/
└── NewsChannel/
    └── 2024_06/
```

---

## 🎯 高级功能

### 1. 上传前压缩

```yaml
upload_rclone:
  enable: true
  before_upload_zip: true  # 启用压缩
  after_upload_delete: true  # 上传后删除
```

### 2. 自定义文件名

```yaml
file_name_prefix:
  - message_id
  - caption
  - file_name

file_name_prefix_split: " | "
```

结果: `12345 | 视频标题 | original_name.mp4`

### 3. 复杂过滤器

```yaml
download_filter: "message_date >= 2024-01-01 and file_size > 1048576 and message_id > 1000"
```

---

## 🔧 依赖更新

```bash
# 安装新依赖
pip install -r requirements.txt
pip install -r requirements_telegram.txt

# 新增依赖
# - PyYAML>=6.0
# - flask>=3.0.0
# - flask-cors>=4.0.0
```

---

## 📝 迁移指南

### 从 JSON 迁移到 YAML

1. 复制现有配置
```bash
cp config/telegram_config.json config/telegram_config.yaml
```

2. 转换格式（手动或使用工具）

3. 删除旧文件（可选）
```bash
rm config/telegram_config.json
```

程序会自动使用 `.yaml` 文件（优先级更高）

---

## 🆕 新增文件

```
TgBackup/
├── config_loader.py           # 统一配置加载器
├── path_generator.py          # 路径生成器
├── rclone_uploader.py         # Rclone 上传器
├── download_filter.py         # 下载过滤器
├── web_monitor.py             # Web 监控服务
├── templates/
│   └── index.html             # Web 界面
└── telegram_config.example.yaml  # YAML 配置示例
```

---

## 🎊 总结

TgBackup v1.3 带来了：
- ✅ 更友好的配置格式
- ✅ 更灵活的文件组织
- ✅ 更多的云存储选择
- ✅ 更强大的过滤功能
- ✅ 更直观的监控界面

**项目现在达到生产级别！** 🚀
