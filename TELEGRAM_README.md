# Telegram Media Downloader

完整的 Telegram 媒体下载器，支持监听频道/群组并自动上传到 OneDrive。

## ✨ 功能特性

### 核心功能
- 🔄 **实时监听** - 自动监听多个频道/群组的新消息
- 📥 **智能下载** - 支持照片、视频、文档、音频等媒体类型
- 🎯 **灵活过滤** - 按文件类型、大小、扩展名过滤
- 📁 **目录管理** - 按频道自动分类存储
- 🚀 **自动上传** - 下载完成后自动上传到 OneDrive
- 🗑️ **自动清理** - 上传成功后可选删除本地文件
- 📊 **实时统计** - 下载/上传数量、流量统计
- 💾 **断点续传** - 避免重复下载已处理的消息

## 📦 安装

### 1. 安装依赖

```bash
# 安装 Telegram 下载器依赖
pip install -r requirements_telegram.txt

# 安装 OneDrive 上传器依赖（如需自动上传）
pip install -r requirements.txt
```

### 2. 获取 Telegram API 凭据

1. 访问 https://my.telegram.org/apps
2. 登录你的 Telegram 账号
3. 创建应用，获取 `api_id` 和 `api_hash`

### 3. 配置 Telegram

复制配置模板：
```bash
cp telegram_config.example.json telegram_config.json
```

编辑 `telegram_config.json`：
```json
{
  "api_id": "12345678",
  "api_hash": "your_api_hash_here",
  "phone": "+8613800138000",
  "channels": [
    "@channel_username",
    "https://t.me/joinchat/xxx",
    -1001234567890
  ],
  "download_path": "./downloads",
  "media_types": ["photo", "video", "document"],
  "auto_upload": true
}
```

**频道格式说明**：
- `@username` - 公开频道用户名
- `https://t.me/xxx` - 频道链接
- `-1001234567890` - 频道 Chat ID（数字）

### 4. 配置 OneDrive（可选）

如果需要自动上传到 OneDrive：
```bash
# 配置 OneDrive
python get_refresh_token.py

# 会生成 onedrive_config.json
```

## 🚀 使用方法

### 启动下载器

```bash
python telegram_downloader.py
```

**首次运行**：
1. 会要求输入手机号验证码
2. 成功登录后会保存 session
3. 下次运行无需再次登录

### 工作流程

```
监听频道新消息 → 检查文件类型 → 下载媒体 → 上传 OneDrive → (可选)删除本地文件
```

### 查看下载

下载的文件按频道分类存储：
```
downloads/
├── 频道名1/
│   ├── photo_123456_20240615.jpg
│   └── video_123457_20240615.mp4
└── 频道名2/
    └── document_123458_20240615.pdf
```

## ⚙️ 配置详解

### telegram_config.json

```json
{
  "api_id": "12345678",              // 必填：Telegram API ID
  "api_hash": "xxx",                  // 必填：Telegram API Hash
  "phone": "+8613800138000",          // 必填：手机号（国际格式）
  
  "channels": [                       // 监听的频道/群组列表
    "@channel1",
    "https://t.me/channel2",
    -1001234567890
  ],
  
  "download_path": "./downloads",     // 下载目录
  
  "media_types": [                    // 下载的媒体类型
    "photo",                          // 照片
    "video",                          // 视频
    "document",                       // 文档
    "audio"                           // 音频
  ],
  
  "file_size_limit": 2147483648,     // 文件大小限制（bytes，默认 2GB）
  
  "extensions_whitelist": [],         // 扩展名白名单（留空不限制）
  "extensions_blacklist": [           // 扩展名黑名单
    ".exe", ".bat", ".cmd"
  ],
  
  "auto_upload": true,                // 自动上传到 OneDrive
  "delete_after_upload": false        // 上传后删除本地文件
}
```

### 过滤规则优先级

1. **已下载检查** - 跳过已处理的消息
2. **媒体类型** - `media_types` 中指定的类型
3. **文件大小** - 不超过 `file_size_limit`
4. **扩展名黑名单** - 排除 `extensions_blacklist`
5. **扩展名白名单** - 如果设置，只下载白名单中的

### 示例配置

#### 只下载视频
```json
{
  "media_types": ["video"],
  "extensions_whitelist": [".mp4", ".mkv", ".avi"]
}
```

#### 只下载大于 10MB 的文件
```json
{
  "file_size_limit": 2147483648,
  "min_file_size": 10485760
}
```

#### 下载图片但不上传
```json
{
  "media_types": ["photo"],
  "auto_upload": false
}
```

## 📊 运行日志

程序会输出详细日志：

```
2024-06-15 10:30:00 - INFO - Telegram Media Downloader v1.0.0
2024-06-15 10:30:01 - INFO - ✓ 已登录: 张三 (@zhangsan)
2024-06-15 10:30:02 - INFO - ✓ 已添加监听: 我的频道 (@my_channel)
2024-06-15 10:30:03 - INFO - ✓ 机器人已启动，开始监听消息...
2024-06-15 10:30:15 - INFO - 收到新消息: 我的频道 - 消息ID 12345
2024-06-15 10:30:15 - INFO - 开始下载: video_12345_20240615.mp4 来自 我的频道
2024-06-15 10:30:20 - INFO - 下载进度: 50.0% (50000000/100000000 bytes)
2024-06-15 10:30:25 - INFO - ✓ 下载成功: video_12345_20240615.mp4 (95.37 MB)
2024-06-15 10:30:26 - INFO - 开始上传: video_12345_20240615.mp4
2024-06-15 10:30:35 - INFO - ✓ 上传成功: video_12345_20240615.mp4
```

日志文件：`tg_downloader.log`

## 🔧 常见问题

### Q: 如何获取频道 ID？

**方法 1**：使用 @userinfobot
1. 转发频道消息给 @userinfobot
2. 会返回频道的 Chat ID

**方法 2**：使用代码
```python
from telethon import TelegramClient

client = TelegramClient('session', api_id, api_hash)
async def get_id():
    await client.start()
    entity = await client.get_entity('@channel_username')
    print(entity.id)
```

### Q: 提示 "Phone number is not registered"？

你的 Telegram 账号未注册。需要先在手机上注册 Telegram。

### Q: 如何监听私有频道/群组？

1. 必须先加入该频道/群组
2. 使用频道链接或 ID 添加到配置
3. 运行程序时会自动验证权限

### Q: 下载速度慢？

1. Telegram 有速率限制
2. 如果触发限流会自动等待
3. 大文件下载会显示进度

### Q: 可以同时运行多个实例吗？

可以，但需要：
1. 使用不同的配置文件
2. 使用不同的 session 名称
3. 避免监听相同的频道

### Q: 如何只下载历史消息？

当前版本只监听新消息。如需下载历史消息，可以使用：

```python
# 添加历史下载功能
async def download_history(client, channel, limit=100):
    async for message in client.iter_messages(channel, limit=limit):
        await downloader.download_media(message, channel.title)
```

## 🔐 安全建议

1. **保护配置文件** - 不要上传到公开仓库
   ```bash
   # .gitignore 已包含
   telegram_config.json
   onedrive_config.json
   *.session
   ```

2. **定期更换密钥** - 如果泄露，及时撤销

3. **谨慎设置权限** - 不要给陌生人管理员权限

4. **备份 session** - `downloader_session.session` 文件包含登录信息

## 📈 性能优化

### 并发下载（高级）

默认是单线程下载。如需并发：

```python
# 在 TelegramDownloaderBot 中添加
self.download_queue = asyncio.Queue()
self.workers = [asyncio.create_task(self._worker()) for _ in range(3)]

async def _worker(self):
    while True:
        message, chat_title = await self.download_queue.get()
        await self.downloader.download_media(message, chat_title)
        self.download_queue.task_done()
```

### 减少日志输出

设置日志级别为 WARNING：
```python
logging.basicConfig(level=logging.WARNING)
```

## 🤝 与原有工具整合

如果你已经有 OneDrive 上传工具，下载器会自动使用：

```
telegram_downloader.py  ←→  tg_to_onedrive.py
        ↓                           ↓
    下载媒体                    上传 OneDrive
```

配置文件共享：
- `onedrive_config.json` - OneDrive 配置
- `telegram_config.json` - Telegram 配置

## 📝 开发计划

- [ ] 支持下载历史消息
- [ ] Web 管理界面
- [ ] 多账号支持
- [ ] 定时任务（每天定时下载）
- [ ] 消息过滤（关键词、发送者）
- [ ] 数据库存储下载记录

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 🙏 致谢

- [Telethon](https://github.com/LonamiWebs/Telethon) - Telegram 客户端库
- 原项目 [telegram_media_downloader](https://github.com/tangyoha/telegram_media_downloader) 提供思路参考
