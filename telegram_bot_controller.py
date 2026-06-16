#!/usr/bin/env python3
"""
Telegram Bot Controller
通过 Telegram Bot 远程控制下载器

命令:
基础命令:
/start - 启动信息
/help - 详细帮助
/status - 查看状态
/stats - 查看统计

频道管理:
/list - 列出所有监听频道
/add <频道> - 添加监听频道
/remove <频道> - 移除监听频道
/test <频道> - 测试频道连接
/info <频道> - 查看频道信息

下载控制:
/pause - 暂停下载
/resume - 恢复下载
/history <频道> [数量] - 下载历史消息
/recent [数量] - 查看最近下载

查询功能:
/search <关键词> - 搜索已下载文件
/logs [行数] - 查看最新日志
/disk - 查看磁盘空间
/speed - 查看下载速度

系统管理:
/config - 查看配置
/filter - 查看过滤规则
/clear - 清理缓存
/restart - 重启下载器
/update - 检查更新
/export - 导出下载记录
/backup - 备份配置
"""

import os
import sys
import asyncio
import logging
import json
import shutil
from datetime import datetime, timedelta
from typing import Optional, List
from pathlib import Path

from telethon import TelegramClient, events
from telethon.tl.types import User, Channel
from telethon.errors import ChannelPrivateError, UsernameInvalidError

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
        self.start_time = datetime.now()

        # 创建 Bot 客户端（不要立即 start）
        self.bot = TelegramClient(
            'sessions/bot_session',
            downloader_bot.tg_config.get('api_id'),
            downloader_bot.tg_config.get('api_hash')
        )

    def is_admin(self, user_id: int) -> bool:
        """检查是否是管理员"""
        return user_id in self.admin_ids

    def get_uptime(self) -> str:
        """获取运行时间"""
        uptime = datetime.now() - self.start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if days > 0:
            return f"{days}天 {hours}小时 {minutes}分钟"
        elif hours > 0:
            return f"{hours}小时 {minutes}分钟"
        else:
            return f"{minutes}分钟 {seconds}秒"

    def get_disk_usage(self, path: str = "./downloads") -> dict:
        """获取磁盘使用情况"""
        try:
            total, used, free = shutil.disk_usage(path)
            return {
                "total": total,
                "used": used,
                "free": free,
                "percent": (used / total) * 100
            }
        except:
            return None

    def get_recent_files(self, limit: int = 10) -> List[dict]:
        """获取最近下载的文件"""
        download_path = Path(self.downloader_bot.tg_config.get('download_path', './downloads'))
        if not download_path.exists():
            return []

        files = []
        for file_path in download_path.rglob('*'):
            if file_path.is_file():
                files.append({
                    'name': file_path.name,
                    'size': file_path.stat().st_size,
                    'time': datetime.fromtimestamp(file_path.stat().st_mtime),
                    'path': str(file_path.relative_to(download_path))
                })

        # 按时间排序
        files.sort(key=lambda x: x['time'], reverse=True)
        return files[:limit]

    def search_files(self, keyword: str, limit: int = 20) -> List[dict]:
        """搜索文件"""
        download_path = Path(self.downloader_bot.tg_config.get('download_path', './downloads'))
        if not download_path.exists():
            return []

        files = []
        keyword_lower = keyword.lower()

        for file_path in download_path.rglob('*'):
            if file_path.is_file() and keyword_lower in file_path.name.lower():
                files.append({
                    'name': file_path.name,
                    'size': file_path.stat().st_size,
                    'path': str(file_path.relative_to(download_path))
                })
                if len(files) >= limit:
                    break

        return files

    def get_log_tail(self, lines: int = 50) -> str:
        """获取日志尾部"""
        log_file = 'tg_downloader.log'
        if not os.path.exists(log_file):
            return "日志文件不存在"

        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                log_lines = f.readlines()
                return ''.join(log_lines[-lines:])
        except Exception as e:
            return f"读取日志失败: {e}"

    def format_size(self, bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes < 1024.0:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.2f} PB"

    async def start(self):
        """启动 Bot"""
        # 先启动 Bot 客户端
        await self.bot.start(bot_token=self.bot_token)
        logger.info("Bot 控制器已启动")

        @self.bot.on(events.NewMessage(pattern='/start'))
        async def cmd_start(event):
            if not self.is_admin(event.sender_id):
                await event.reply("❌ 无权限")
                return

            await event.reply(
                "🤖 **TgBackup 控制面板**\n\n"
                "📋 **基础命令**\n"
                "/help - 详细帮助\n"
                "/status - 查看状态\n"
                "/stats - 查看统计\n\n"
                "📺 **频道管理**\n"
                "/list - 列出频道\n"
                "/add <频道> - 添加频道\n"
                "/remove <频道> - 移除频道\n"
                "/test <频道> - 测试连接\n"
                "/info <频道> - 频道信息\n\n"
                "⬇️ **下载控制**\n"
                "/pause - 暂停下载\n"
                "/resume - 恢复下载\n"
                "/history <频道> [数量] - 下载历史\n"
                "/recent [数量] - 最近下载\n"
                "/browse <频道> - 浏览历史消息\n"
                "/download <消息ID> - 下载指定消息\n\n"
                "💡 **快捷功能**\n"
                "直接转发消息给我 - 自动下载媒体\n\n"
                "🔍 **查询功能**\n"
                "/search <关键词> - 搜索文件\n"
                "/logs [行数] - 查看日志\n"
                "/disk - 磁盘空间\n"
                "/speed - 下载速度\n\n"
                "⚙️ **系统管理**\n"
                "/config - 查看配置\n"
                "/filter - 过滤规则\n"
                "/clear - 清理缓存\n"
                "/export - 导出记录\n"
                "/backup - 备份配置"
            )

        @self.bot.on(events.NewMessage(pattern='/help'))
        async def cmd_help(event):
            if not self.is_admin(event.sender_id):
                return

            await event.reply(
                "📖 **TgBackup 详细帮助**\n\n"
                "**基础命令**\n"
                "`/status` - 查看运行状态、运行时间\n"
                "`/stats` - 查看下载统计信息\n\n"
                "**频道管理**\n"
                "`/list` - 列出所有监听的频道\n"
                "`/add @channel` - 添加新频道监听\n"
                "`/remove @channel` - 移除频道监听\n"
                "`/test @channel` - 测试频道连接\n"
                "`/info @channel` - 查看频道详细信息\n\n"
                "**下载控制**\n"
                "`/pause` - 暂停所有下载任务\n"
                "`/resume` - 恢复所有下载任务\n"
                "`/history @channel 100` - 下载指定数量历史消息\n"
                "`/history @channel 0` - 下载全部历史消息\n"
                "`/browse @channel` - 浏览频道历史（显示最近 20 条）\n"
                "`/download 12345` - 下载指定消息 ID 的媒体\n"
                "`/recent 10` - 查看最近 10 个下载\n\n"
                "**快捷下载**\n"
                "💡 直接转发消息给我，自动下载媒体文件\n"
                "支持：照片、视频、文档、音频\n\n"
                "**查询功能**\n"
                "`/search 关键词` - 搜索已下载文件\n"
                "`/logs 50` - 查看最新 50 行日志\n"
                "`/disk` - 查看磁盘使用情况\n"
                "`/speed` - 查看下载速度统计\n\n"
                "**系统管理**\n"
                "`/config` - 查看当前配置\n"
                "`/filter` - 查看文件过滤规则\n"
                "`/clear` - 清理下载缓存\n"
                "`/export` - 导出下载记录为 CSV\n"
                "`/backup` - 备份当前配置"
            )

        @self.bot.on(events.NewMessage(pattern='/status'))
        async def cmd_status(event):
            if not self.is_admin(event.sender_id):
                return

            status = "✅ 运行中" if not self.paused else "⏸️ 已暂停"
            channels_count = len(self.downloader_bot.channels)
            uptime = self.get_uptime()

            # 获取磁盘信息
            disk = self.get_disk_usage()
            disk_info = ""
            if disk:
                disk_info = f"\n💾 磁盘空间: {self.format_size(disk['free'])} / {self.format_size(disk['total'])} 可用"

            await event.reply(
                f"📊 **系统状态**\n\n"
                f"状态: {status}\n"
                f"监听频道: {channels_count} 个\n"
                f"运行时间: {uptime}"
                f"{disk_info}"
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

        @self.bot.on(events.NewMessage(pattern='/recent'))
        async def cmd_recent(event):
            """查看最近下载的文件"""
            if not self.is_admin(event.sender_id):
                return

            parts = event.message.text.split()
            limit = int(parts[1]) if len(parts) > 1 else 10

            files = self.get_recent_files(limit)
            if not files:
                await event.reply("📭 还没有下载任何文件")
                return

            text = f"📥 **最近 {len(files)} 个下载**\n\n"
            for i, file in enumerate(files, 1):
                size = self.format_size(file['size'])
                time_str = file['time'].strftime('%m-%d %H:%M')
                text += f"{i}. `{file['name']}`\n"
                text += f"   📦 {size} | 🕐 {time_str}\n\n"

            await event.reply(text)

        @self.bot.on(events.NewMessage(pattern='/search'))
        async def cmd_search(event):
            """搜索已下载的文件"""
            if not self.is_admin(event.sender_id):
                return

            parts = event.message.text.split(maxsplit=1)
            if len(parts) < 2:
                await event.reply("❌ 用法: /search <关键词>")
                return

            keyword = parts[1]
            files = self.search_files(keyword)

            if not files:
                await event.reply(f"🔍 未找到包含 '{keyword}' 的文件")
                return

            text = f"🔍 **搜索结果: '{keyword}'**\n\n"
            text += f"找到 {len(files)} 个文件:\n\n"

            for i, file in enumerate(files[:10], 1):  # 只显示前10个
                size = self.format_size(file['size'])
                text += f"{i}. `{file['name']}`\n"
                text += f"   📦 {size} | 📁 {file['path']}\n\n"

            if len(files) > 10:
                text += f"\n...还有 {len(files) - 10} 个结果"

            await event.reply(text)

        @self.bot.on(events.NewMessage(pattern='/disk'))
        async def cmd_disk(event):
            """查看磁盘空间"""
            if not self.is_admin(event.sender_id):
                return

            disk = self.get_disk_usage()
            if not disk:
                await event.reply("❌ 无法获取磁盘信息")
                return

            total = self.format_size(disk['total'])
            used = self.format_size(disk['used'])
            free = self.format_size(disk['free'])
            percent = disk['percent']

            # 进度条
            bar_length = 20
            filled = int(bar_length * percent / 100)
            bar = '█' * filled + '░' * (bar_length - filled)

            await event.reply(
                f"💾 **磁盘使用情况**\n\n"
                f"总容量: {total}\n"
                f"已使用: {used}\n"
                f"可用: {free}\n"
                f"使用率: {percent:.1f}%\n\n"
                f"[{bar}] {percent:.1f}%"
            )

        @self.bot.on(events.NewMessage(pattern='/logs'))
        async def cmd_logs(event):
            """查看最新日志"""
            if not self.is_admin(event.sender_id):
                return

            parts = event.message.text.split()
            lines = int(parts[1]) if len(parts) > 1 else 30

            log_content = self.get_log_tail(lines)

            # 限制消息长度
            if len(log_content) > 4000:
                log_content = log_content[-4000:]
                log_content = "...(日志过长，仅显示最后部分)\n\n" + log_content

            await event.reply(f"📋 **最新 {lines} 行日志**\n\n```\n{log_content}\n```")

        @self.bot.on(events.NewMessage(pattern='/test'))
        async def cmd_test(event):
            """测试频道连接"""
            if not self.is_admin(event.sender_id):
                return

            parts = event.message.text.split()
            if len(parts) < 2:
                await event.reply("❌ 用法: /test @channel")
                return

            channel_input = parts[1]
            await event.reply(f"🔄 正在测试 {channel_input}...")

            try:
                entity = await self.downloader_bot.client.get_entity(channel_input)
                await event.reply(
                    f"✅ **连接成功**\n\n"
                    f"频道: {getattr(entity, 'title', 'N/A')}\n"
                    f"用户名: @{getattr(entity, 'username', 'N/A')}\n"
                    f"类型: {'频道' if isinstance(entity, Channel) else '群组'}\n"
                    f"状态: 可访问"
                )
            except ChannelPrivateError:
                await event.reply(f"❌ 频道 {channel_input} 是私有的或无权访问")
            except UsernameInvalidError:
                await event.reply(f"❌ 无效的频道用户名: {channel_input}")
            except Exception as e:
                await event.reply(f"❌ 测试失败: {e}")

        @self.bot.on(events.NewMessage(pattern='/info'))
        async def cmd_info(event):
            """查看频道详细信息"""
            if not self.is_admin(event.sender_id):
                return

            parts = event.message.text.split()
            if len(parts) < 2:
                await event.reply("❌ 用法: /info @channel")
                return

            channel_input = parts[1]

            try:
                entity = await self.downloader_bot.client.get_entity(channel_input)

                info_text = f"📺 **频道信息**\n\n"
                info_text += f"标题: {getattr(entity, 'title', 'N/A')}\n"
                info_text += f"用户名: @{getattr(entity, 'username', 'N/A')}\n"
                info_text += f"ID: `{entity.id}`\n"

                if hasattr(entity, 'participants_count'):
                    info_text += f"成员数: {entity.participants_count:,}\n"

                if hasattr(entity, 'about'):
                    about = entity.about[:100] + '...' if len(entity.about) > 100 else entity.about
                    info_text += f"\n简介: {about}"

                await event.reply(info_text)
            except Exception as e:
                await event.reply(f"❌ 获取信息失败: {e}")

        @self.bot.on(events.NewMessage(pattern='/speed'))
        async def cmd_speed(event):
            """查看下载速度统计"""
            if not self.is_admin(event.sender_id):
                return

            stats = self.downloader_bot.downloader.get_stats()

            # 计算平均速度（粗略估算）
            uptime_seconds = (datetime.now() - self.start_time).total_seconds()
            if uptime_seconds > 0:
                avg_speed = stats['bytes_downloaded'] / uptime_seconds
                avg_speed_text = self.format_size(int(avg_speed)) + "/s"
            else:
                avg_speed_text = "N/A"

            await event.reply(
                f"🚀 **下载速度统计**\n\n"
                f"总下载: {self.format_size(stats['bytes_downloaded'])}\n"
                f"运行时间: {self.get_uptime()}\n"
                f"平均速度: {avg_speed_text}\n"
                f"已下载: {stats['downloaded']} 个文件"
            )

        @self.bot.on(events.NewMessage(pattern='/filter'))
        async def cmd_filter(event):
            """查看过滤规则"""
            if not self.is_admin(event.sender_id):
                return

            tg_config = self.downloader_bot.tg_config

            media_types = tg_config.get('media_types', [])
            size_limit = tg_config.get('file_size_limit', 0)
            whitelist = tg_config.get('extensions_whitelist', [])
            blacklist = tg_config.get('extensions_blacklist', [])

            text = "🎯 **文件过滤规则**\n\n"
            text += f"📁 媒体类型: {', '.join(media_types)}\n"
            text += f"📦 大小限制: {self.format_size(size_limit)}\n\n"

            if whitelist:
                text += f"✅ 白名单: {', '.join(whitelist)}\n"
            else:
                text += f"✅ 白名单: 全部允许\n"

            if blacklist:
                text += f"❌ 黑名单: {', '.join(blacklist)}\n"
            else:
                text += f"❌ 黑名单: 无\n"

            await event.reply(text)

        @self.bot.on(events.NewMessage(pattern='/clear'))
        async def cmd_clear(event):
            """清理缓存"""
            if not self.is_admin(event.sender_id):
                return

            await event.reply("🔄 正在清理缓存...")

            try:
                # 清理下载记录
                record_file = 'downloaded_messages.json'
                if os.path.exists(record_file):
                    os.remove(record_file)

                await event.reply("✅ 缓存已清理\n\n清理内容:\n- 下载记录")
            except Exception as e:
                await event.reply(f"❌ 清理失败: {e}")

        @self.bot.on(events.NewMessage(pattern='/export'))
        async def cmd_export(event):
            """导出下载记录"""
            if not self.is_admin(event.sender_id):
                return

            await event.reply("📊 正在导出记录...")

            try:
                stats = self.downloader_bot.downloader.get_stats()
                files = self.get_recent_files(1000)  # 导出最近1000个

                # 生成 CSV 内容
                csv_content = "文件名,大小,下载时间,路径\n"
                for file in files:
                    csv_content += f'"{file["name"]}",{file["size"]},"{file["time"]}","{file["path"]}"\n'

                # 保存到文件
                export_file = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                with open(export_file, 'w', encoding='utf-8') as f:
                    f.write(csv_content)

                await event.reply(
                    f"✅ **导出完成**\n\n"
                    f"文件: `{export_file}`\n"
                    f"记录数: {len(files)}\n"
                    f"总大小: {self.format_size(sum(f['size'] for f in files))}"
                )

                # 发送文件
                await event.reply(file=export_file)
            except Exception as e:
                await event.reply(f"❌ 导出失败: {e}")

        @self.bot.on(events.NewMessage(pattern='/backup'))
        async def cmd_backup(event):
            """备份配置"""
            if not self.is_admin(event.sender_id):
                return

            await event.reply("💾 正在备份配置...")

            try:
                backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.makedirs(backup_dir, exist_ok=True)

                # 备份配置文件
                if os.path.exists('telegram_config.json'):
                    shutil.copy2('telegram_config.json', f"{backup_dir}/telegram_config.json")

                if os.path.exists('onedrive_config.json'):
                    shutil.copy2('onedrive_config.json', f"{backup_dir}/onedrive_config.json")

                # 备份下载记录
                if os.path.exists('downloaded_messages.json'):
                    shutil.copy2('downloaded_messages.json', f"{backup_dir}/downloaded_messages.json")

                # 压缩
                shutil.make_archive(backup_dir, 'zip', backup_dir)
                shutil.rmtree(backup_dir)

                await event.reply(
                    f"✅ **备份完成**\n\n"
                    f"文件: `{backup_dir}.zip`\n"
                    f"包含:\n"
                    f"- Telegram 配置\n"
                    f"- OneDrive 配置\n"
                    f"- 下载记录"
                )

                # 发送备份文件
                await event.reply(file=f"{backup_dir}.zip")
            except Exception as e:
                await event.reply(f"❌ 备份失败: {e}")

        @self.bot.on(events.NewMessage(pattern='/browse'))
        async def cmd_browse(event):
            """浏览频道历史消息"""
            if not self.is_admin(event.sender_id):
                return

            parts = event.message.text.split()
            if len(parts) < 2:
                await event.reply("❌ 用法: /browse @channel [数量]")
                return

            channel_input = parts[1]
            limit = int(parts[2]) if len(parts) > 2 else 20

            await event.reply(f"🔄 正在浏览 {channel_input} 最近 {limit} 条消息...")

            try:
                entity = await self.downloader_bot.client.get_entity(channel_input)
                chat_title = getattr(entity, 'title', channel_input)

                messages = []
                async for message in self.downloader_bot.client.iter_messages(entity, limit=limit):
                    if message.media:
                        # 获取媒体类型
                        media_type = "unknown"
                        if message.photo:
                            media_type = "📷 照片"
                        elif message.video:
                            media_type = "🎥 视频"
                        elif message.document:
                            media_type = "📄 文档"
                        elif message.audio:
                            media_type = "🎵 音频"

                        # 获取文件大小
                        file_size = ""
                        if hasattr(message.media, 'document'):
                            size = message.media.document.size
                            file_size = f" ({self.format_size(size)})"

                        # 获取文件名
                        file_name = ""
                        if message.file and message.file.name:
                            file_name = f"\n   📝 {message.file.name}"

                        messages.append({
                            'id': message.id,
                            'type': media_type,
                            'size': file_size,
                            'name': file_name,
                            'date': message.date.strftime('%m-%d %H:%M'),
                            'text': message.text[:30] + '...' if message.text and len(message.text) > 30 else message.text or ''
                        })

                if not messages:
                    await event.reply(f"📭 频道 {chat_title} 最近 {limit} 条消息中没有媒体")
                    return

                # 分页显示
                text = f"📺 **{chat_title}**\n"
                text += f"最近 {len(messages)} 条媒体消息:\n\n"

                for msg in messages:
                    text += f"**消息 ID: {msg['id']}** | {msg['date']}\n"
                    text += f"{msg['type']}{msg['size']}"
                    if msg['name']:
                        text += msg['name']
                    if msg['text']:
                        text += f"\n💬 {msg['text']}"
                    text += "\n\n"

                text += f"💡 使用 /download {messages[0]['id']} 下载指定消息"

                # Telegram 消息长度限制，分批发送
                if len(text) > 4000:
                    chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
                    for chunk in chunks:
                        await event.reply(chunk)
                else:
                    await event.reply(text)

            except Exception as e:
                await event.reply(f"❌ 浏览失败: {e}")

        @self.bot.on(events.NewMessage(pattern='/download'))
        async def cmd_download_by_id(event):
            """下载指定消息 ID 的媒体"""
            if not self.is_admin(event.sender_id):
                return

            parts = event.message.text.split()
            if len(parts) < 2:
                await event.reply(
                    "❌ 用法: /download <消息ID> [频道]\n\n"
                    "示例:\n"
                    "/download 12345\n"
                    "/download 12345 @channel"
                )
                return

            message_id = int(parts[1])
            channel_input = parts[2] if len(parts) > 2 else None

            await event.reply(f"🔄 正在下载消息 {message_id}...")

            try:
                # 如果指定了频道
                if channel_input:
                    entity = await self.downloader_bot.client.get_entity(channel_input)
                    message = await self.downloader_bot.client.get_messages(entity, ids=message_id)
                else:
                    # 尝试从已监听的频道中查找
                    message = None
                    for channel in self.downloader_bot.channels:
                        try:
                            msg = await self.downloader_bot.client.get_messages(channel, ids=message_id)
                            if msg and msg.media:
                                message = msg
                                break
                        except:
                            continue

                if not message or not message.media:
                    await event.reply(f"❌ 未找到消息 {message_id} 或消息不包含媒体")
                    return

                # 下载
                chat_title = "Manual_Download"
                result = await self.downloader_bot.downloader.download_media(message, chat_title)

                if result:
                    await event.reply(f"✅ 下载完成！\n\n文件: {result.get('file_name', 'N/A')}")
                else:
                    await event.reply(f"❌ 下载失败或文件已存在")

            except Exception as e:
                await event.reply(f"❌ 下载失败: {e}")

        @self.bot.on(events.NewMessage())
        async def handle_forwarded_message(event):
            """处理转发的消息，自动下载媒体"""
            if not self.is_admin(event.sender_id):
                return

            # 忽略命令消息
            if event.message.text and event.message.text.startswith('/'):
                return

            # 检查是否是转发的消息
            if not event.message.fwd_from and not event.message.media:
                return

            # 检查是否有媒体
            if not event.message.media:
                return

            await event.reply("🔄 检测到媒体文件，开始下载...")

            try:
                # 获取来源信息
                source_name = "Forwarded"
                if event.message.fwd_from:
                    if event.message.fwd_from.from_name:
                        source_name = event.message.fwd_from.from_name
                    elif event.message.fwd_from.from_id:
                        try:
                            entity = await event.client.get_entity(event.message.fwd_from.from_id)
                            source_name = getattr(entity, 'title', getattr(entity, 'username', 'Unknown'))
                        except:
                            pass

                # 下载
                result = await self.downloader_bot.downloader.download_media(
                    event.message,
                    f"Manual/{source_name}"
                )

                if result:
                    file_name = result.get('file_name', 'N/A')
                    file_size = result.get('file_size', 0)
                    await event.reply(
                        f"✅ **下载完成**\n\n"
                        f"文件: `{file_name}`\n"
                        f"大小: {self.format_size(file_size)}\n"
                        f"来源: {source_name}"
                    )
                else:
                    await event.reply("⏭️ 文件已存在或不符合过滤条件")

            except Exception as e:
                await event.reply(f"❌ 下载失败: {e}")

        logger.info("✓ Bot 命令已注册 (28+ 命令，包含转发下载)")

    def should_process_message(self) -> bool:
        """是否应该处理消息（暂停检查）"""
        return not self.paused


async def main_with_bot():
    """带 Bot 控制的主函数"""
    # 加载配置
    try:
        tg_config = TelegramConfig('config/telegram_config.json')
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Telegram 配置错误: {e}")
        sys.exit(1)

    # 检查 Bot Token
    bot_token = tg_config.get('bot_token')
    admin_ids = tg_config.get('admin_ids', [])

    if not bot_token:
        logger.warning("未配置 bot_token，Bot 控制功能将不可用")
        logger.info("如需启用，请在 config/telegram_config.json 中添加:")
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
    if os.path.exists('config/onedrive_config.json'):
        try:
            onedrive_config = Config('config/onedrive_config.json')
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
