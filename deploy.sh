#!/bin/bash
# 快速部署脚本 - Linux/macOS

set -e

echo "=================================="
echo "TG Downloader Docker 快速部署"
echo "=================================="
echo

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: 未安装 Docker"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误: 未安装 docker-compose"
    echo "请先安装 docker-compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✓ Docker 已安装"
echo

# 创建必要的目录
echo "创建目录..."
mkdir -p downloads logs sessions config
echo "✓ 目录已创建"
echo

# 检查配置文件
if [ ! -f "telegram_config.json" ]; then
    echo "⚠ telegram_config.json 不存在"
    if [ -f "telegram_config.example.json" ]; then
        echo "正在创建配置文件..."
        cp telegram_config.example.json telegram_config.json
        echo "✓ 已创建 telegram_config.json"
        echo "❗ 请编辑 telegram_config.json 填入你的配置"
        echo
        read -p "是否现在编辑配置? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ${EDITOR:-nano} telegram_config.json
        else
            echo "请稍后手动编辑 telegram_config.json"
            exit 0
        fi
    else
        echo "❌ 错误: 找不到配置文件模板"
        exit 1
    fi
fi

if [ ! -f "onedrive_config.json" ]; then
    echo "⚠ onedrive_config.json 不存在"
    if [ -f "onedrive_config.example.json" ]; then
        echo "正在创建配置文件..."
        cp onedrive_config.example.json onedrive_config.json
        echo "✓ 已创建 onedrive_config.json"
        echo "提示: 如不需要 OneDrive 上传，可跳过此配置"
    fi
fi

echo "✓ 配置文件检查完成"
echo

# 构建镜像
echo "构建 Docker 镜像..."
docker-compose build
echo "✓ 镜像构建完成"
echo

# 首次登录
echo "=================================="
echo "首次登录 Telegram"
echo "=================================="
echo
echo "需要进行首次登录以获取 session"
read -p "是否现在登录? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose run --rm telegram-downloader python telegram_downloader.py
fi

echo
echo "=================================="
echo "部署选项"
echo "=================================="
echo
echo "1. 启动下载器 (带 Bot 控制)"
echo "2. 启动下载器 (无 Bot 控制)"
echo "3. 启动下载器 + 独立上传器"
echo "4. 退出"
echo

read -p "请选择 (1-4): " choice

case $choice in
    1)
        echo "启动下载器 (带 Bot 控制)..."
        docker-compose up -d telegram-downloader
        ;;
    2)
        echo "启动下载器 (无 Bot 控制)..."
        # 修改 command
        docker-compose run -d --name tg-downloader telegram-downloader python telegram_downloader.py
        ;;
    3)
        echo "启动下载器 + 独立上传器..."
        docker-compose --profile standalone up -d
        ;;
    4)
        echo "退出"
        exit 0
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac

echo
echo "=================================="
echo "✓ 部署完成！"
echo "=================================="
echo
echo "查看状态: docker-compose ps"
echo "查看日志: docker-compose logs -f"
echo "停止服务: docker-compose down"
echo
echo "如果启用了 Bot 控制，请在 Telegram 与你的 Bot 对话"
echo "发送 /start 查看可用命令"
echo
