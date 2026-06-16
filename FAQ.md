# 常见问题 FAQ

## 安装和配置

### Q: 如何安装 Python 依赖？

```bash
pip install -r requirements.txt
```

如果遇到权限问题，使用：
```bash
pip install --user -r requirements.txt
```

### Q: Azure 应用注册时提示"需要管理员权限"？

**情况 1：企业账户**
- 联系你的 IT 管理员获取权限
- 或使用个人 Microsoft 账户

**情况 2：个人账户**
- 确保选择「任何组织目录(任何 Azure AD 目录 - 多租户)中的帐户和个人 Microsoft 帐户」
- 不要选择「仅此组织目录中的帐户」

### Q: 获取 refresh_token 时浏览器授权失败？

1. **检查重定向 URI**
   - 必须完全是 `http://localhost:8080`
   - 不能有多余的斜杠或路径

2. **端口被占用**
   - 关闭其他占用 8080 端口的程序
   - 或修改 `get_refresh_token.py` 中的端口号

3. **防火墙拦截**
   - 允许 Python 访问网络
   - 临时关闭防火墙测试

### Q: 配置文件格式错误？

确保 `onedrive_config.json` 是有效的 JSON 格式：

```json
{
  "client_id": "your-client-id",
  "client_secret": "your-client-secret",
  "refresh_token": "your-refresh-token",
  "base_path": "/TG_Media"
}
```

**常见错误**：
- ❌ 最后一行有逗号
- ❌ 使用单引号 `'` 而不是双引号 `"`
- ❌ 字符串中的特殊字符未转义

## 上传问题

### Q: 上传失败，提示 401 Unauthorized？

**原因**：Token 过期或无效

**解决方法**：
```bash
# 删除旧配置
rm onedrive_config.json

# 重新获取 token
python get_refresh_token.py
```

### Q: 上传失败，提示 403 Forbidden？

**原因**：权限不足

**解决方法**：
1. 检查 Azure 应用的 API 权限
2. 确保添加了 `Files.ReadWrite.All` 权限
3. 点击「代表 XXX 授予管理员同意」（如果有）

### Q: 上传失败，提示 404 Not Found？

**原因**：OneDrive 路径不存在

**解决方法**：
- `base_path` 不需要手动创建，程序会自动创建
- 检查路径格式：`/folder/subfolder`（开头必须有 `/`）
- 不要使用 Windows 格式路径：~~`\folder\subfolder`~~

### Q: 大文件上传到一半就失败了？

**可能原因**：
1. 网络不稳定
2. OneDrive 存储空间不足
3. 单个文件超过 OneDrive 限制（250GB）

**解决方法**：
- 检查网络连接
- 检查 OneDrive 剩余空间
- 程序会自动重试 3 次

### Q: 文件上传重复了？

**原因**：`uploaded_files.json` 记录丢失

**解决方法**：
- 不要删除 `uploaded_files.json`
- 如果丢失，程序会根据「文件名 + 大小」判断去重
- 手动清理 OneDrive 中的重复文件

### Q: 上传速度很慢？

**优化建议**：
1. **调整分块大小**（`tg_to_onedrive.py` 第 93 行）：
   ```python
   chunk_size = 10 * 1024 * 1024  # 默认 10MB，可改为 20MB
   ```

2. **使用更快的网络**

3. **多文件并发上传**（高级）：
   - 修改代码支持多线程上传

## 监听和检测

### Q: 程序运行了，但文件下载后不自动上传？

**排查步骤**：

1. **检查监听目录**
   ```python
   WATCH_PATH = 'd:/telegram_downloads'  # 确保路径正确
   ```

2. **检查文件是否在监听目录内**
   - 必须在 `WATCH_PATH` 或其子目录

3. **查看日志**
   ```bash
   tail -f tg_to_onedrive.log
   ```

4. **测试监听**
   - 手动复制一个文件到监听目录
   - 看是否触发上传

### Q: 文件还在下载就开始上传了（上传不完整）？

**解决方法**：增加稳定时间（`tg_to_onedrive.py` 第 161 行）

```python
def __init__(self, uploader, watch_path, min_stable_time=5):
    # 改为 10 秒或更长
    self.min_stable_time = 10
```

### Q: 某些文件类型不想上传怎么办？

在 `_upload_file` 方法中添加过滤：

```python
def _upload_file(self, file_path):
    file_path = Path(file_path)
    
    # 跳过某些扩展名
    if file_path.suffix.lower() in ['.tmp', '.part', '.txt']:
        logger.info(f"跳过文件类型: {file_path.name}")
        return
    
    # 跳过小于 1MB 的文件
    if file_path.stat().st_size < 1024 * 1024:
        logger.info(f"文件太小，跳过: {file_path.name}")
        return
    
    # 原有代码...
```

## 运行和部署

### Q: 如何后台运行程序？

**Windows**：
```batch
# 方法 1: 使用 start
start /B python tg_to_onedrive.py

# 方法 2: 使用 pythonw（无窗口）
pythonw tg_to_onedrive.py
```

**Linux/macOS**：
```bash
# 方法 1: nohup
nohup python tg_to_onedrive.py > /dev/null 2>&1 &

# 方法 2: screen
screen -dmS tg_uploader python tg_to_onedrive.py

# 方法 3: tmux
tmux new -d -s tg_uploader 'python tg_to_onedrive.py'
```

### Q: 如何设置开机自启动？

**Windows**：
1. 创建 `start_uploader.bat`（见 README）
2. Win+R 输入 `shell:startup`
3. 将批处理文件快捷方式放入

**Linux (systemd)**：
见 README 中的 systemd 配置

**macOS (launchd)**：
```xml
<!-- ~/Library/LaunchAgents/com.tg.onedrive.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.tg.onedrive</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/tg_to_onedrive.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

加载服务：
```bash
launchctl load ~/Library/LaunchAgents/com.tg.onedrive.plist
```

### Q: 程序崩溃了怎么办？

1. **查看日志**
   ```bash
   tail -100 tg_to_onedrive.log
   ```

2. **常见崩溃原因**
   - Token 过期：重新获取
   - 网络断开：检查网络
   - 磁盘空间不足：清理空间
   - 权限问题：检查目录权限

3. **自动重启**
   - 使用 systemd 的 `Restart=always`
   - 或使用 supervisor

## 与 telegram_media_downloader 整合

### Q: telegram_media_downloader 是什么？

一个自动下载 Telegram 频道/群组媒体文件的工具。

项目地址：https://github.com/tangyoha/telegram_media_downloader

### Q: 如何配置两个程序协同工作？

1. **安装 telegram_media_downloader**
   ```bash
   git clone https://github.com/tangyoha/telegram_media_downloader.git
   cd telegram_media_downloader
   pip install -r requirements.txt
   ```

2. **配置下载目录一致**
   
   在 `telegram_media_downloader/config.yaml`：
   ```yaml
   api_id: YOUR_API_ID
   api_hash: YOUR_API_HASH
   media:
     download_path: d:/telegram_downloads
   ```

   在 `tg_to_onedrive.py`：
   ```python
   WATCH_PATH = 'd:/telegram_downloads'
   ```

3. **启动顺序**
   ```bash
   # 先启动上传程序
   python tg_to_onedrive.py
   
   # 再启动下载程序
   cd telegram_media_downloader
   python media_downloader.py
   ```

### Q: 可以监听多个 Telegram 下载目录吗？

可以！修改 `tg_to_onedrive.py` 的 `main()` 函数：

```python
def main():
    # 多个监听目录
    watch_paths = [
        'd:/telegram_downloads/channel1',
        'd:/telegram_downloads/channel2',
        'e:/other_downloads'
    ]
    
    uploader = OneDriveUploader('onedrive_config.json')
    observers = []
    
    for watch_path in watch_paths:
        handler = DownloadHandler(uploader, watch_path)
        observer = Observer()
        observer.schedule(handler, watch_path, recursive=True)
        observer.start()
        observers.append(observer)
        logger.info(f"开始监听: {watch_path}")
    
    try:
        while True:
            for handler in [obs._handlers for obs in observers]:
                handler[0].check_stable_files()
            time.sleep(2)
    except KeyboardInterrupt:
        for obs in observers:
            obs.stop()
        for obs in observers:
            obs.join()
```

## 安全和隐私

### Q: 配置文件会泄露吗？

`onedrive_config.json` 已在 `.gitignore` 中排除，不会上传到 Git。

**安全建议**：
- 不要分享配置文件
- 定期更换 `client_secret`
- 不要截图时暴露 Token

### Q: 上传到 OneDrive 的文件是私有的吗？

是的，只有你可以访问。

如果配合 `onedrive-cf-index-ng` 公开分享：
- 只分享你明确想公开的目录
- 不要分享敏感文件
- 可以设置密码保护

### Q: Token 被盗用怎么办？

1. 访问 https://account.live.com/consent/Manage
2. 撤销对应应用的授权
3. 在 Azure 重新生成 `client_secret`
4. 重新运行 `get_refresh_token.py`

## 性能和限制

### Q: OneDrive API 有速率限制吗？

是的。OneDrive API 限制：
- 个人账户：较宽松，一般不会触及
- 企业账户：更严格

如果遇到 429 错误（Too Many Requests），程序会自动重试。

### Q: 可以上传多大的文件？

- 单文件最大：250GB（OneDrive 限制）
- 程序会自动分块上传大文件

### Q: 可以同时上传多个文件吗？

当前版本是单线程上传。如需并发上传，可以改造代码使用线程池。

### Q: 上传会占用很多内存吗？

不会。程序使用流式上传：
- 小文件（< 4MB）：一次性读入内存
- 大文件：分块读取，内存占用约 10MB

## 其他

### Q: 可以下载后自动删除本地文件吗？

可以！在 `_upload_file` 方法成功上传后添加：

```python
if self.uploader.upload_file(file_path, remote_path):
    self.uploaded_files.add(file_key)
    self._save_uploaded_record()
    
    # 上传成功后删除本地文件
    try:
        os.remove(file_path)
        logger.info(f"已删除本地文件: {file_path.name}")
    except Exception as e:
        logger.error(f"删除文件失败: {e}")
```

### Q: 支持 Google Drive / Dropbox 吗？

当前版本仅支持 OneDrive。

如需支持其他云盘：
1. Fork 本项目
2. 参考 `OneDriveUploader` 类实现其他云盘的上传器
3. 提交 Pull Request

### Q: 有 Web 管理界面吗？

当前版本没有。如有需求，可以考虑添加：
- Flask/FastAPI Web 界面
- 查看上传历史
- 手动触发上传
- 配置管理

欢迎贡献代码！

### Q: 可以发送上传完成通知吗？

可以！在 `_upload_file` 方法成功后发送通知：

**Telegram Bot 通知**：
```python
import requests

def send_telegram_notification(message):
    bot_token = 'YOUR_BOT_TOKEN'
    chat_id = 'YOUR_CHAT_ID'
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    requests.post(url, json={'chat_id': chat_id, 'text': message})

# 在上传成功后调用
send_telegram_notification(f'✅ 已上传: {file_path.name}')
```

**邮件通知**：
```python
import smtplib
from email.mime.text import MIMEText

def send_email_notification(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'your@email.com'
    msg['To'] = 'your@email.com'
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('your@email.com', 'password')
        server.send_message(msg)
```

---

## 还有问题？

- 📖 查看 [README](README.md) 和 [贡献指南](CONTRIBUTING.md)
- 🐛 [提交 Issue](https://github.com/yannlie/tg-to-onedrive-uploader/issues)
- 💬 [发起讨论](https://github.com/yannlie/tg-to-onedrive-uploader/discussions)
