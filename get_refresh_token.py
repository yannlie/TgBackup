#!/usr/bin/env python3
"""
获取 OneDrive Refresh Token 工具
用于首次配置 OneDrive API 认证
"""

import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests
import json

# 填写你的应用信息
CLIENT_ID = 'YOUR_CLIENT_ID'
CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
REDIRECT_URI = 'http://localhost:8080'

# 授权 URL
AUTH_URL = (
    f'https://login.microsoftonline.com/common/oauth2/v2.0/authorize'
    f'?client_id={CLIENT_ID}'
    f'&response_type=code'
    f'&redirect_uri={REDIRECT_URI}'
    f'&response_mode=query'
    f'&scope=https://graph.microsoft.com/Files.ReadWrite.All offline_access'
)

authorization_code = None


class CallbackHandler(BaseHTTPRequestHandler):
    """处理 OAuth 回调"""

    def do_GET(self):
        global authorization_code

        # 解析回调 URL
        query = urlparse(self.path).query
        params = parse_qs(query)

        if 'code' in params:
            authorization_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'''
                <html>
                <body>
                    <h2>授权成功！</h2>
                    <p>可以关闭此页面，返回终端查看 refresh_token</p>
                </body>
                </html>
            ''')
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Authorization failed')

    def log_message(self, format, *args):
        """禁用日志输出"""
        pass


def get_refresh_token():
    """获取 Refresh Token"""
    print("=== OneDrive Refresh Token 获取工具 ===\n")

    if CLIENT_ID == 'YOUR_CLIENT_ID' or CLIENT_SECRET == 'YOUR_CLIENT_SECRET':
        print("错误：请先在脚本中填写 CLIENT_ID 和 CLIENT_SECRET！")
        print("\n配置步骤：")
        print("1. 访问 https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade")
        print("2. 新建应用注册")
        print("3. 在'证书和密码'中创建客户端密码")
        print("4. 在'API 权限'中添加 Microsoft Graph 的 Files.ReadWrite.All (委托权限)")
        print("5. 将 CLIENT_ID 和 CLIENT_SECRET 填入此脚本")
        return

    print("步骤 1: 打开浏览器进行授权...")
    print(f"授权 URL: {AUTH_URL}\n")
    webbrowser.open(AUTH_URL)

    print("步骤 2: 启动本地服务器接收回调...")
    server = HTTPServer(('localhost', 8080), CallbackHandler)

    # 等待回调
    while authorization_code is None:
        server.handle_request()

    print("步骤 3: 使用授权码获取 Token...\n")

    # 交换 token
    token_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': authorization_code,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }

    try:
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        token_data = response.json()

        print("=" * 60)
        print("获取成功！请将以下信息复制到 onedrive_config.json：")
        print("=" * 60)
        print(f"\nclient_id: {CLIENT_ID}")
        print(f"client_secret: {CLIENT_SECRET}")
        print(f"refresh_token: {token_data['refresh_token']}")
        print("\n" + "=" * 60)

        # 自动保存到配置文件
        config = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'refresh_token': token_data['refresh_token'],
            'base_path': '/TG_Media'
        }

        with open('onedrive_config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print("\n✓ 已自动保存到 onedrive_config.json")

    except Exception as e:
        print(f"错误：获取 Token 失败 - {e}")


if __name__ == '__main__':
    get_refresh_token()
