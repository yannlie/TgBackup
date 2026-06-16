# 🎉 项目重命名完成！

## ✅ 重命名总结

**旧名字**: tg-to-onedrive-uploader  
**新名字**: **TgBackup**

---

## 📋 已完成的更新

### GitHub 仓库
- ✅ 仓库名称：`tg-to-onedrive-uploader` → `TgBackup`
- ✅ 仓库 URL：`https://github.com/yannlie/TgBackup`
- ✅ 远程地址已更新

### Docker 镜像
- ✅ 镜像名称：`yannlie/tg-to-onedrive-uploader` → `yannlie/tgbackup`
- ✅ 容器名称：`tg-downloader` → `tgbackup`
- ✅ 网络名称：`tg-network` → `tgbackup-network`

### 文档和代码
- ✅ README.md - 标题和徽章
- ✅ docker-compose.yml - 服务和容器名
- ✅ Dockerfile - 描述标签
- ✅ GitHub Actions - 镜像名称
- ✅ 构建脚本 - 镜像名称

---

## 🔄 下一次推送时

**新的 Docker 镜像会自动构建**：
- `yannlie/tgbackup:latest`
- `yannlie/tgbackup:main`
- `ghcr.io/yannlie/tgbackup:latest`

旧镜像 `yannlie/tg-to-onedrive-uploader` 仍然可用，但不会再更新。

---

## 🚀 新的使用方式

### Docker Hub
```bash
# 拉取镜像
docker pull yannlie/tgbackup:latest

# 运行
docker run -d --name tgbackup \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/downloads:/app/downloads \
  yannlie/tgbackup:latest
```

### docker-compose
```bash
docker-compose up -d
```

### GitHub
```bash
# 克隆仓库
git clone https://github.com/yannlie/TgBackup.git

# 更新远程地址（如果你已经克隆了旧仓库）
git remote set-url origin https://github.com/yannlie/TgBackup.git
```

---

## 📦 所有链接已更新

| 资源 | 新链接 |
|------|--------|
| **GitHub 仓库** | https://github.com/yannlie/TgBackup |
| **Docker Hub** | https://hub.docker.com/r/yannlie/tgbackup |
| **GHCR** | https://github.com/yannlie/TgBackup/pkgs/container/tgbackup |
| **Issues** | https://github.com/yannlie/TgBackup/issues |
| **Releases** | https://github.com/yannlie/TgBackup/releases |

---

## ⚠️ 迁移提示

### 对现有用户

如果有人已经在使用旧镜像：

1. **旧镜像仍然可用**（不会删除）
   ```bash
   docker pull yannlie/tg-to-onedrive-uploader:1.1.0
   ```

2. **建议迁移到新镜像**
   ```bash
   # 停止旧容器
   docker stop tg-downloader
   docker rm tg-downloader
   
   # 拉取新镜像
   docker pull yannlie/tgbackup:latest
   
   # 使用新镜像运行
   docker run -d --name tgbackup \
     -v $(pwd)/config:/app/config \
     -v $(pwd)/downloads:/app/downloads \
     yannlie/tgbackup:latest
   ```

3. **或更新 docker-compose.yml**
   ```yaml
   services:
     tgbackup:
       image: yannlie/tgbackup:latest
       container_name: tgbackup
   ```

---

## 🎯 下一步

### 立即要做的

1. ✅ **触发新镜像构建**
   - 下次 push 会自动构建 `yannlie/tgbackup`
   - 或手动触发 GitHub Actions

2. ✅ **创建新的 Release**
   ```bash
   git tag -a v1.1.1 -m "Release v1.1.1 - 项目重命名为 TgBackup"
   git push origin v1.1.1
   ```

3. ✅ **更新 Docker Hub 仓库**
   - 访问：https://hub.docker.com/repository/docker/yannlie/tgbackup
   - 设置仓库描述
   - 添加 README（会自动从 GitHub 同步）

### 可选的

1. **添加重定向说明**
   - 在旧 Docker Hub 仓库添加说明
   - 告知用户新的镜像位置

2. **更新外部引用**
   - 如果在其他地方引用了项目
   - 更新链接到新地址

---

## 📢 公告模板

如果你想通知用户，可以使用这个模板：

```markdown
# 项目重命名公告

我们的项目已重命名为 **TgBackup**！

## 新地址
- GitHub: https://github.com/yannlie/TgBackup
- Docker Hub: docker pull yannlie/tgbackup:latest

## 为什么重命名？
- 更简洁易记
- 更准确描述功能
- 更容易传播

## 旧版本怎么办？
旧镜像 `yannlie/tg-to-onedrive-uploader` 仍然可用，但建议迁移到新镜像。

## 如何迁移？
详见：https://github.com/yannlie/TgBackup/blob/main/RENAME.md

感谢支持！🚀
```

---

## 🎊 恭喜！

你的项目现在有了一个：
- ✅ 简洁的名字：**TgBackup**
- ✅ 清晰的定位：Telegram Backup Tool
- ✅ 统一的品牌：所有地方都用新名字

**新项目地址**: https://github.com/yannlie/TgBackup

---

需要我帮你：
1. 触发新镜像构建？
2. 创建 v1.1.1 Release？
3. 其他更新？

告诉我！🚀
