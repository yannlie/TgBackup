"""Rclone 云盘上传器"""
import os
import subprocess
import logging
import shutil
import zipfile
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class RcloneUploader:
    """Rclone 上传器，支持所有 rclone 支持的云盘"""

    def __init__(
        self,
        remote_dir: str,
        rclone_path: str = "rclone",
        before_upload_zip: bool = False,
        after_upload_delete: bool = False
    ):
        """
        Args:
            remote_dir: 远程目录 (格式: remote_name:/path)
            rclone_path: rclone 可执行文件路径
            before_upload_zip: 上传前压缩
            after_upload_delete: 上传后删除本地文件
        """
        self.remote_dir = remote_dir
        self.rclone_path = rclone_path
        self.before_upload_zip = before_upload_zip
        self.after_upload_delete = after_upload_delete

        # 检查 rclone 是否可用
        if not self._check_rclone():
            raise RuntimeError(f"rclone 不可用: {rclone_path}")

        logger.info(f"✓ Rclone 上传器已初始化: {remote_dir}")

    def _check_rclone(self) -> bool:
        """检查 rclone 是否可用"""
        try:
            result = subprocess.run(
                [self.rclone_path, "version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"rclone 检查失败: {e}")
            return False

    def upload_file(
        self,
        local_path: str,
        remote_path: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        上传文件到云盘

        Args:
            local_path: 本地文件路径
            remote_path: 远程路径（相对于 remote_dir），为 None 则使用文件名

        Returns:
            (成功, 消息)
        """
        local_file = Path(local_path)
        if not local_file.exists():
            return False, f"文件不存在: {local_path}"

        try:
            # 确定远程路径
            if remote_path is None:
                remote_path = local_file.name

            # 完整远程路径
            full_remote_path = f"{self.remote_dir}/{remote_path}"

            # 压缩（如果需要）
            upload_file = local_file
            if self.before_upload_zip:
                upload_file = self._zip_file(local_file)
                if upload_file is None:
                    return False, "压缩失败"
                full_remote_path += ".zip"

            logger.info(f"开始上传: {upload_file.name} -> {full_remote_path}")

            # 上传
            result = subprocess.run(
                [
                    self.rclone_path,
                    "copy",
                    str(upload_file),
                    full_remote_path,
                    "--progress",
                    "--stats", "5s"
                ],
                capture_output=True,
                text=True,
                timeout=3600  # 1小时超时
            )

            if result.returncode == 0:
                logger.info(f"✓ 上传成功: {full_remote_path}")

                # 删除本地文件（如果需要）
                if self.after_upload_delete:
                    try:
                        local_file.unlink()
                        logger.info(f"✓ 已删除本地文件: {local_file}")
                    except Exception as e:
                        logger.warning(f"删除本地文件失败: {e}")

                # 删除压缩文件
                if self.before_upload_zip and upload_file != local_file:
                    try:
                        upload_file.unlink()
                    except Exception:
                        pass

                return True, "上传成功"
            else:
                error_msg = result.stderr or result.stdout
                logger.error(f"上传失败: {error_msg}")
                return False, f"上传失败: {error_msg[:100]}"

        except subprocess.TimeoutExpired:
            return False, "上传超时（1小时）"
        except Exception as e:
            logger.error(f"上传异常: {e}")
            return False, f"上传异常: {e}"

    def _zip_file(self, file_path: Path) -> Optional[Path]:
        """
        压缩文件

        Args:
            file_path: 文件路径

        Returns:
            压缩文件路径，失败返回 None
        """
        try:
            zip_path = file_path.parent / f"{file_path.stem}.zip"
            logger.info(f"压缩文件: {file_path} -> {zip_path}")

            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.write(file_path, file_path.name)

            logger.info(f"✓ 压缩完成: {zip_path}")
            return zip_path
        except Exception as e:
            logger.error(f"压缩失败: {e}")
            return None

    def list_remotes(self) -> list:
        """列出所有配置的远程存储"""
        try:
            result = subprocess.run(
                [self.rclone_path, "listremotes"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return [line.strip() for line in result.stdout.split('\n') if line.strip()]
            return []
        except Exception as e:
            logger.error(f"列出远程存储失败: {e}")
            return []


if __name__ == "__main__":
    # 测试
    logging.basicConfig(level=logging.INFO)

    try:
        uploader = RcloneUploader(
            remote_dir="drive:/test",
            before_upload_zip=False,
            after_upload_delete=False
        )

        # 列出远程存储
        remotes = uploader.list_remotes()
        print(f"远程存储: {remotes}")

    except Exception as e:
        print(f"测试失败: {e}")
