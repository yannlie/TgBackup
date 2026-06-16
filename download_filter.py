"""下载过滤器 - 支持按日期、ID、大小过滤消息"""
# ponytail: stdlib operator + regex does it

import re
import operator
from datetime import datetime
from typing import Optional, Tuple


def should_download(
    filter_expr: str = "",
    message_date: Optional[datetime] = None,
    message_id: Optional[int] = None,
    file_size: Optional[int] = None
) -> Tuple[bool, Optional[str]]:
    """
    判断是否应该下载

    Args:
        filter_expr: 过滤表达式
            - message_date >= 2024-01-01
            - message_id > 1000
            - file_size < 104857600
        message_date: 消息日期
        message_id: 消息 ID
        file_size: 文件大小（字节）

    Returns:
        (是否下载, 拒绝原因)
    """
    if not filter_expr:
        return True, None

    ops = {
        '>=': operator.ge,
        '<=': operator.le,
        '>': operator.gt,
        '<': operator.lt,
        '==': operator.eq
    }

    # Date filter
    for op_str, val in re.findall(r'message_date\s*(>=|<=|>|<|==)\s*(\d{4}-\d{2}-\d{2})', filter_expr):
        if message_date:
            try:
                filter_date = datetime.strptime(val, '%Y-%m-%d')
                if not ops[op_str](message_date, filter_date):
                    return False, f"日期不符合: {op_str} {val}"
            except ValueError:
                pass

    # ID filter
    for op_str, val in re.findall(r'message_id\s*(>=|<=|>|<|==)\s*(\d+)', filter_expr):
        if message_id and not ops[op_str](message_id, int(val)):
            return False, f"消息ID不符合: {op_str} {val}"

    # Size filter
    for op_str, val in re.findall(r'file_size\s*(>=|<=|>|<|==)\s*(\d+)', filter_expr):
        if file_size and not ops[op_str](file_size, int(val)):
            return False, f"文件大小不符合: {op_str} {val} 字节"

    return True, None


# Backward compatibility
class DownloadFilter:
    """Compatibility wrapper"""
    def __init__(self, filter_expression: str = ""):
        self.expression = filter_expression

    def should_download(self, message_date=None, message_id=None, file_size=None):
        return should_download(self.expression, message_date, message_id, file_size)


if __name__ == "__main__":
    # Test
    result, reason = should_download(
        "message_date >= 2024-01-01",
        message_date=datetime(2024, 6, 16)
    )
    print(f"Test 1: {result}, {reason}")  # True, None

    result, reason = should_download(
        "message_id > 1000",
        message_id=500
    )
    print(f"Test 2: {result}, {reason}")  # False, "消息ID不符合: > 1000"
