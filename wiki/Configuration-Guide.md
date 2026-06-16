# 配置指南

完整的 TgBackup 配置说明。

---

## 📋 配置文件

TgBackup 使用 `telegram_config.json` 作为主配置文件。

---

## 🎯 最小配置

这是能够运行的最小配置：

```json
{
  "api_id": 12345678,
  "api_hash": "your_api_hash_here",
  "phone": "+8613800138000",
  "channels": []
}
```

### 获取 API 凭据

1. 访问 https://my.telegram.org/apps
2. 使用手机号登录
3. 点击 "API development tools"
4. 创建应用（App title 和 Short name 随意填写）
5. 获得 `api_id` 和 `api_hash`

---

## ⭐ 推荐配置

启用 Bot 远程控制（强烈推荐）：

```json
{
  "api_id": 12345678,
  "api_hash": "your_api_hash_here",
  "phone": "+8613800138000",
  "channels": [],
  "bot_token": "123456:ABC-DEF...",
  "admin_ids": [123456789]
}
```

### 获取 Bot Token

与 [@BotFather](https://t.me/BotFather) 对话：

```
/newbot
→ Bot name: My TgBackup Bot
→ Bot username: mytgbackup_bot
→ 获得 bot_token
```

### 获取 User ID

与 [@userinfobot](https://t.me/userinfobot) 对话：

```
/start
→ 获得 User ID
```

---

## 📦 完整配置

包含所有选项的完整配置：

```json
{
  "api_id": 12345678,
  "api_hash": "your_api_hash_here",
  "phone": "+8613800138000",
  "channels": [
    "@channel_username",
    "https://t.me/channel_link",
    -1001234567890
  ],
  "download_path": "./downloads",
  "media_types": ["photo", "video", "document", "audio"],
  "file_size_limit": 2147483648,
  "extensions_whitelist": [],
  "extensions_blacklist": [".exe", ".bat", ".cmd", ".scr"],
  "auto_upload": true,
  "delete_after_upload": false,
  "bot_token": "123456:ABC-DEF...",
  "admin_ids": [123456789]
}
```

---

## 🔧 配置项详解

### 必需配置

#### api_id
- **类型**: 整数
- **说明**: Telegram API ID
- **获取**: https://my.telegram.org/apps
- **示例**: `12345678`

#### api_hash
- **类型**: 字符串
- **说明**: Telegram API Hash
- **获取**: https://my.telegram.org/apps
- **示例**: `"0123456789abcdef0123456789abcdef"`

#### phone
- **类型**: 字符串
- **说明**: 你的手机号（国际格式）
- **格式**: `+[国家码][手机号]`
- **示例**: `"+8613800138000"`

---

### 可选配置

#### channels
- **类型**: 数组
- **默认**: `[]`
- **说明**: 要监听的频道/群组列表
- **格式**: 
  - 用户名: `"@channel_username"`
  - 链接: `"https://t.me/channel_link"`
  - Chat ID: `-1001234567890`
- **示例**: 
  ```json
  "channels": [
    "@my_channel",
    "https://t.me/another_channel",
    -1001234567890
  ]
  ```
- **注意**: 可以为空！通过 Bot 动态添加或直接转发下载

#### download_path
- **类型**: 字符串
- **默认**: `"./downloads"`
- **说明**: 下载文件保存路径
- **示例**: `"./downloads"`, `"/data/tg_media"`

#### media_types
- **类型**: 数组
- **默认**: `["photo", "video", "document", "audio"]`
- **说明**: 要下载的媒体类型
- **可选值**: 
  - `"photo"` - 照片
  - `"video"` - 视频
  - `"document"` - 文档
  - `"audio"` - 音频
- **示例**: `["video", "document"]` (只下载视频和文档)

#### file_size_limit
- **类型**: 整数（字节）
- **默认**: `2147483648` (2 GB)
- **说明**: 文件大小限制
- **示例**: 
  - `104857600` (100 MB)
  - `1073741824` (1 GB)
  - `0` (不限制)

#### extensions_whitelist
- **类型**: 数组
- **默认**: `[]`
- **说明**: 扩展名白名单（留空=不限制）
- **示例**: `[".mp4", ".mkv", ".avi"]` (只下载这些格式)

#### extensions_blacklist
- **类型**: 数组
- **默认**: `[".exe", ".bat", ".cmd", ".scr"]`
- **说明**: 扩展名黑名单
- **示例**: `[".exe", ".msi", ".apk"]`

#### auto_upload
- **类型**: 布尔值
- **默认**: `true`
- **说明**: 下载后自动上传到 OneDrive
- **前提**: 需要配置 `onedrive_config.json`

#### delete_after_upload
- **类型**: 布尔值
- **默认**: `false`
- **说明**: 上传成功后删除本地文件
- **注意**: 慎用！确保上传成功

#### bot_token
- **类型**: 字符串
- **默认**: `""`
- **说明**: Telegram Bot Token
- **获取**: 与 @BotFather 对话
- **示例**: `"123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"`

#### admin_ids
- **类型**: 数组
- **默认**: `[]`
- **说明**: 允许控制 Bot 的用户 ID 列表
- **获取**: 与 @userinfobot 对话
- **示例**: `[123456789, 987654321]`

---

## 🎨 配置示例

### 示例 1: 零配置模式（仅转发下载）

```json
{
  "api_id": 12345678,
  "api_hash": "your_api_hash_here",
  "phone": "+8613800138000",
  "channels": [],
  "bot_token": "123456:ABC-DEF...",
  "admin_ids": [123456789]
}
```

**使用场景**: 不想配置频道，只想转发消息下载

---

### 示例 2: 自动监听模式

```json
{
  "api_id": 12345678,
  "api_hash": "your_api_hash_here",
  "phone": "+8613800138000",
  "channels": [
    "@resource_channel",
    "@study_channel",
    "@movie_channel"
  ],
  "media_types": ["video", "document"],
  "file_size_limit": 1073741824,
  "bot_token": "123456:ABC-DEF...",
  "admin_ids": [123456789]
}
```

**使用场景**: 24/7 自动备份多个频道的视频和文档

---

### 示例 3: 严格过滤模式

```json
{
  "api_id": 12345678,
  "api_hash": "your_api_hash_here",
  "phone": "+8613800138000",
  "channels": ["@video_channel"],
  "media_types": ["video"],
  "file_size_limit": 524288000,
  "extensions_whitelist": [".mp4", ".mkv"],
  "bot_token": "123456:ABC-DEF...",
  "admin_ids": [123456789]
}
```

**使用场景**: 只下载特定格式的视频，且不超过 500MB

---

### 示例 4: OneDrive 自动备份

```json
{
  "api_id": 12345678,
  "api_hash": "your_api_hash_here",
  "phone": "+8613800138000",
  "channels": ["@backup_channel"],
  "auto_upload": true,
  "delete_after_upload": true,
  "bot_token": "123456:ABC-DEF...",
  "admin_ids": [123456789]
}
```

**使用场景**: 自动上传 OneDrive，上传后删除本地文件节省空间

---

## 🔒 OneDrive 配置

如果启用 `auto_upload`，需要创建 `onedrive_config.json`：

```json
{
  "client_id": "your_client_id",
  "client_secret": "your_client_secret",
  "refresh_token": "your_refresh_token",
  "base_path": "/TG_Media",
  "chunk_size": 10,
  "min_stable_time": 5
}
```

**详细配置步骤**: 参考 [OneDrive 配置](OneDrive-Setup.md)

---

## 💡 配置技巧

### 1. 分阶段配置

```
第一阶段: 最小配置
→ 只填 api_id, api_hash, phone
→ 测试能否登录

第二阶段: 启用 Bot
→ 添加 bot_token, admin_ids
→ 测试 Bot 控制

第三阶段: 添加功能
→ 配置 channels 或使用转发
→ 配置 OneDrive
```

### 2. 环境区分

```
开发环境: config/telegram_config.dev.json
生产环境: config/telegram_config.prod.json
```

### 3. 安全建议

```
✅ 不要分享你的配置文件
✅ 不要提交配置到 Git
✅ 定期备份配置
✅ 使用环境变量（高级）
```

---

## 🔄 重载配置

修改配置后需要重启：

```bash
# Docker
docker restart tgbackup

# docker-compose
docker-compose restart
```

---

## ✅ 验证配置

### 1. JSON 格式检查

```bash
# Linux/Mac
python -c "import json; json.load(open('config/telegram_config.json'))"

# 或使用在线工具
https://jsonlint.com/
```

### 2. 启动测试

```bash
docker logs tgbackup
# 查看是否有错误
```

---

## ❓ 常见问题

### Q: channels 可以留空吗？
A: 可以！通过 Bot 动态添加或直接转发下载。

### Q: 如何监听私有频道？
A: 
1. 先手动加入该频道
2. 获取频道的 Chat ID（使用 @userinfobot）
3. 添加到 `channels` 列表

### Q: 修改配置后是否立即生效？
A: 不会，需要重启服务。

### Q: 如何同时使用多个账号？
A: 目前不支持，计划在 v2.0 实现。

---

## 🔗 相关文档

- [快速开始](Quick-Start.md)
- [Bot 命令大全](Bot-Commands.md)
- [OneDrive 配置](OneDrive-Setup.md)
- [文件过滤规则](File-Filters.md)

---

**配置完成后，开始使用吧！** 🚀
