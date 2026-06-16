#!/usr/bin/env python3
"""
Telegram Bot Controller
通过 Telegram Bot 远程控制下载器

命令:
/start - 启动信息
/status - 查看状态
/stats - 查看统计
/add <频道> - 添加监听频道
/remove <频道> - 移除监听频道
/list - 列出所有监听频道
/pause - 暂停下载
/resume - 恢复下载
/config - 查看配置
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from typing import Optional

from telethon import TelegramClient, events
from telethon.tl.types import User

# 导入主程序
from telegram_downloader import TelegramDownloaderBot, TelegramConfig, Config

logger = logging.getLogger(__name__)


class BotController:
    """Bot 控制器"""

    def __init__(
        self,
        bot_token: str,
        admin_ids: list,
        downloader_bot: TelegramDownloaderBot
    ):
        """
        Args:
            bot_token: Bot Token (@BotFather 获取)
            admin_ids: 管理员 ID 列表
            downloader_bot: 下载器实例
        """
        self.bot_token = bot_token
        self.admin_ids = set(admin_ids)
        self.downloader_bot = downloader_bot
        self.paused = False

        # 创建 Bot 客户端
        self.bot = TelegramClient(
            'bot_session',
            downloader_bot.tg_config.get('api_id'),
            downloader_bot.tg_config.get('api_hash')
        ).start(bot_token=bot_token)

    def is_admin(self, user_id: int) -> bool:
        """检查是否是管理员"""
        return user_id in self.admin_ids

    async def start(self):
        """启动 Bot"""
        logger.info("Bot 控制器已启动")

        @self.bot.on(events.NewMessage(pattern='/start'))
        async def cmd_start(event):
            if not self.is_admin(event.sender_id):
                await event.reply("❌ 无权限")
                return

            await event.reply(
                "🤖 **Telegram 下载器控制面板**\n\n"
                "可用命令:\n"
                "/status - 查看状态\n"
                "/stats - 查看统计\n"
                "/add <频道> - 添加监听\n"
                "/remove <频道> - 移除监听\n"
                "/list - 列出频道\n"
                "/pause - 暂停下载\n"
                "/resume - 恢复下载\n"
                "/config - 查看配置\n"
                "/history <频道> [数量] - 下载历史消息"
            )

        @self.bot.on(events.NewMessage(pattern='/status'))
        async def cmd_status(event):
            if not self.is_admin(event.sender_id):
                return

            status = "✅ 运行中" if not self.paused else "⏸️ 已暂停"
            channels_count = len(self.downloader_bot.channels)

            await event.reply(
                f"📊 **系统状态**\n\n"
                f"状态: {status}\n"
                f"监听频道: {channels_count} 个\n"
                f"运行时间: {self._get_uptime()}"
            )

        @self.bot.on(events.NewMessage(pattern='/stats'))
        async def cmd_stats(event):
            if not self.is_admin(event.sender_id):
                return

            stats = self.downloader_bot.downloader.get_stats()

            await event.reply(
                f"📈 **统计信息**\n\n"
                f"✅ 已下载: {stats['downloaded']}\n"
                f"☁️ 已上传: {stats['uploaded']}\n"
                f"❌ 失败: {stats['failed']}\n"
                f"⏭️ 跳过: {stats['skipped']}\n"
                f"📦 总下载: {stats['bytes_downloaded'] / 1024 / 1024:.2f} MB"
            )

        @self.bot.on(events.NewMessage(pattern='/list'))
        async def cmd_list(event):
            if not self.is_admin(event.sender_id):
                return

            if not self.downloader_bot.channels:
                await event.reply("📝 当前没有监听任何频道")
                return

            channels_text = "\n".join([
                f"• {ch.title} (@{getattr(ch, 'username', 'N/A')})"
                for ch in self.downloader_bot.channels
            ])

            await event.reply(f"📝 **监听频道列表**\n\n{channels_text}")

        @self.bot.on(events.NewMessage(pattern='/add'))
        async def cmd_add(event):
            if not self.is_admin(event.sender_id):
                return

            parts = event.message.text.split(maxsplit=1)
            if len(parts) < 2:
                await event.reply("❌ 用法: /add @channel 或 频道链接")
                return

            channel_input = parts[1].strip()

            try:
                entity = await self.downloader_bot.client.get_entity(channel_input)
                self.downloader_bot.channels.append(entity)

                # 保存到配置
                tg_config = self.downloader_bot.tg_config
                current_channels = tg_config.get('channels', [])
                if channel_input not in current_channels:
                    current_channels.append(channel_input)
                    tg_config.data['channels'] = current_channels
                    tg_config.save()

                await event.reply(f"✅ 已添加: {entity.title}")
                logger.info(f"通过 Bot 添加频道: {entity.title}")

            except Exception as e:
                await event.reply(f"❌ 添加失败: {e}")

        @self.bot.on(events.NewMessage(pattern='/remove'))
        async def cmd_remove(event):
            if not self.is_admin(event.sender_id):
                return

            parts = event.message.text.split(maxsplit=1)
            if len(parts) < 2:
                await event.reply("❌ 用法: /remove @channel")
                return

            channel_input = parts[1].strip()

            try:
                # 从监听列表移除
                entity = await self.downloader_bot.client.get_entity(channel_input)
                self.downloader_bot.channels = [
                    ch for ch in self.downloader_bot.channels
                    if ch.id != entity.id
                ]

                # 从配置移除
                tg_config = self.downloader_bot.tg_config
                current_channels = tg_config.get('channels', [])
                current_channels = [ch for ch in current_channels if ch != channel_input]
                tg_config.data['channels'] = current_channels
                tg_config.save()

                await event.reply(f"✅ 已移除: {entity.title}")
                logger.info(f"通过 Bot 移除频道: {entity.title}")

            except Exception as e:
                await event.reply(f"❌ 移除失败: {e}")

        @self.bot.on(events.NewMessage(pattern='/pause'))
        async def cmd_pause(event):
            if not self.is_admin(event.sender_id):
                return

            self.paused = True
            await event.reply("⏸️ 下载已暂停")

        @self.bot.on(events.NewMessage(pattern='/resume'))
        async def cmd_resume(event):
            if not self.is_admin(event.sender_id):
                return

            self.paused = False
            await event.reply("▶️ 下载已恢复")

        @self.bot.on(events.NewMessage(pattern='/config'))
        async def cmd_config(event):
            if not self.is_admin(event.sender_id):
                return

            tg_config = self.downloader_bot.tg_config

            config_text = (
                f"⚙️ **当前配置**\n\n"
                f"下载路径: `{tg_config.get('download_path')}`\n"
                f"媒体类型: {', '.join(tg_config.get('media_types', []))}\n"
                f"大小限制: {tg_config.get('file_size_limit', 0) / 1024 / 1024:.0f} MB\n"
                f"自动上传: {'✅' if tg_config.get('auto_upload') else '❌'}\n"
                f"上传后删除: {'✅' if tg_config.get('delete_after_upload') else '❌'}"
            )

            await event.reply(config_text)

        @self.bot.on(events.NewMessage(pattern='/history'))
        async def cmd_history(event):
            if not self.is_admin(event.sender_id):
                return

            parts = event.message.text.split()
            if len(parts) < 2:
                await event.reply(
                    "❌ 用法: /history <频道> [数量]\n\n"
                    "示例:\n"
                    "/history @channel 100\n"
                    "/history @channel 0 (下载全部)"
                )
                return

            channel_input = parts[1]
            limit = int(parts[2]) if len(parts) > 2 else 100

            await event.reply(f"🔄 开始下载历史消息: {channel_input}\n限制: {limit if limit > 0 else '全部'}\n\n请稍候...")

            try:
                count = await self.downloader_bot.download_history(channel_input, limit)
                await event.reply(f"✅ 历史下载完成！\n成功下载 {count} 个文件")
            except Exception as e:
                await event.reply(f"❌ 下载失败: {e}")

        logger.info("✓ Bot 命令已注册")

    def _get_uptime(self) -> str:
        """获取运行时间（简化版）"""
        # 可以记录启动时间并计算
        return "运行中"

    def should_process_message(self) -> bool:
        """是否应该处理消息（暂停检查）"""
        return not self.paused


async def main_with_bot():
    """带 Bot 控制的主函数"""
    # 加载配置
    try:
        tg_config = TelegramConfig('telegram_config.json')
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Telegram 配置错误: {e}")
        sys.exit(1)

    # 检查 Bot Token
    bot_token = tg_config.get('bot_token')
    admin_ids = tg_config.get('admin_ids', [])

    if not bot_token:
        logger.warning("未配置 bot_token，Bot 控制功能将不可用")
        logger.info("如需启用，请在 telegram_config.json 中添加:")
        logger.info('  "bot_token": "YOUR_BOT_TOKEN"')
        logger.info('  "admin_ids": [YOUR_USER_ID]')
        # 继续运行但不启用 Bot
        from telegram_downloader import main
        await main()
        return

    if not admin_ids:
        logger.error("未配置 admin_ids，Bot 控制需要管理员 ID")
        sys.exit(1)

    # 加载 OneDrive 配置（可选）
    onedrive_config = None
    if os.path.exists('onedrive_config.json'):
        try:
            onedrive_config = Config('onedrive_config.json')
            logger.info("✓ OneDrive 配置已加载")
        except Exception as e:
            logger.warning(f"OneDrive 配置加载失败: {e}")

    # 创建下载器
    downloader_bot = TelegramDownloaderBot(tg_config, onedrive_config)

    # 创建 Bot 控制器
    bot_controller = BotController(bot_token, admin_ids, downloader_bot)

    # 启动
    await downloader_bot.start()
    await bot_controller.start()

    logger.info("✓ Bot 控制已启用")
    logger.info(f"  管理员 ID: {admin_ids}")

    # 运行
    try:
        await downloader_bot.client.run_until_disconnected()
    except KeyboardInterrupt:
        logger.info("收到停止信号...")
    finally:
        await downloader_bot.stop()
        await bot_controller.bot.disconnect()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    asyncio.run(main_with_bot())
