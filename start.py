#!/usr/bin/env python3
"""
一键启动脚本 - Telegram 下载 + OneDrive 上传
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    print("检查依赖...")

    required = {
        'telethon': 'requirements_telegram.txt',
        'watchdog': 'requirements.txt',
        'requests': 'requirements.txt'
    }

    missing = []
    for module, req_file in required.items():
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError:
            print(f"  ✗ {module} (缺失)")
            missing.append(req_file)

    if missing:
        print("\n安装缺失的依赖...")
        for req_file in set(missing):
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', req_file])
        print("✓ 依赖安装完成\n")

def check_config():
    """检查配置文件"""
    print("检查配置文件...")

    configs = {
        'telegram_config.json': 'telegram_config.example.json',
        'onedrive_config.json': 'onedrive_config.example.json'
    }

    all_exist = True

    for config, example in configs.items():
        if not os.path.exists(config):
            print(f"  ✗ {config} 不存在")
            if os.path.exists(example):
                print(f"    提示: 复制 {example} 并修改")
            all_exist = False
        else:
            # 检查是否是模板
            with open(config, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if config == 'telegram_config.json':
                if data.get('api_id') == 'YOUR_API_ID':
                    print(f"  ✗ {config} 需要配置 (api_id 未填写)")
                    all_exist = False
                else:
                    print(f"  ✓ {config}")

            elif config == 'onedrive_config.json':
                if data.get('client_id') == 'YOUR_CLIENT_ID':
                    print(f"  ⚠ {config} 未配置 (将只下载不上传)")
                else:
                    print(f"  ✓ {config}")

    return all_exist

def show_menu():
    """显示菜单"""
    print("\n" + "=" * 60)
    print("Telegram Media Downloader + OneDrive Uploader")
    print("=" * 60)
    print("\n请选择运行模式：")
    print()
    print("1. 启动 Telegram 下载器 (自动监听新消息)")
    print("2. 启动 OneDrive 上传器 (监听本地目录)")
    print("3. 配置向导")
    print("4. 测试配置")
    print("5. 退出")
    print()

    choice = input("请选择 (1-5): ").strip()
    return choice

def run_telegram_downloader():
    """运行 Telegram 下载器"""
    print("\n启动 Telegram 下载器...")
    print("提示: 按 Ctrl+C 停止\n")
    subprocess.run([sys.executable, 'telegram_downloader.py'])

def run_onedrive_uploader():
    """运行 OneDrive 上传器"""
    print("\n启动 OneDrive 上传器...")
    print("提示: 按 Ctrl+C 停止\n")

    # 询问监听目录
    default_path = './downloads'
    path = input(f"监听目录 (默认: {default_path}): ").strip() or default_path

    subprocess.run([sys.executable, 'tg_to_onedrive.py', '--watch-path', path])

def config_wizard():
    """配置向导"""
    print("\n" + "=" * 60)
    print("配置向导")
    print("=" * 60)

    # Telegram 配置
    print("\n1. Telegram 配置")
    print("-" * 40)

    if not os.path.exists('telegram_config.json'):
        print("telegram_config.json 不存在，正在创建...")

        api_id = input("请输入 api_id (从 https://my.telegram.org/apps 获取): ").strip()
        api_hash = input("请输入 api_hash: ").strip()
        phone = input("请输入手机号 (格式: +8613800138000): ").strip()

        config = {
            "api_id": api_id,
            "api_hash": api_hash,
            "phone": phone,
            "channels": [],
            "download_path": "./downloads",
            "media_types": ["photo", "video", "document", "audio"],
            "file_size_limit": 2147483648,
            "extensions_whitelist": [],
            "extensions_blacklist": [".exe", ".bat", ".cmd"],
            "auto_upload": True,
            "delete_after_upload": False
        }

        with open('telegram_config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print("✓ telegram_config.json 已创建")
    else:
        print("✓ telegram_config.json 已存在")

    # OneDrive 配置
    print("\n2. OneDrive 配置")
    print("-" * 40)

    if not os.path.exists('onedrive_config.json'):
        choice = input("是否配置 OneDrive 自动上传? (y/n): ").strip().lower()
        if choice == 'y':
            print("\n请运行: python get_refresh_token.py")
            print("按照提示完成 OneDrive 授权")
        else:
            print("跳过 OneDrive 配置 (仅下载)")
    else:
        print("✓ onedrive_config.json 已存在")

    print("\n配置完成！")

def test_config():
    """测试配置"""
    print("\n测试配置...")
    print("-" * 60)

    # 测试 Telegram 配置
    print("\n1. Telegram 配置")
    try:
        with open('telegram_config.json', 'r', encoding='utf-8') as f:
            tg_config = json.load(f)

        print(f"  api_id: {tg_config.get('api_id')}")
        print(f"  phone: {tg_config.get('phone')}")
        print(f"  channels: {len(tg_config.get('channels', []))} 个")
        print(f"  download_path: {tg_config.get('download_path')}")

        if tg_config.get('api_id') == 'YOUR_API_ID':
            print("  ✗ 需要配置")
        else:
            print("  ✓ 配置正常")

    except FileNotFoundError:
        print("  ✗ 配置文件不存在")
    except Exception as e:
        print(f"  ✗ 错误: {e}")

    # 测试 OneDrive 配置
    print("\n2. OneDrive 配置")
    try:
        with open('onedrive_config.json', 'r', encoding='utf-8') as f:
            od_config = json.load(f)

        print(f"  client_id: {od_config.get('client_id')[:20]}...")
        print(f"  base_path: {od_config.get('base_path')}")

        if od_config.get('client_id') == 'YOUR_CLIENT_ID':
            print("  ⚠ 未配置 (将只下载不上传)")
        else:
            print("  ✓ 配置正常")

    except FileNotFoundError:
        print("  ⚠ 配置文件不存在 (将只下载不上传)")
    except Exception as e:
        print(f"  ✗ 错误: {e}")

    print("\n" + "-" * 60)

def main():
    """主函数"""
    # 检查依赖
    check_dependencies()

    # 检查配置
    config_ok = check_config()

    if not config_ok:
        print("\n⚠ 配置文件有问题，请先运行配置向导")
        print()

    # 显示菜单
    while True:
        choice = show_menu()

        if choice == '1':
            run_telegram_downloader()

        elif choice == '2':
            run_onedrive_uploader()

        elif choice == '3':
            config_wizard()

        elif choice == '4':
            test_config()

        elif choice == '5':
            print("\n再见！")
            break

        else:
            print("\n无效的选择，请重试")

        input("\n按 Enter 继续...")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已停止")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
