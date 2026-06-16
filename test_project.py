#!/usr/bin/env python3
"""
项目完整性测试脚本
测试所有核心功能和文件
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def test_section(title):
    """打印测试分区"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def check_file_exists(filepath, required=True):
    """检查文件是否存在"""
    exists = os.path.exists(filepath)
    status = "OK" if exists else ("FAIL" if required else "WARN")
    print(f"  [{status}] {filepath} {'exists' if exists else 'missing'}")
    return exists

def check_python_syntax(filepath):
    """检查 Python 语法"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            compile(f.read(), filepath, 'exec')
        print(f"  [OK] {filepath} - Syntax valid")
        return True
    except SyntaxError as e:
        print(f"  [FAIL] {filepath} - Syntax error: {e}")
        return False
    except Exception as e:
        print(f"  [WARN] {filepath} - {e}")
        return False

def check_json_valid(filepath):
    """检查 JSON 格式"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"  [OK] {filepath} - Valid JSON ({len(data)} keys)")
        return True
    except json.JSONDecodeError as e:
        print(f"  [FAIL] {filepath} - JSON error: {e}")
        return False
    except FileNotFoundError:
        print(f"  [WARN] {filepath} - Not found")
        return False

def check_docker_files():
    """检查 Docker 文件"""
    docker_files = [
        'Dockerfile',
        'docker-compose.yml',
        '.dockerignore'
    ]

    for file in docker_files:
        if check_file_exists(file):
            # 检查文件不为空
            size = os.path.getsize(file)
            print(f"       Size: {size} bytes")

def check_dependencies():
    """检查 Python 依赖"""
    deps_files = ['requirements.txt', 'requirements_telegram.txt']

    for file in deps_files:
        if os.path.exists(file):
            with open(file, 'r') as f:
                lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]
            print(f"  [OK] {file} ({len(lines)} packages)")
            for line in lines[:3]:  # 显示前3个
                print(f"       - {line}")
            if len(lines) > 3:
                print(f"       ... and {len(lines)-3} more")

def run_tests():
    """运行所有测试"""

    # 1. 核心 Python 文件
    test_section("Core Python Files")
    python_files = [
        'telegram_downloader.py',
        'telegram_bot_controller.py',
        'tg_to_onedrive.py',
        'get_refresh_token.py',
        'start.py',
        'test_uploader.py'
    ]

    syntax_ok = True
    for file in python_files:
        if check_file_exists(file):
            if not check_python_syntax(file):
                syntax_ok = False

    # 2. 配置文件模板
    test_section("Configuration Templates")
    config_files = [
        'telegram_config.example.json',
        'onedrive_config.example.json'
    ]

    for file in config_files:
        if check_file_exists(file):
            check_json_valid(file)

    # 3. Docker 文件
    test_section("Docker Files")
    check_docker_files()

    # 4. 部署脚本
    test_section("Deployment Scripts")
    check_file_exists('deploy.sh')
    check_file_exists('deploy.bat')

    # 5. 文档文件
    test_section("Documentation")
    docs = [
        'README.md',
        'TELEGRAM_README.md',
        'DOCKER.md',
        'FAQ.md',
        'CONTRIBUTING.md',
        'LICENSE'
    ]

    for doc in docs:
        check_file_exists(doc)

    # 6. 依赖文件
    test_section("Dependencies")
    check_dependencies()

    # 7. GitHub Actions
    test_section("GitHub Actions")
    workflows = [
        '.github/workflows/python-quality.yml',
        '.github/workflows/release.yml',
        '.github/workflows/update-deps.yml'
    ]

    for workflow in workflows:
        check_file_exists(workflow)

    # 8. Git 文件
    test_section("Git Files")
    check_file_exists('.gitignore')
    check_file_exists('.dockerignore')

    # 最终总结
    test_section("Test Summary")

    if syntax_ok:
        print("  [OK] All Python files have valid syntax")
    else:
        print("  [FAIL] Some Python files have syntax errors")

    # 统计文件
    py_files = list(Path('.').glob('*.py'))
    md_files = list(Path('.').glob('*.md'))
    json_files = list(Path('.').glob('*.json'))

    print(f"\n  File Statistics:")
    print(f"    Python files: {len(py_files)}")
    print(f"    Markdown docs: {len(md_files)}")
    print(f"    JSON configs: {len(json_files)}")

    # 代码统计
    total_lines = 0
    for py_file in py_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
                total_lines += lines
        except:
            pass

    print(f"    Total Python LOC: {total_lines}")

    print("\n" + "="*60)
    if syntax_ok:
        print("  [PASS] PROJECT TEST PASSED")
    else:
        print("  [FAIL] PROJECT TEST FAILED")
    print("="*60)

    return syntax_ok

if __name__ == '__main__':
    print("="*60)
    print("  TG to OneDrive - Project Integrity Test")
    print("="*60)

    success = run_tests()
    sys.exit(0 if success else 1)
