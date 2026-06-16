"""简单的 Web 监控界面"""
import os
import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS


class WebMonitor:
    """Web 监控服务"""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 5000,
        login_secret: str = ""
    ):
        """
        Args:
            host: 监听地址
            port: 监听端口
            login_secret: 登录密码（为空则不需要登录）
        """
        self.host = host
        self.port = port
        self.login_secret = login_secret

        self.app = Flask(__name__)
        CORS(self.app)

        self.stats = {
            "downloaded": 0,
            "uploaded": 0,
            "failed": 0,
            "skipped": 0,
            "running": False,
            "start_time": None,
            "recent_files": []
        }

        self._setup_routes()
        self.thread = None

    def _setup_routes(self):
        """设置路由"""

        @self.app.route('/')
        def index():
            """首页"""
            return render_template('index.html')

        @self.app.route('/api/stats')
        def get_stats():
            """获取统计信息"""
            return jsonify({
                "success": True,
                "data": {
                    **self.stats,
                    "uptime": self._get_uptime()
                }
            })

        @self.app.route('/api/recent')
        def get_recent():
            """获取最近下载"""
            return jsonify({
                "success": True,
                "data": self.stats.get("recent_files", [])[-20:]
            })

        @self.app.route('/api/config')
        def get_config():
            """获取配置信息"""
            # TODO: 读取配置文件
            return jsonify({
                "success": True,
                "data": {
                    "download_path": "./downloads",
                    "channels": []
                }
            })

    def _get_uptime(self) -> str:
        """获取运行时间"""
        if not self.stats.get("start_time"):
            return "未运行"

        start = datetime.fromisoformat(self.stats["start_time"])
        delta = datetime.now() - start

        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60

        return f"{delta.days}天 {hours}小时 {minutes}分钟"

    def update_stats(self, key: str, value: Any):
        """更新统计信息"""
        self.stats[key] = value

    def add_recent_file(self, file_info: Dict[str, Any]):
        """添加最近下载的文件"""
        if "recent_files" not in self.stats:
            self.stats["recent_files"] = []

        self.stats["recent_files"].append({
            **file_info,
            "time": datetime.now().isoformat()
        })

        # 只保留最近 100 个
        if len(self.stats["recent_files"]) > 100:
            self.stats["recent_files"] = self.stats["recent_files"][-100:]

    def start(self):
        """启动 Web 服务"""
        self.stats["running"] = True
        self.stats["start_time"] = datetime.now().isoformat()

        def run():
            self.app.run(
                host=self.host,
                port=self.port,
                debug=False,
                use_reloader=False
            )

        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()

        print(f"✓ Web 界面已启动: http://{self.host}:{self.port}")

    def stop(self):
        """停止 Web 服务"""
        self.stats["running"] = False


# 全局实例
_monitor_instance = None


def get_monitor() -> WebMonitor:
    """获取 Web 监控实例"""
    global _monitor_instance
    return _monitor_instance


def init_monitor(host: str = "127.0.0.1", port: int = 5000, login_secret: str = ""):
    """初始化 Web 监控"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = WebMonitor(host, port, login_secret)
        _monitor_instance.start()
    return _monitor_instance


if __name__ == "__main__":
    # 测试
    monitor = WebMonitor(host="127.0.0.1", port=5000)
    monitor.start()

    # 模拟更新
    import time
    monitor.update_stats("downloaded", 10)
    monitor.add_recent_file({
        "name": "test.mp4",
        "size": 1024000,
        "channel": "Test Channel"
    })

    print("Web 服务运行中，按 Ctrl+C 停止...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n停止中...")
