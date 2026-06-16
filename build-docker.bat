@echo off
chcp 65001 >nul
REM Docker 镜像构建和推送脚本 - Windows

echo ==================================
echo Docker 镜像构建和推送
echo ==================================
echo.

REM 配置
set IMAGE_NAME=tg-to-onedrive-uploader
set DOCKER_USERNAME=yannlie

REM 获取版本号
for /f "tokens=2 delims='" %%a in ('findstr "__version__" telegram_downloader.py') do set VERSION=%%a

echo 镜像名称: %DOCKER_USERNAME%/%IMAGE_NAME%
echo 版本: %VERSION%
echo.

REM 检查 Docker
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 错误: 未安装 Docker
    pause
    exit /b 1
)

echo ✓ Docker 已安装
echo.

REM 构建镜像
echo ==================================
echo 1. 构建 Docker 镜像
echo ==================================
echo.

docker build -t %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION% -t %DOCKER_USERNAME%/%IMAGE_NAME%:latest .

if %errorlevel% neq 0 (
    echo ❌ 镜像构建失败
    pause
    exit /b 1
)

echo ✓ 镜像构建成功
echo.

REM 测试镜像
echo ==================================
echo 2. 测试镜像
echo ==================================
echo.

docker run --rm %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION% python --version
docker run --rm %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION% python -c "import telethon; print('Telethon OK')"

echo ✓ 镜像测试通过
echo.

REM 推送镜像
echo ==================================
echo 3. 推送镜像到 Docker Hub
echo ==================================
echo.

set /p PUSH="是否推送镜像到 Docker Hub? (y/n) "

if /i "%PUSH%"=="y" (
    echo 登录 Docker Hub...
    docker login

    echo 推送镜像...
    docker push %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION%
    docker push %DOCKER_USERNAME%/%IMAGE_NAME%:latest

    echo ✓ 镜像推送成功
    echo.
    echo 镜像地址:
    echo   docker pull %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION%
    echo   docker pull %DOCKER_USERNAME%/%IMAGE_NAME%:latest
) else (
    echo 跳过推送
)

echo.
echo ==================================
echo 完成！
echo ==================================
echo.
echo 使用方法:
echo   docker run -d --name tg-downloader ^
echo     -v %cd%/config:/app/config ^
echo     -v %cd%/downloads:/app/downloads ^
echo     %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION%
echo.
pause
