"""下载过滤器 - 支持按日期、类型等过滤消息"""
import re
from datetime import datetime
from typing import Optional


class DownloadFilter:
    """下载过滤器"""

    def __init__(self, filter_expression: str = ""):
        """
        Args:
            filter_expression: 过滤表达式
                支持的条件:
                - message_date >= 2024-01-01
                - message_date <= 2024-12-31
                - message_date >= 2024-01-01 00:00:00
                - message_id > 1000
                - message_id < 5000
                - file_size > 1048576  (字节)
                - file_size < 104857600
        """
        self.expression = filter_expression.strip()
        self.conditions = []

        if self.expression:
            self._parse_expression()

    def _parse_expression(self):
        """解析过滤表达式"""
        # 支持的条件类型
        patterns = {
            'date': r'message_date\s*(>=|<=|>|<|==)\s*(\d{4}-\d{2}-\d{2}(?:\s+\d{2}:\d{2}:\d{2})?)',
            'id': r'message_id\s*(>=|<=|>|<|==)\s*(\d+)',
            'size': r'file_size\s*(>=|<=|>|<|==)\s*(\d+)',
        }

        for cond_type, pattern in patterns.items():
            matches = re.findall(pattern, self.expression)
            for operator, value in matches:
                self.conditions.append({
                    'type': cond_type,
                    'operator': operator,
                    'value': value
                })

    def should_download(
        self,
        message_date: Optional[datetime] = None,
        message_id: Optional[int] = None,
        file_size: Optional[int] = None
    ) -> tuple[bool, Optional[str]]:
        """
        判断是否应该下载

        Args:
            message_date: 消息日期
            message_id: 消息 ID
            file_size: 文件大小（字节）

        Returns:
            (是否下载, 原因)
        """
        if not self.conditions:
            return True, None

        for condition in self.conditions:
            cond_type = condition['type']
            operator = condition['operator']
            value = condition['value']

            # 日期过滤
            if cond_type == 'date' and message_date is not None:
                try:
                    # 解析日期
                    if len(value) == 10:  # YYYY-MM-DD
                        filter_date = datetime.strptime(value, '%Y-%m-%d')
                    else:  # YYYY-MM-DD HH:MM:SS
                        filter_date = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')

                    if not self._compare(message_date, operator, filter_date):
                        return False, f"日期不符合: {operator} {value}"
                except ValueError:
                    pass

            # ID 过滤
            elif cond_type == 'id' and message_id is not None:
                filter_id = int(value)
                if not self._compare(message_id, operator, filter_id):
                    return False, f"消息ID不符合: {operator} {value}"

            # 文件大小过滤
            elif cond_type == 'size' and file_size is not None:
                filter_size = int(value)
                if not self._compare(file_size, operator, filter_size):
                    return False, f"文件大小不符合: {operator} {value} 字节"

        return True, None

    def _compare(self, left, operator: str, right) -> bool:
        """执行比较操作"""
        if operator == '>=':
            return left >= right
        elif operator == '<=':
            return left <= right
        elif operator == '>':
            return left > right
        elif operator == '<':
            return left < right
        elif operator == '==':
            return left == right
        return False


if __name__ == "__main__":
    # 测试
    filter1 = DownloadFilter("message_date >= 2024-01-01 and message_date <= 2024-12-31")

    # 测试日期过滤
    result1, reason1 = filter1.should_download(
        message_date=datetime(2024, 6, 16)
    )
    print(f"Test 1: {result1}, {reason1}")

    result2, reason2 = filter1.should_download(
        message_date=datetime(2023, 6, 16)
    )
    print(f"Test 2: {result2}, {reason2}")

    # 测试 ID 过滤
    filter2 = DownloadFilter("message_id > 1000")
    result3, reason3 = filter2.should_download(message_id=1500)
    print(f"Test 3: {result3}, {reason3}")

    result4, reason4 = filter2.should_download(message_id=500)
    print(f"Test 4: {result4}, {reason4}")
