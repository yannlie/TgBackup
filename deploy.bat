@echo off
chcp 65001 >nul
REM 快速部署脚本 - Windows

echo ==================================
echo TG Downloader Docker 快速部署
echo ==================================
echo.

REM 检查 Docker
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 错误: 未安装 Docker
    echo 请先安装 Docker Desktop: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

where docker-compose >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 错误: 未安装 docker-compose
    echo Docker Desktop 应该已包含 docker-compose
    pause
    exit /b 1
)

echo ✓ Docker 已安装
echo.

REM 创建必要的目录
echo 创建目录...
if not exist "downloads" mkdir downloads
if not exist "logs" mkdir logs
if not exist "sessions" mkdir sessions
if not exist "config" mkdir config
echo ✓ 目录已创建
echo.

REM 检查配置文件
if not exist "telegram_config.json" (
    echo ⚠ telegram_config.json 不存在
    if exist "telegram_config.example.json" (
        echo 正在创建配置文件...
        copy telegram_config.example.json telegram_config.json
        echo ✓ 已创建 telegram_config.json
        echo ❗ 请编辑 telegram_config.json 填入你的配置
        echo.
        set /p edit="是否现在编辑配置? (y/n) "
        if /i "%edit%"=="y" (
            notepad telegram_config.json
        ) else (
            echo 请稍后手动编辑 telegram_config.json
            pause
            exit /b 0
        )
    ) else (
        echo ❌ 错误: 找不到配置文件模板
        pause
        exit /b 1
    )
)

if not exist "onedrive_config.json" (
    echo ⚠ onedrive_config.json 不存在
    if exist "onedrive_config.example.json" (
        echo 正在创建配置文件...
        copy onedrive_config.example.json onedrive_config.json
        echo ✓ 已创建 onedrive_config.json
        echo 提示: 如不需要 OneDrive 上传，可跳过此配置
    )
)

echo ✓ 配置文件检查完成
echo.

REM 构建镜像
echo 构建 Docker 镜像...
docker-compose build
if %errorlevel% neq 0 (
    echo ❌ 镜像构建失败
    pause
    exit /b 1
)
echo ✓ 镜像构建完成
echo.

REM 首次登录
echo ==================================
echo 首次登录 Telegram
echo ==================================
echo.
echo 需要进行首次登录以获取 session
set /p login="是否现在登录? (y/n) "
if /i "%login%"=="y" (
    docker-compose run --rm telegram-downloader python telegram_downloader.py
)

echo.
echo ==================================
echo 部署选项
echo ==================================
echo.
echo 1. 启动下载器 (带 Bot 控制)
echo 2. 启动下载器 (无 Bot 控制)
echo 3. 启动下载器 + 独立上传器
echo 4. 退出
echo.

set /p choice="请选择 (1-4): "

if "%choice%"=="1" (
    echo 启动下载器 (带 Bot 控制)...
    docker-compose up -d telegram-downloader
) else if "%choice%"=="2" (
    echo 启动下载器 (无 Bot 控制)...
    docker-compose run -d --name tg-downloader telegram-downloader python telegram_downloader.py
) else if "%choice%"=="3" (
    echo 启动下载器 + 独立上传器...
    docker-compose --profile standalone up -d
) else if "%choice%"=="4" (
    echo 退出
    exit /b 0
) else (
    echo 无效选择
    pause
    exit /b 1
)

echo.
echo ==================================
echo ✓ 部署完成！
echo ==================================
echo.
echo 查看状态: docker-compose ps
echo 查看日志: docker-compose logs -f
echo 停止服务: docker-compose down
echo.
echo 如果启用了 Bot 控制，请在 Telegram 与你的 Bot 对话
echo 发送 /start 查看可用命令
echo.
pause
