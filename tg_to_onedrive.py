#!/usr/bin/env python3
"""
TG Media to OneDrive Auto Uploader
自动将 telegram_media_downloader 下载的文件上传到 OneDrive
"""

import os
import time
import json
import logging
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tg_to_onedrive.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class OneDriveUploader:
    """OneDrive 上传器"""

    def __init__(self, config_path='onedrive_config.json'):
        self.config = self._load_config(config_path)
        self.access_token = None
        self.token_expires_at = 0
        self.session = self._create_session()

    def _load_config(self, config_path):
        """加载配置文件"""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

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
            'client_id': self.config['client_id'],
            'client_secret': self.config['client_secret'],
            'refresh_token': self.config['refresh_token'],
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
                self.config['refresh_token'] = token_data['refresh_token']
                self._save_config()

            logger.info("Token 刷新成功")
            return self.access_token

        except Exception as e:
            logger.error(f"刷新 Token 失败: {e}")
            raise

    def _save_config(self):
        """保存配置（更新 refresh_token）"""
        with open('onedrive_config.json', 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def upload_file(self, local_path, remote_path=None):
        """
        上传文件到 OneDrive

        Args:
            local_path: 本地文件路径
            remote_path: OneDrive 远程路径（相对于配置的 base_path）
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

        try:
            token = self._get_access_token()

            # 小文件直接上传 (< 4MB)
            if file_size < 4 * 1024 * 1024:
                return self._simple_upload(local_path, full_remote_path, token)
            else:
                # 大文件分块上传
                return self._chunked_upload(local_path, full_remote_path, token)

        except Exception as e:
            logger.error(f"上传失败: {local_path.name}, 错误: {e}")
            return False

    def _simple_upload(self, local_path, remote_path, token):
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

    def _chunked_upload(self, local_path, remote_path, token):
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
        chunk_size = 10 * 1024 * 1024  # 10MB 分块

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


class DownloadHandler(FileSystemEventHandler):
    """文件下载完成处理器"""

    def __init__(self, uploader, watch_path, min_stable_time=5):
        self.uploader = uploader
        self.watch_path = Path(watch_path)
        self.min_stable_time = min_stable_time
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

    def _upload_file(self, file_path):
        """上传单个文件"""
        file_path = Path(file_path)

        # 检查是否已上传
        file_key = f"{file_path.name}_{file_path.stat().st_size}"
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


def main():
    """主函数"""
    # 配置路径
    WATCH_PATH = 'd:/telegram_downloads'  # telegram_media_downloader 下载目录
    CONFIG_PATH = 'onedrive_config.json'

    # 检查下载目录
    if not os.path.exists(WATCH_PATH):
        logger.warning(f"下载目录不存在，将创建: {WATCH_PATH}")
        os.makedirs(WATCH_PATH, exist_ok=True)

    # 初始化
    try:
        uploader = OneDriveUploader(CONFIG_PATH)
        handler = DownloadHandler(uploader, WATCH_PATH)

        # 启动文件监听
        observer = Observer()
        observer.schedule(handler, WATCH_PATH, recursive=True)
        observer.start()

        logger.info(f"开始监听目录: {WATCH_PATH}")
        logger.info("按 Ctrl+C 停止程序")

        try:
            while True:
                # 定期检查稳定文件
                handler.check_stable_files()
                time.sleep(2)

        except KeyboardInterrupt:
            logger.info("收到停止信号，正在关闭...")
            observer.stop()

        observer.join()

    except FileNotFoundError as e:
        logger.error(f"配置文件错误: {e}")
        logger.info("请先创建 onedrive_config.json 配置文件")
    except Exception as e:
        logger.error(f"程序错误: {e}", exc_info=True)


if __name__ == '__main__':
    main()
