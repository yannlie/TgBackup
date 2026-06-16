"""文件路径和文件名生成器"""
# ponytail: stdlib Path.joinpath + regex does it

import re
from datetime import datetime
from pathlib import Path
from typing import Optional


def make_path(
    base_path: str,
    chat_title: str = "Unknown",
    media_type: str = "document",
    media_date: Optional[datetime] = None,
    date_format: str = "%Y_%m",
    path_parts: list = None
) -> Path:
    """
    生成文件保存路径

    Args:
        base_path: 基础路径
        chat_title: 频道标题
        media_type: 媒体类型
        media_date: 媒体日期
        date_format: 日期格式
        path_parts: 路径组件 ['chat_title', 'media_datetime', 'media_type']

    Returns:
        完整路径
    """
    if media_date is None:
        media_date = datetime.now()

    path_parts = path_parts or ["chat_title"]

    # ponytail: regex for sanitize, no class needed
    def clean(s):
        s = re.sub(r'[<>:"/\\|?*]', '_', s or 'Unknown')[:50].strip()
        return s or 'Unknown'

    parts = []
    for part in path_parts:
        if part == "chat_title":
            parts.append(clean(chat_title))
        elif part == "media_datetime":
            parts.append(media_date.strftime(date_format))
        elif part == "media_type":
            parts.append(media_type)

    return Path(base_path).joinpath(*parts)


def make_filename(
    message_id: int,
    original_filename: str = "",
    caption: str = "",
    extension: str = "",
    separator: str = " - ",
    filename_parts: list = None
) -> str:
    """
    生成文件名

    Args:
        message_id: 消息 ID
        original_filename: 原始文件名
        caption: 消息标题
        extension: 文件扩展名
        separator: 分隔符
        filename_parts: 文件名组件 ['message_id', 'file_name', 'caption']

    Returns:
        生成的文件名
    """
    filename_parts = filename_parts or ["message_id", "file_name"]

    # ponytail: inline sanitize
    def clean(s, max_len=50):
        s = re.sub(r'[<>:"/\\|?*@]', '_', s)
        s = re.sub(r'https?://\S+', '', s)
        s = re.sub(r'\s+', ' ', s).strip()
        return s[:max_len] if s else ''

    parts = []
    for part in filename_parts:
        if part == "message_id":
            parts.append(str(message_id))
        elif part == "file_name" and original_filename:
            name = Path(original_filename).stem
            if cleaned := clean(name):
                parts.append(cleaned)
        elif part == "caption" and caption:
            if cleaned := clean(caption):
                parts.append(cleaned)

    if not parts:
        parts = [str(message_id)]

    filename = separator.join(parts)

    if extension and not extension.startswith('.'):
        extension = f'.{extension}'
    if extension and not filename.endswith(extension):
        filename += extension

    return filename


# Backward compatibility
class PathGenerator:
    """Compatibility wrapper"""
    def __init__(self, base_path, file_path_prefix=None, file_name_prefix=None,
                 file_name_split=" - ", date_format="%Y_%m"):
        self.base_path = base_path
        self.file_path_prefix = file_path_prefix or ["chat_title"]
        self.file_name_prefix = file_name_prefix or ["file_name"]
        self.file_name_split = file_name_split
        self.date_format = date_format

    def generate_path(self, chat_title="Unknown", media_type="document", media_date=None):
        return make_path(self.base_path, chat_title, media_type, media_date,
                        self.date_format, self.file_path_prefix)

    def generate_filename(self, message_id, original_filename="", caption="", extension=""):
        return make_filename(message_id, original_filename, caption, extension,
                           self.file_name_split, self.file_name_prefix)


if __name__ == "__main__":
    # Test
    path = make_path(
        "./downloads",
        "Test Channel",
        "video",
        datetime(2024, 6, 16),
        "%Y_%m",
        ["chat_title", "media_datetime"]
    )
    print(f"Path: {path}")

    filename = make_filename(
        12345,
        "test_video.mp4",
        "这是测试 @user https://example.com",
        ".mp4",
        " - ",
        ["message_id", "file_name"]
    )
    print(f"Filename: {filename}")
