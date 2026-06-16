#!/bin/bash
# Docker 镜像构建和推送脚本

set -e

# 配置
IMAGE_NAME="tgbackup"
DOCKER_USERNAME="${DOCKER_USERNAME:-yannlie}"  # 替换为你的 Docker Hub 用户名
VERSION=$(grep -oP '__version__ = "\K[^"]+' telegram_downloader.py | head -1)

echo "=================================="
echo "Docker 镜像构建和推送"
echo "=================================="
echo ""
echo "镜像名称: ${DOCKER_USERNAME}/${IMAGE_NAME}"
echo "版本: ${VERSION}"
echo ""

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: 未安装 Docker"
    exit 1
fi

echo "✓ Docker 已安装"
echo ""

# 构建镜像
echo "=================================="
echo "1. 构建 Docker 镜像"
echo "=================================="
echo ""

docker build \
    --platform linux/amd64,linux/arm64 \
    -t ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION} \
    -t ${DOCKER_USERNAME}/${IMAGE_NAME}:latest \
    .

if [ $? -eq 0 ]; then
    echo "✓ 镜像构建成功"
else
    echo "❌ 镜像构建失败"
    exit 1
fi

echo ""

# 测试镜像
echo "=================================="
echo "2. 测试镜像"
echo "=================================="
echo ""

docker run --rm ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION} python --version
docker run --rm ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION} python -c "import telethon; print('Telethon OK')"

echo "✓ 镜像测试通过"
echo ""

# 推送镜像
echo "=================================="
echo "3. 推送镜像到 Docker Hub"
echo "=================================="
echo ""

read -p "是否推送镜像到 Docker Hub? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "登录 Docker Hub..."
    docker login

    echo "推送镜像..."
    docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}
    docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:latest

    echo "✓ 镜像推送成功"
    echo ""
    echo "镜像地址:"
    echo "  docker pull ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}"
    echo "  docker pull ${DOCKER_USERNAME}/${IMAGE_NAME}:latest"
else
    echo "跳过推送"
fi

echo ""
echo "=================================="
echo "完成！"
echo "=================================="
echo ""
echo "使用方法:"
echo "  docker run -d --name tg-downloader \\"
echo "    -v \$(pwd)/config:/app/config \\"
echo "    -v \$(pwd)/downloads:/app/downloads \\"
echo "    ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}"
echo ""
