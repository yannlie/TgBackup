"""文件路径和文件名生成器"""
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional


class PathGenerator:
    """路径生成器"""

    def __init__(
        self,
        base_path: str,
        file_path_prefix: List[str] = None,
        file_name_prefix: List[str] = None,
        file_name_split: str = " - ",
        date_format: str = "%Y_%m"
    ):
        """
        Args:
            base_path: 基础下载路径
            file_path_prefix: 路径前缀列表 (chat_title, media_datetime, media_type)
            file_name_prefix: 文件名前缀列表 (message_id, file_name, caption)
            file_name_split: 文件名分隔符
            date_format: 日期格式
        """
        self.base_path = Path(base_path)
        self.file_path_prefix = file_path_prefix or ["chat_title"]
        self.file_name_prefix = file_name_prefix or ["file_name"]
        self.file_name_split = file_name_split
        self.date_format = date_format

    def generate_path(
        self,
        chat_title: str = "Unknown",
        media_type: str = "document",
        media_date: Optional[datetime] = None
    ) -> Path:
        """
        生成文件保存路径

        Args:
            chat_title: 频道/群组标题
            media_type: 媒体类型
            media_date: 媒体日期

        Returns:
            完整路径
        """
        if media_date is None:
            media_date = datetime.now()

        # 构建路径组件
        components = []
        for prefix in self.file_path_prefix:
            if prefix == "chat_title":
                components.append(self._sanitize(chat_title))
            elif prefix == "media_datetime":
                components.append(media_date.strftime(self.date_format))
            elif prefix == "media_type":
                components.append(media_type)

        # 组合路径
        path = self.base_path
        for component in components:
            path = path / component

        return path

    def generate_filename(
        self,
        message_id: int,
        original_filename: str = "",
        caption: str = "",
        extension: str = ""
    ) -> str:
        """
        生成文件名

        Args:
            message_id: 消息 ID
            original_filename: 原始文件名
            caption: 消息标题
            extension: 文件扩展名

        Returns:
            生成的文件名
        """
        # 构建文件名组件
        components = []
        for prefix in self.file_name_prefix:
            if prefix == "message_id":
                components.append(str(message_id))
            elif prefix == "file_name" and original_filename:
                # 移除扩展名
                name = Path(original_filename).stem
                components.append(self._sanitize(name))
            elif prefix == "caption" and caption:
                # 清理 caption
                clean_caption = self._clean_caption(caption)
                if clean_caption:
                    components.append(clean_caption)

        # 如果没有有效组件，使用消息 ID
        if not components:
            components = [str(message_id)]

        # 组合文件名
        filename = self.file_name_split.join(components)

        # 添加扩展名
        if extension and not extension.startswith('.'):
            extension = f".{extension}"
        if not filename.endswith(extension):
            filename += extension

        return filename

    def _sanitize(self, name: str, max_length: int = 50) -> str:
        """
        清理文件名/路径名

        Args:
            name: 原始名称
            max_length: 最大长度

        Returns:
            清理后的名称
        """
        # 移除非法字符
        name = re.sub(r'[<>:"/\\|?*]', '_', name)
        # 移除前后空格
        name = name.strip()
        # 限制长度
        if len(name) > max_length:
            name = name[:max_length]
        # 如果为空，使用默认
        if not name:
            name = "Untitled"
        return name

    def _clean_caption(self, caption: str, max_length: int = 50) -> str:
        """
        清理 caption 作为文件名

        Args:
            caption: 原始 caption
            max_length: 最大长度

        Returns:
            清理后的 caption
        """
        # 移除 @ 提及
        caption = re.sub(r'@\w+', '', caption)
        # 移除 URL
        caption = re.sub(r'https?://\S+', '', caption)
        # 移除多余空格
        caption = re.sub(r'\s+', ' ', caption)
        # 移除换行
        caption = caption.replace('\n', ' ')
        # 清理并限制长度
        return self._sanitize(caption, max_length)


if __name__ == "__main__":
    # 测试
    generator = PathGenerator(
        base_path="./downloads",
        file_path_prefix=["chat_title", "media_datetime"],
        file_name_prefix=["message_id", "file_name"],
        date_format="%Y_%m"
    )

    # 测试路径生成
    path = generator.generate_path(
        chat_title="Test Channel",
        media_type="video",
        media_date=datetime(2024, 6, 16)
    )
    print(f"Path: {path}")

    # 测试文件名生成
    filename = generator.generate_filename(
        message_id=12345,
        original_filename="test_video.mp4",
        caption="这是一个测试视频 @someone https://example.com"
    )
    print(f"Filename: {filename}")
