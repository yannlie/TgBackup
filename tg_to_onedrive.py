#!/usr/bin/env python3
"""
TG Media to OneDrive Auto Uploader
自动将 telegram_media_downloader 下载的文件上传到 OneDrive

Version: 2.0.0
"""

import os
import sys
import time
import json
import logging
import argparse
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

__version__ = "2.0.0"

# 配置日志
def setup_logging(log_level=logging.INFO, log_file='tg_to_onedrive.log'):
    """设置日志配置"""
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()


class Config:
    """配置管理类"""

    def __init__(self, config_path='onedrive_config.json'):
        self.config_path = config_path
        self.data = self._load()

    def _load(self) -> dict:
        """加载配置"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(
                f"配置文件不存在: {self.config_path}\n"
                "请先运行 python get_refresh_token.py 创建配置文件"
            )

        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 验证必需字段
        required = ['client_id', 'client_secret', 'refresh_token']
        missing = [field for field in required if not config.get(field)]
        if missing:
            raise ValueError(f"配置文件缺少必需字段: {', '.join(missing)}")

        return config

    def save(self):
        """保存配置"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def get(self, key: str, default=None):
        """获取配置值"""
        return self.data.get(key, default)

    def set(self, key: str, value):
        """设置配置值"""
        self.data[key] = value


class OneDriveUploader:
    """OneDrive 上传器（优化版）"""

    def __init__(self, config: Config):
        self.config = config
        self.access_token = None
        self.token_expires_at = 0
        self.session = self._create_session()
        self.upload_stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'bytes_uploaded': 0
        }

    def _create_session(self):
        """创建带重试机制的会话"""
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('https://', adapter)
        return session

    def _get_access_token(self):
        """获取或刷新 Access Token"""
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token

        logger.info("刷新 OneDrive Access Token...")

        token_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
        data = {
            'client_id': self.config.get('client_id'),
            'client_secret': self.config.get('client_secret'),
            'refresh_token': self.config.get('refresh_token'),
            'grant_type': 'refresh_token',
            'scope': 'https://graph.microsoft.com/Files.ReadWrite.All offline_access'
        }

        try:
            response = self.session.post(token_url, data=data, timeout=30)
            response.raise_for_status()
            token_data = response.json()

            self.access_token = token_data['access_token']
            # 提前 5 分钟刷新
            self.token_expires_at = time.time() + token_data['expires_in'] - 300

            # 更新 refresh_token（如果返回了新的）
            if 'refresh_token' in token_data:
                self.config.set('refresh_token', token_data['refresh_token'])
                self.config.save()

            logger.info("Token 刷新成功")
            return self.access_token

        except Exception as e:
            logger.error(f"刷新 Token 失败: {e}")
            raise

    def upload_file(self, local_path: Path, remote_path: Optional[str] = None) -> bool:
        """
        上传文件到 OneDrive

        Args:
            local_path: 本地文件路径
            remote_path: OneDrive 远程路径（相对于配置的 base_path）

        Returns:
            bool: 上传是否成功
        """
        local_path = Path(local_path)
        if not local_path.exists():
            logger.error(f"文件不存在: {local_path}")
            return False

        # 构建远程路径
        if remote_path is None:
            remote_path = local_path.name

        base_path = self.config.get('base_path', '/TG_Media')
        full_remote_path = f"{base_path}/{remote_path}".replace('//', '/')

        file_size = local_path.stat().st_size
        logger.info(f"开始上传: {local_path.name} ({file_size / 1024 / 1024:.2f} MB) -> {full_remote_path}")

        self.upload_stats['total'] += 1

        try:
            token = self._get_access_token()

            # 小文件直接上传 (< 4MB)
            if file_size < 4 * 1024 * 1024:
                success = self._simple_upload(local_path, full_remote_path, token)
            else:
                # 大文件分块上传
                success = self._chunked_upload(local_path, full_remote_path, token)

            if success:
                self.upload_stats['success'] += 1
                self.upload_stats['bytes_uploaded'] += file_size
            else:
                self.upload_stats['failed'] += 1

            return success

        except Exception as e:
            logger.error(f"上传失败: {local_path.name}, 错误: {e}")
            self.upload_stats['failed'] += 1
            return False

    def _simple_upload(self, local_path: Path, remote_path: str, token: str) -> bool:
        """简单上传（小文件）"""
        url = f"https://graph.microsoft.com/v1.0/me/drive/root:{remote_path}:/content"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/octet-stream'
        }

        with open(local_path, 'rb') as f:
            response = self.session.put(url, headers=headers, data=f, timeout=300)

        if response.status_code in [200, 201]:
            logger.info(f"✓ 上传成功: {local_path.name}")
            return True
        else:
            logger.error(f"上传失败: {response.status_code} - {response.text}")
            return False

    def _chunked_upload(self, local_path: Path, remote_path: str, token: str) -> bool:
        """分块上传（大文件）"""
        # 创建上传会话
        create_session_url = f"https://graph.microsoft.com/v1.0/me/drive/root:{remote_path}:/createUploadSession"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        response = self.session.post(create_session_url, headers=headers, json={}, timeout=30)
        if response.status_code != 200:
            logger.error(f"创建上传会话失败: {response.text}")
            return False

        upload_url = response.json()['uploadUrl']
        file_size = local_path.stat().st_size
        chunk_size = self.config.get('chunk_size', 10) * 1024 * 1024  # 默认 10MB

        # 分块上传
        with open(local_path, 'rb') as f:
            chunk_start = 0
            while chunk_start < file_size:
                chunk_end = min(chunk_start + chunk_size, file_size)
                chunk_data = f.read(chunk_size)

                headers = {
                    'Content-Length': str(len(chunk_data)),
                    'Content-Range': f'bytes {chunk_start}-{chunk_end - 1}/{file_size}'
                }

                response = self.session.put(upload_url, headers=headers, data=chunk_data, timeout=300)

                if response.status_code not in [200, 201, 202]:
                    logger.error(f"分块上传失败: {response.status_code} - {response.text}")
                    return False

                progress = (chunk_end / file_size) * 100
                logger.info(f"上传进度: {progress:.1f}% ({chunk_end}/{file_size} bytes)")

                chunk_start = chunk_end

        logger.info(f"✓ 上传成功: {local_path.name}")
        return True

    def get_stats(self) -> Dict:
        """获取上传统计"""
        return self.upload_stats.copy()


class UploadFilter:
    """上传过滤器"""

    def __init__(self, config: Config):
        self.config = config
        self.excluded_extensions = set(config.get('excluded_extensions', []))
        self.min_size = config.get('min_file_size', 0)  # bytes
        self.max_size = config.get('max_file_size', 250 * 1024 * 1024 * 1024)  # 250GB

    def should_upload(self, file_path: Path) -> tuple[bool, Optional[str]]:
        """
        判断文件是否应该上传

        Returns:
            (should_upload, reason): 是否上传和原因
        """
        # 检查扩展名
        if file_path.suffix.lower() in self.excluded_extensions:
            return False, f"文件类型被排除: {file_path.suffix}"

        # 检查文件大小
        try:
            size = file_path.stat().st_size
        except OSError:
            return False, "无法获取文件大小"

        if size < self.min_size:
            return False, f"文件太小: {size} < {self.min_size}"

        if size > self.max_size:
            return False, f"文件太大: {size} > {self.max_size}"

        return True, None


class DownloadHandler(FileSystemEventHandler):
    """文件下载完成处理器（优化版）"""

    def __init__(
        self,
        uploader: OneDriveUploader,
        watch_path: Path,
        upload_filter: UploadFilter,
        min_stable_time: int = 5,
        auto_delete: bool = False
    ):
        self.uploader = uploader
        self.watch_path = Path(watch_path)
        self.upload_filter = upload_filter
        self.min_stable_time = min_stable_time
        self.auto_delete = auto_delete
        self.processing_files = {}  # 正在处理的文件
        self.uploaded_files = set()  # 已上传的文件
        self._load_uploaded_record()

    def _load_uploaded_record(self):
        """加载已上传文件记录"""
        record_file = 'uploaded_files.json'
        if os.path.exists(record_file):
            with open(record_file, 'r', encoding='utf-8') as f:
                self.uploaded_files = set(json.load(f))
            logger.info(f"已加载 {len(self.uploaded_files)} 条上传记录")

    def _save_uploaded_record(self):
        """保存已上传文件记录"""
        with open('uploaded_files.json', 'w', encoding='utf-8') as f:
            json.dump(list(self.uploaded_files), f, indent=2, ensure_ascii=False)

    def _calculate_file_hash(self, file_path: Path) -> str:
        """计算文件哈希（用于去重）"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                # 只读取前 1MB 和后 1MB 计算哈希（提高性能）
                chunk = f.read(1024 * 1024)
                hash_md5.update(chunk)

                file_size = file_path.stat().st_size
                if file_size > 2 * 1024 * 1024:
                    f.seek(-1024 * 1024, 2)
                    chunk = f.read(1024 * 1024)
                    hash_md5.update(chunk)

            return f"{file_path.name}_{file_size}_{hash_md5.hexdigest()[:8]}"
        except Exception as e:
            logger.error(f"计算文件哈希失败: {e}")
            return f"{file_path.name}_{file_path.stat().st_size}"

    def on_created(self, event):
        """文件创建事件"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # 忽略临时文件和隐藏文件
        if file_path.name.startswith('.') or file_path.suffix in ['.tmp', '.part', '.crdownload']:
            return

        logger.info(f"检测到新文件: {file_path.name}")
        self.processing_files[str(file_path)] = time.time()

    def on_modified(self, event):
        """文件修改事件"""
        if event.is_directory:
            return

        file_path = str(event.src_path)
        if file_path in self.processing_files:
            # 更新修改时间
            self.processing_files[file_path] = time.time()

    def check_stable_files(self):
        """检查稳定的文件并上传"""
        current_time = time.time()
        stable_files = []

        for file_path, last_modified in list(self.processing_files.items()):
            # 文件在 min_stable_time 秒内没有修改，认为下载完成
            if current_time - last_modified >= self.min_stable_time:
                stable_files.append(file_path)
                del self.processing_files[file_path]

        for file_path in stable_files:
            self._upload_file(file_path)

    def _upload_file(self, file_path: str):
        """上传单个文件"""
        file_path = Path(file_path)

        # 检查文件是否存在
        if not file_path.exists():
            logger.warning(f"文件不存在，跳过: {file_path}")
            return

        # 过滤检查
        should_upload, reason = self.upload_filter.should_upload(file_path)
        if not should_upload:
            logger.info(f"跳过文件: {file_path.name}, 原因: {reason}")
            return

        # 检查是否已上传
        file_key = self._calculate_file_hash(file_path)
        if file_key in self.uploaded_files:
            logger.info(f"文件已上传，跳过: {file_path.name}")
            return

        # 构建远程路径（保留下载目录结构）
        try:
            relative_path = file_path.relative_to(self.watch_path)
            remote_path = str(relative_path).replace('\\', '/')
        except ValueError:
            remote_path = file_path.name

        # 上传
        if self.uploader.upload_file(file_path, remote_path):
            self.uploaded_files.add(file_key)
            self._save_uploaded_record()

            # 自动删除本地文件
            if self.auto_delete:
                try:
                    os.remove(file_path)
                    logger.info(f"已删除本地文件: {file_path.name}")
                except Exception as e:
                    logger.error(f"删除文件失败: {e}")


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='TG Media to OneDrive Auto Uploader',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--config', '-c',
        default='onedrive_config.json',
        help='配置文件路径 (默认: onedrive_config.json)'
    )

    parser.add_argument(
        '--watch-path', '-w',
        help='监听目录路径 (优先级高于配置文件)'
    )

    parser.add_argument(
        '--auto-delete',
        action='store_true',
        help='上传成功后自动删除本地文件'
    )

    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='日志级别'
    )

    parser.add_argument(
        '--version', '-v',
        action='version',
        version=f'%(prog)s {__version__}'
    )

    return parser.parse_args()


def main():
    """主函数"""
    # 解析参数
    args = parse_args()

    # 设置日志级别
    logger.setLevel(getattr(logging, args.log_level))

    # 加载配置
    try:
        config = Config(args.config)
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"配置错误: {e}")
        sys.exit(1)

    # 获取监听路径
    watch_path = args.watch_path or config.get('watch_path', 'd:/telegram_downloads')

    # 检查监听目录
    if not os.path.exists(watch_path):
        logger.warning(f"监听目录不存在，将创建: {watch_path}")
        os.makedirs(watch_path, exist_ok=True)

    logger.info(f"TG to OneDrive Uploader v{__version__}")
    logger.info(f"配置文件: {args.config}")
    logger.info(f"监听目录: {watch_path}")
    logger.info(f"自动删除: {'开启' if args.auto_delete else '关闭'}")

    # 初始化组件
    try:
        uploader = OneDriveUploader(config)
        upload_filter = UploadFilter(config)
        handler = DownloadHandler(
            uploader,
            watch_path,
            upload_filter,
            min_stable_time=config.get('min_stable_time', 5),
            auto_delete=args.auto_delete
        )

        # 启动文件监听
        observer = Observer()
        observer.schedule(handler, watch_path, recursive=True)
        observer.start()

        logger.info("✓ 程序已启动，开始监听...")
        logger.info("按 Ctrl+C 停止程序")

        try:
            while True:
                # 定期检查稳定文件
                handler.check_stable_files()
                time.sleep(2)

                # 每小时输出一次统计
                if int(time.time()) % 3600 < 2:
                    stats = uploader.get_stats()
                    if stats['total'] > 0:
                        logger.info(
                            f"统计: 总计 {stats['total']} | "
                            f"成功 {stats['success']} | "
                            f"失败 {stats['failed']} | "
                            f"已上传 {stats['bytes_uploaded'] / 1024 / 1024:.2f} MB"
                        )

        except KeyboardInterrupt:
            logger.info("收到停止信号，正在关闭...")
            observer.stop()

        observer.join()

        # 输出最终统计
        stats = uploader.get_stats()
        logger.info("=" * 60)
        logger.info("最终统计:")
        logger.info(f"  总文件数: {stats['total']}")
        logger.info(f"  成功: {stats['success']}")
        logger.info(f"  失败: {stats['failed']}")
        logger.info(f"  总上传: {stats['bytes_uploaded'] / 1024 / 1024:.2f} MB")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"程序错误: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
