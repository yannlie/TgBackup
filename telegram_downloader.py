#!/usr/bin/env python3
"""
Telegram Media Downloader with Cloud Auto Upload
完整的 TG 媒体下载器，支持监听频道/群组并自动上传到云盘

Version: 1.3.0
Features:
- 监听多个频道/群组
- 自动下载媒体文件（照片、视频、文档等）
- 文件类型过滤
- 自动上传到 OneDrive / Rclone (60+ 云盘)
- 实时进度显示
- 断点续传
"""

import os
import sys
import asyncio
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict
import hashlib

from telethon import TelegramClient, events
from telethon.tl.types import (
    MessageMediaPhoto, MessageMediaDocument,
    DocumentAttributeFilename, DocumentAttributeVideo,
    MessageMediaWebPage
)
from telethon.errors import FloodWaitError

# 导入上传器
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from tg_to_onedrive import OneDriveUploader, Config, UploadFilter
except ImportError:
    OneDriveUploader = None

try:
    from rclone_uploader import RcloneUploader
except ImportError:
    RcloneUploader = None

__version__ = "1.3.0"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tg_downloader.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TelegramConfig:
    """Telegram 配置管理"""

    def __init__(self, config_path='telegram_config.json'):
        self.config_path = config_path
        self.data = self._load()

    def _load(self) -> dict:
        """加载配置"""
        if not os.path.exists(self.config_path):
            # 创建默认配置
            default_config = {
                "api_id": "YOUR_API_ID",
                "api_hash": "YOUR_API_HASH",
                "phone": "YOUR_PHONE_NUMBER",
                "channels": [],
                "download_path": "./downloads",
                "media_types": ["photo", "video", "document", "audio"],
                "file_size_limit": 2147483648,
                "extensions_whitelist": [],
                "extensions_blacklist": [".exe", ".bat", ".cmd"],
                "auto_upload": False,
                "delete_after_upload": False
            }

            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)

            logger.warning(f"已创建配置文件模板: {self.config_path}")
            logger.warning("请填写 api_id, api_hash, phone 后再运行")
            sys.exit(0)

        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 验证必需字段
        if config.get('api_id') == 'YOUR_API_ID':
            raise ValueError("请先在配置文件中填写 api_id")
        if config.get('api_hash') == 'YOUR_API_HASH':
            raise ValueError("请先在配置文件中填写 api_hash")
        if config.get('phone') == 'YOUR_PHONE_NUMBER':
            raise ValueError("请先在配置文件中填写 phone")

        return config

    def get(self, key: str, default=None):
        """获取配置值"""
        return self.data.get(key, default)

    def save(self):
        """保存配置"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)


class MediaDownloader:
    """媒体文件下载器"""

    def __init__(self, tg_config: TelegramConfig, onedrive_config: Optional[Config] = None):
        self.tg_config = tg_config
        self.onedrive_config = onedrive_config
        self.download_path = Path(tg_config.get('download_path', './downloads'))
        self.download_path.mkdir(parents=True, exist_ok=True)

        # 初始化上传器
        self.uploader = None
        self.upload_filter = None
        self.uploader_type = None  # 'onedrive' 或 'rclone'

        # 优先使用 Rclone（如果配置了）
        rclone_config = tg_config.get('upload_rclone', {})
        if rclone_config.get('enable', False) and RcloneUploader:
            try:
                self.uploader = RcloneUploader(
                    remote_dir=rclone_config.get('remote_dir', 'onedrive:/TgBackup'),
                    rclone_path=rclone_config.get('rclone_path', 'rclone'),
                    before_upload_zip=rclone_config.get('before_upload_zip', False),
                    after_upload_delete=rclone_config.get('after_upload_delete', False)
                )
                self.uploader_type = 'rclone'
                logger.info(f"✓ Rclone 上传器已启用: {rclone_config.get('remote_dir')}")
            except Exception as e:
                logger.error(f"Rclone 初始化失败: {e}")

        # 回退到 OneDrive（如果 Rclone 未配置）
        elif onedrive_config and tg_config.get('auto_upload', False) and OneDriveUploader:
            try:
                self.uploader = OneDriveUploader(onedrive_config)
                self.upload_filter = UploadFilter(onedrive_config)
                self.uploader_type = 'onedrive'
                logger.info("✓ OneDrive 上传器已启用")
            except Exception as e:
                logger.warning(f"OneDrive 上传器初始化失败: {e}")

        # 统计信息
        self.stats = {
            'downloaded': 0,
            'uploaded': 0,
            'failed': 0,
            'skipped': 0,
            'bytes_downloaded': 0
        }

        # 已下载文件记录（避免重复下载）
        self.downloaded_ids = set()
        self._load_download_record()

    def _load_download_record(self):
        """加载下载记录"""
        record_file = 'downloaded_messages.json'
        if os.path.exists(record_file):
            with open(record_file, 'r', encoding='utf-8') as f:
                self.downloaded_ids = set(json.load(f))
            logger.info(f"已加载 {len(self.downloaded_ids)} 条下载记录")

    def _save_download_record(self):
        """保存下载记录"""
        with open('downloaded_messages.json', 'w', encoding='utf-8') as f:
            json.dump(list(self.downloaded_ids), f, indent=2)

    def _get_message_id(self, message) -> str:
        """生成消息唯一ID"""
        return f"{message.chat_id}_{message.id}"

    def _should_download(self, message) -> tuple[bool, Optional[str]]:
        """判断是否应该下载"""
        # 检查是否已下载
        msg_id = self._get_message_id(message)
        if msg_id in self.downloaded_ids:
            logger.debug(f"跳过: 消息 {msg_id} 已下载")
            return False, "已下载过"

        # 检查是否有媒体
        if not message.media:
            logger.debug(f"跳过: 消息 {msg_id} 无媒体")
            return False, "无媒体文件"

        # 检查媒体类型
        media_types = self.tg_config.get('media_types', [])
        logger.info(f"配置的媒体类型: {media_types}")
        logger.info(f"消息媒体类型: {type(message.media).__name__}")

        if isinstance(message.media, MessageMediaPhoto):
            if 'photo' not in media_types:
                logger.debug(f"跳过: 照片类型被排除")
                return False, "照片类型被排除"

        elif isinstance(message.media, MessageMediaDocument):
            doc = message.media.document

            # 检查文件大小
            size_limit = self.tg_config.get('file_size_limit', 2 * 1024 * 1024 * 1024)
            logger.info(f"文件大小: {doc.size / 1024 / 1024:.2f} MB, 限制: {size_limit / 1024 / 1024:.2f} MB")
            if doc.size > size_limit:
                return False, f"文件太大: {doc.size / 1024 / 1024:.2f} MB"

            # 获取文件名和扩展名
            filename = self._get_filename(message)
            ext = Path(filename).suffix.lower()
            logger.info(f"文件名: {filename}, 扩展名: {ext}")

            # 检查黑名单
            blacklist = self.tg_config.get('extensions_blacklist', [])
            if ext in blacklist:
                logger.debug(f"跳过: 扩展名 {ext} 在黑名单中")
                return False, f"扩展名被排除: {ext}"

            # 检查白名单（如果设置了）
            whitelist = self.tg_config.get('extensions_whitelist', [])
            if whitelist and ext not in whitelist:
                logger.debug(f"跳过: 扩展名 {ext} 不在白名单中")
                return False, f"扩展名不在白名单: {ext}"

            # 检查文档类型（通过 MIME 类型判断）
            mime_type = doc.mime_type
            logger.info(f"MIME 类型: {mime_type}")

            # 判断具体媒体类型
            is_video = 'video' in mime_type
            is_audio = 'audio' in mime_type

            logger.info(f"是否视频: {is_video}, 是否音频: {is_audio}")

            # 视频类型检查
            if is_video and 'video' not in media_types:
                logger.debug(f"跳过: 视频类型被排除")
                return False, "视频类型被排除"

            # 音频类型检查
            if is_audio and 'audio' not in media_types:
                logger.debug(f"跳过: 音频类型被排除")
                return False, "音频类型被排除"

            # 其他文档类型检查（不是视频也不是音频）
            if not is_video and not is_audio and 'document' not in media_types:
                logger.debug(f"跳过: 文档类型被排除")
                return False, "文档类型被排除"

        elif isinstance(message.media, MessageMediaWebPage):
            return False, "网页链接"
        else:
            logger.warning(f"不支持的媒体类型: {type(message.media)}")
            return False, f"不支持的媒体类型: {type(message.media)}"

        logger.info(f"✓ 消息 {msg_id} 通过所有过滤")
        return True, None

    def _get_filename(self, message) -> str:
        """获取文件名"""
        if isinstance(message.media, MessageMediaPhoto):
            # 照片使用消息ID + 时间戳
            timestamp = message.date.strftime('%Y%m%d_%H%M%S')
            return f"photo_{message.id}_{timestamp}.jpg"

        elif isinstance(message.media, MessageMediaDocument):
            doc = message.media.document

            # 尝试从属性中获取文件名
            for attr in doc.attributes:
                if isinstance(attr, DocumentAttributeFilename):
                    return attr.file_name
                elif isinstance(attr, DocumentAttributeVideo):
                    timestamp = message.date.strftime('%Y%m%d_%H%M%S')
                    return f"video_{message.id}_{timestamp}.mp4"

            # 使用 MIME 类型推断扩展名
            ext = self._get_extension_from_mime(doc.mime_type)
            timestamp = message.date.strftime('%Y%m%d_%H%M%S')
            return f"file_{message.id}_{timestamp}{ext}"

        return f"unknown_{message.id}"

    def _get_extension_from_mime(self, mime_type: str) -> str:
        """从 MIME 类型推断扩展名"""
        mime_map = {
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'video/mp4': '.mp4',
            'video/x-matroska': '.mkv',
            'video/quicktime': '.mov',
            'audio/mpeg': '.mp3',
            'audio/ogg': '.ogg',
            'application/pdf': '.pdf',
            'application/zip': '.zip',
        }
        return mime_map.get(mime_type, '.bin')

    async def download_media(self, message, chat_title: str = "Unknown") -> Optional[Path]:
        """
        下载媒体文件

        Returns:
            Path: 下载的文件路径，失败返回 None
        """
        # 检查是否应该下载
        should_download, reason = self._should_download(message)
        if not should_download:
            logger.debug(f"跳过消息 {message.id}: {reason}")
            self.stats['skipped'] += 1
            return None

        try:
            # 获取文件名
            filename = self._get_filename(message)

            # 创建频道目录
            channel_dir = self.download_path / self._sanitize_filename(chat_title)
            channel_dir.mkdir(parents=True, exist_ok=True)

            file_path = channel_dir / filename

            # 如果文件已存在，跳过
            if file_path.exists():
                logger.info(f"文件已存在，跳过: {filename}")
                self.stats['skipped'] += 1
                self.downloaded_ids.add(self._get_message_id(message))
                self._save_download_record()
                return None

            logger.info(f"开始下载: {filename} 来自 {chat_title}")

            # 下载文件（带进度）
            def progress_callback(current, total):
                percent = (current / total) * 100
                if int(percent) % 10 == 0:  # 每 10% 输出一次
                    logger.info(f"下载进度: {percent:.1f}% ({current}/{total} bytes)")

            await message.download_media(
                file=str(file_path),
                progress_callback=progress_callback
            )

            file_size = file_path.stat().st_size
            logger.info(f"✓ 下载成功: {filename} ({file_size / 1024 / 1024:.2f} MB)")

            self.stats['downloaded'] += 1
            self.stats['bytes_downloaded'] += file_size
            self.downloaded_ids.add(self._get_message_id(message))
            self._save_download_record()

            # 自动上传到云盘
            if self.uploader:
                await self._upload_to_cloud(file_path, chat_title)

            return file_path

        except FloodWaitError as e:
            logger.warning(f"触发限流，需等待 {e.seconds} 秒")
            await asyncio.sleep(e.seconds)
            return await self.download_media(message, chat_title)

        except Exception as e:
            logger.error(f"下载失败: {filename}, 错误: {e}", exc_info=True)
            self.stats['failed'] += 1
            return None

    async def _upload_to_cloud(self, file_path: Path, chat_title: str):
        """上传文件到云盘（支持 OneDrive 和 Rclone）"""
        try:
            if self.uploader_type == 'rclone':
                # Rclone 上传
                remote_path = f"{chat_title}/{file_path.name}"

                loop = asyncio.get_event_loop()
                success, message = await loop.run_in_executor(
                    None,
                    self.uploader.upload_file,
                    str(file_path),
                    remote_path
                )

                if success:
                    self.stats['uploaded'] += 1
                    logger.info(f"✓ 已上传到云盘: {remote_path}")
                else:
                    logger.error(f"上传失败: {message}")

            elif self.uploader_type == 'onedrive':
                # OneDrive 上传（原逻辑）
                # 过滤检查
                if self.upload_filter:
                    should_upload, reason = self.upload_filter.should_upload(file_path)
                    if not should_upload:
                        logger.info(f"跳过上传: {file_path.name}, 原因: {reason}")
                        return

                # 构建远程路径（保留频道名称）
                remote_path = f"{chat_title}/{file_path.name}"

                # 在异步环境中运行同步上传
                loop = asyncio.get_event_loop()
                success = await loop.run_in_executor(
                    None,
                    self.uploader.upload_file,
                    file_path,
                    remote_path
                )

                if success:
                    self.stats['uploaded'] += 1

                    # 上传成功后删除本地文件
                    if self.tg_config.get('delete_after_upload', False):
                        try:
                            os.remove(file_path)
                            logger.info(f"已删除本地文件: {file_path.name}")
                        except Exception as e:
                            logger.error(f"删除文件失败: {e}")

        except Exception as e:
            logger.error(f"上传失败: {file_path.name}, 错误: {e}")

    def _sanitize_filename(self, name: str) -> str:
        """清理文件名（移除非法字符）"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        return name[:100]  # 限制长度

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self.stats.copy()


class TelegramDownloaderBot:
    """Telegram 下载机器人主类"""

    def __init__(
        self,
        tg_config: TelegramConfig,
        onedrive_config: Optional[Config] = None
    ):
        self.tg_config = tg_config
        self.onedrive_config = onedrive_config

        # 初始化 Telegram 客户端
        self.client = TelegramClient(
            'sessions/downloader_session',
            int(tg_config.get('api_id')),
            tg_config.get('api_hash')
        )

        # 初始化下载器
        self.downloader = MediaDownloader(tg_config, onedrive_config)

        # 监听的频道/群组
        self.channels = []

    async def start(self):
        """启动机器人"""
        logger.info("=" * 60)
        logger.info(f"Telegram Media Downloader v{__version__}")
        logger.info("=" * 60)

        await self.client.start(phone=self.tg_config.get('phone'))

        me = await self.client.get_me()
        logger.info(f"✓ 已登录: {me.first_name} (@{me.username})")

        # 解析频道列表
        await self._parse_channels()

        # 注册事件处理器
        self._register_handlers()

        logger.info("✓ 机器人已启动，开始监听消息...")
        logger.info("按 Ctrl+C 停止")

    async def _parse_channels(self):
        """解析和验证频道列表"""
        channel_inputs = self.tg_config.get('channels', [])

        if not channel_inputs:
            logger.warning("配置文件中没有频道！请在 telegram_config.json 中添加频道")
            return

        for channel_input in channel_inputs:
            try:
                entity = await self.client.get_entity(channel_input)
                self.channels.append(entity)
                logger.info(f"✓ 已添加监听: {entity.title} ({channel_input})")
            except Exception as e:
                logger.error(f"无法添加频道 {channel_input}: {e}")

    def _register_handlers(self):
        """注册消息处理器"""
        @self.client.on(events.NewMessage(chats=self.channels))
        async def handle_new_message(event):
            message = event.message
            chat = await event.get_chat()
            chat_title = getattr(chat, 'title', 'Private')

            logger.info(f"收到新消息: {chat_title} - 消息ID {message.id}")

            # 下载媒体
            await self.downloader.download_media(message, chat_title)

    async def run(self):
        """运行机器人"""
        try:
            await self.start()
            await self.client.run_until_disconnected()
        except KeyboardInterrupt:
            logger.info("收到停止信号...")
        finally:
            await self.stop()

    async def download_history(
        self,
        channel_input: str,
        limit: int = 100,
        offset_date: Optional[datetime] = None
    ):
        """
        下载频道历史消息

        Args:
            channel_input: 频道用户名或 ID
            limit: 下载数量限制（0 = 全部）
            offset_date: 起始日期（None = 从最新开始）
        """
        try:
            entity = await self.client.get_entity(channel_input)
            chat_title = getattr(entity, 'title', channel_input)

            logger.info("=" * 60)
            logger.info(f"开始下载历史消息: {chat_title}")
            logger.info(f"  限制数量: {limit if limit > 0 else '全部'}")
            if offset_date:
                logger.info(f"  起始日期: {offset_date.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 60)

            downloaded_count = 0
            processed_count = 0

            async for message in self.client.iter_messages(
                entity,
                limit=limit if limit > 0 else None,
                offset_date=offset_date
            ):
                processed_count += 1

                # 每处理 100 条消息输出进度
                if processed_count % 100 == 0:
                    logger.info(f"已处理 {processed_count} 条消息，已下载 {downloaded_count} 个文件")

                # 下载媒体
                result = await self.downloader.download_media(message, chat_title)
                if result:
                    downloaded_count += 1

            logger.info("=" * 60)
            logger.info("历史消息下载完成")
            logger.info(f"  处理消息: {processed_count}")
            logger.info(f"  下载文件: {downloaded_count}")
            logger.info("=" * 60)

            return downloaded_count

        except Exception as e:
            logger.error(f"下载历史消息失败: {e}")
            return 0

    async def stop(self):
        """停止机器人"""
        logger.info("正在关闭...")

        # 输出统计
        stats = self.downloader.get_stats()
        logger.info("=" * 60)
        logger.info("最终统计:")
        logger.info(f"  已下载: {stats['downloaded']}")
        logger.info(f"  已上传: {stats['uploaded']}")
        logger.info(f"  失败: {stats['failed']}")
        logger.info(f"  跳过: {stats['skipped']}")
        logger.info(f"  总下载: {stats['bytes_downloaded'] / 1024 / 1024:.2f} MB")
        logger.info("=" * 60)

        await self.client.disconnect()


async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='Telegram Media Downloader')
    parser.add_argument('--download-history', metavar='CHANNEL', help='下载频道历史消息')
    parser.add_argument('--limit', type=int, default=100, help='下载数量限制（0=全部，默认100）')
    parser.add_argument('--from-date', help='起始日期 (YYYY-MM-DD)')
    args = parser.parse_args()

    # 加载配置
    try:
        tg_config = TelegramConfig('config/telegram_config.json')
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Telegram 配置错误: {e}")
        sys.exit(1)

    # 加载 OneDrive 配置（可选）
    onedrive_config = None
    if os.path.exists('config/onedrive_config.json'):
        try:
            onedrive_config = Config('config/onedrive_config.json')
            logger.info("✓ OneDrive 配置已加载")
        except Exception as e:
            logger.warning(f"OneDrive 配置加载失败: {e}")
    else:
        logger.info("未找到 OneDrive 配置，仅下载不上传")

    # 创建机器人
    bot = TelegramDownloaderBot(tg_config, onedrive_config)

    # 如果是下载历史模式
    if args.download_history:
        await bot.start()

        # 解析日期
        offset_date = None
        if args.from_date:
            try:
                offset_date = datetime.strptime(args.from_date, '%Y-%m-%d')
            except ValueError:
                logger.error("日期格式错误，应为 YYYY-MM-DD")
                sys.exit(1)

        # 下载历史
        await bot.download_history(args.download_history, args.limit, offset_date)

        await bot.stop()
    else:
        # 正常运行模式
        await bot.run()


if __name__ == '__main__':
    asyncio.run(main())
