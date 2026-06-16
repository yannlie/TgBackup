"""通用工具函数"""
# ponytail: one place for common utils


import re


def format_size(bytes_size: int) -> str:
    """
    格式化文件大小为人类可读格式

    Args:
        bytes_size: 字节数

    Returns:
        格式化的大小（如 "10.5 MB"）
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f} TB"


def sanitize_filename(name: str, max_length: int = 100) -> str:
    """
    清理文件名（移除非法字符）

    Args:
        name: 原始文件名
        max_length: 最大长度

    Returns:
        清理后的文件名
    """
    # ponytail: regex does it
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', name)[:max_length].strip()
    return cleaned or 'untitled'


if __name__ == "__main__":
    # Test
    print(format_size(1024))  # 1.00 KB
    print(format_size(1048576))  # 1.00 MB
    print(format_size(1158951948))  # 1105.26 MB

    print(sanitize_filename('test:file<name>.txt'))  # test_file_name_.txt
    print(sanitize_filename('a' * 200, 50))  # aaaa... (50 chars)
