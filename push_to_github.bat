@echo off
echo ===================================
echo GitHub 仓库创建和推送脚本
echo ===================================
echo.

echo 步骤 1: 登录 GitHub CLI
gh auth login

echo.
echo 步骤 2: 创建 GitHub 仓库
gh repo create tg-to-onedrive-uploader --public --source=. --description "自动将 Telegram 下载的媒体文件上传到 OneDrive | Auto upload Telegram media to OneDrive"

echo.
echo 步骤 3: 推送代码到 GitHub
git branch -M main
git remote add origin https://github.com/yannlie/tg-to-onedrive-uploader.git
git push -u origin main

echo.
echo ===================================
echo 完成！仓库地址：
echo https://github.com/yannlie/tg-to-onedrive-uploader
echo ===================================
pause
