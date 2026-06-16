# Docker 镜像构建和使用指南

## 📦 预构建镜像

### Docker Hub
```bash
# 拉取最新版本
docker pull yannlie/tg-to-onedrive-uploader:latest

# 拉取指定版本
docker pull yannlie/tg-to-onedrive-uploader:1.1.0
```

### GitHub Container Registry
```bash
# 拉取最新版本
docker pull ghcr.io/yannlie/tg-to-onedrive-uploader:latest

# 拉取指定版本
docker pull ghcr.io/yannlie/tg-to-onedrive-uploader:1.1.0
```

---

## 🛠️ 手动构建镜像

### 方法 1: 使用构建脚本（推荐）

**Linux/macOS**:
```bash
chmod +x build-docker.sh
./build-docker.sh
```

**Windows**:
```bash
build-docker.bat
```

### 方法 2: 手动构建

```bash
# 构建镜像
docker build -t tg-to-onedrive-uploader:latest .

# 多平台构建（需要 buildx）
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t tg-to-onedrive-uploader:latest \
  --push .
```

---

## 🚀 使用 Docker 镜像

### 快速启动

```bash
docker run -d \
  --name tg-downloader \
  --restart unless-stopped \
  -v $(pwd)/telegram_config.json:/app/config/telegram_config.json \
  -v $(pwd)/onedrive_config.json:/app/config/onedrive_config.json \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/sessions:/app/sessions \
  yannlie/tg-to-onedrive-uploader:latest
```

### 使用 docker-compose（推荐）

```bash
# 启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

---

## 🔧 镜像标签说明

| 标签 | 说明 | 示例 |
|------|------|------|
| `latest` | 最新稳定版本 | `yannlie/tg-to-onedrive-uploader:latest` |
| `v1.1.0` | 具体版本号 | `yannlie/tg-to-onedrive-uploader:1.1.0` |
| `main` | 主分支最新构建 | `yannlie/tg-to-onedrive-uploader:main` |
| `sha-xxxxx` | 特定 commit | `yannlie/tg-to-onedrive-uploader:sha-abc1234` |

---

## 📊 镜像信息

### 镜像大小
- **压缩后**: ~200MB
- **解压后**: ~500MB

### 支持平台
- ✅ linux/amd64 (x86_64)
- ✅ linux/arm64 (ARM64)

### 基础镜像
- **Base**: `python:3.11-slim`
- **Python**: 3.11
- **操作系统**: Debian

---

## 🔐 配置 Secrets (GitHub Actions)

如果你 fork 了本项目，需要配置以下 Secrets 来启用自动构建：

### Docker Hub
1. 访问 https://github.com/YOUR_USERNAME/tg-to-onedrive-uploader/settings/secrets/actions
2. 添加以下 Secrets:
   - `DOCKER_USERNAME`: 你的 Docker Hub 用户名
   - `DOCKER_PASSWORD`: 你的 Docker Hub 访问令牌

**获取 Docker Hub Token**:
1. 访问 https://hub.docker.com/settings/security
2. 点击 "New Access Token"
3. 创建并复制 Token

### GitHub Container Registry
GitHub Container Registry 会自动使用 `GITHUB_TOKEN`，无需额外配置。

---

## 📝 自动构建触发条件

GitHub Actions 会在以下情况自动构建镜像：

1. **推送到 main 分支**
   ```bash
   git push origin main
   ```
   - 构建标签: `latest`, `main`

2. **创建版本标签**
   ```bash
   git tag v1.1.0
   git push origin v1.1.0
   ```
   - 构建标签: `1.1.0`, `1.1`, `1`, `latest`

3. **Pull Request**
   - 仅构建测试，不推送

4. **手动触发**
   - 在 GitHub Actions 页面点击 "Run workflow"

---

## 🏷️ 推送到 Docker Hub

### 手动推送

```bash
# 登录 Docker Hub
docker login

# 标记镜像
docker tag tg-to-onedrive-uploader:latest yannlie/tg-to-onedrive-uploader:1.1.0
docker tag tg-to-onedrive-uploader:latest yannlie/tg-to-onedrive-uploader:latest

# 推送镜像
docker push yannlie/tg-to-onedrive-uploader:1.1.0
docker push yannlie/tg-to-onedrive-uploader:latest
```

### 使用脚本推送

脚本会自动完成登录、标记、推送：
```bash
./build-docker.sh
```

---

## 🧪 测试镜像

### 基础测试

```bash
# 测试 Python 版本
docker run --rm yannlie/tg-to-onedrive-uploader:latest python --version

# 测试依赖
docker run --rm yannlie/tg-to-onedrive-uploader:latest python -c "import telethon; print('OK')"

# 查看帮助
docker run --rm yannlie/tg-to-onedrive-uploader:latest python telegram_downloader.py --help
```

### 完整测试

```bash
# 进入容器
docker run -it --rm \
  -v $(pwd)/telegram_config.json:/app/config/telegram_config.json \
  yannlie/tg-to-onedrive-uploader:latest bash

# 容器内测试
python telegram_downloader.py --help
python test_project.py
```

---

## 🌐 镜像仓库

### Docker Hub
- **地址**: https://hub.docker.com/r/yannlie/tg-to-onedrive-uploader
- **拉取命令**: `docker pull yannlie/tg-to-onedrive-uploader`

### GitHub Container Registry
- **地址**: https://github.com/yannlie/tg-to-onedrive-uploader/pkgs/container/tg-to-onedrive-uploader
- **拉取命令**: `docker pull ghcr.io/yannlie/tg-to-onedrive-uploader`

---

## 🔄 更新镜像

### 用户更新

```bash
# 拉取最新镜像
docker pull yannlie/tg-to-onedrive-uploader:latest

# 重启容器
docker-compose down
docker-compose up -d
```

### 自动更新（Watchtower）

```bash
# 安装 Watchtower
docker run -d \
  --name watchtower \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower \
  --interval 3600 \
  tg-downloader
```

---

## 🐛 故障排查

### 镜像拉取失败

```bash
# 检查网络
ping hub.docker.com

# 尝试其他镜像源
docker pull ghcr.io/yannlie/tg-to-onedrive-uploader:latest
```

### 容器启动失败

```bash
# 查看日志
docker logs tg-downloader

# 检查配置
docker run --rm -v $(pwd)/telegram_config.json:/app/config/telegram_config.json \
  yannlie/tg-to-onedrive-uploader:latest \
  cat /app/config/telegram_config.json
```

### 构建失败

```bash
# 清理缓存
docker system prune -a

# 重新构建
docker build --no-cache -t tg-to-onedrive-uploader:latest .
```

---

## 📦 多阶段构建优化

当前 Dockerfile 已经优化：
- ✅ 使用 Python slim 镜像（减小体积）
- ✅ 合并 RUN 命令（减少层数）
- ✅ 清理 apt 缓存
- ✅ 使用 pip --no-cache-dir
- ✅ 多平台支持

---

## 🔒 安全建议

1. **不要在镜像中包含敏感信息**
   - 配置文件通过 volume 挂载
   - Session 文件通过 volume 持久化

2. **定期更新基础镜像**
   ```bash
   docker pull python:3.11-slim
   docker build --no-cache -t tg-to-onedrive-uploader:latest .
   ```

3. **扫描镜像漏洞**
   ```bash
   docker scan yannlie/tg-to-onedrive-uploader:latest
   ```

---

## 💡 最佳实践

1. **使用特定版本标签**
   ```yaml
   # 生产环境
   image: yannlie/tg-to-onedrive-uploader:1.1.0
   
   # 而不是
   image: yannlie/tg-to-onedrive-uploader:latest
   ```

2. **资源限制**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2'
         memory: 2G
   ```

3. **健康检查**
   ```yaml
   healthcheck:
     test: ["CMD", "python", "-c", "import os; exit(0 if os.path.exists('/app/logs/tg_downloader.log') else 1)"]
     interval: 30s
     timeout: 10s
     retries: 3
   ```

---

## 📚 相关文档

- [Docker 部署指南](DOCKER.md)
- [主文档](README.md)
- [项目结构](PROJECT_STRUCTURE.md)

---

**最后更新**: 2024-06-16
