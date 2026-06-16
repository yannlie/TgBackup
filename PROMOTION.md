# TgBackup 推广素材包

## 📝 Reddit 发帖

### r/selfhosted (最重要)

**标题**:
```
[Project] TgBackup - Automatically backup Telegram media to OneDrive with one Docker command
```

**正文**:
```markdown
Hi r/selfhosted!

I built **TgBackup** - a tool that automatically backs up Telegram channel/group media to OneDrive.

## Why I built this

I was tired of manually downloading media from Telegram channels and wanted automatic cloud backup. After trying existing solutions, I decided to build my own with better features.

## Key Features

- 🔄 **Real-time monitoring** - Watches multiple channels/groups
- 📥 **History download** - Download all past messages  
- 🤖 **Bot remote control** - Manage via Telegram bot (10 commands)
- ☁️ **OneDrive integration** - Auto upload with smart deduplication
- 🐳 **One-line Docker deploy** - `docker pull yannlie/tgbackup`
- 📱 **Multi-platform** - Supports amd64 and arm64
- 🌍 **Full English docs** - Complete documentation

## Quick Start

```bash
docker pull yannlie/tgbackup:latest
docker-compose up -d
```

That's it! Configure and run.

## Use Cases

- Backup resource channels automatically
- Archive important groups
- Save media from private channels
- Scheduled backups with history

## Tech Stack

Python, Telethon, Docker, FastAPI (web UI coming soon)

## Links

- **GitHub**: https://github.com/yannlie/TgBackup
- **Docker Hub**: https://hub.docker.com/r/yannlie/tgbackup
- **Documentation**: Complete setup guides and FAQs

## What's Next

Planning v1.2 with web management interface. Feedback and suggestions welcome!

---

**Questions? Ask away!** I'm actively developing and happy to help with setup.
```

---

### r/DataHoarder

**标题**:
```
TgBackup - Automated Telegram media archiving to OneDrive
```

**正文**:
```markdown
Fellow data hoarders,

Built a tool specifically for archiving Telegram content: **TgBackup**

## Perfect for

- 📚 Archiving resource channels (ebooks, courses, movies)
- 💾 Backing up private groups before they disappear
- 🎥 Downloading entire channel history
- ☁️ Automatic cloud backup without manual work

## Features

- Downloads photos, videos, documents, audio
- Smart filtering by size/type/extension
- Deduplication (won't download twice)
- Bot control (check status from phone)
- Docker deployment (runs 24/7 on server)

## Real-world usage

I use it to backup:
- 15 resource channels (~500GB media)
- 5 private groups (before they get deleted)
- Auto-sync to OneDrive every night

## Get started

```bash
docker pull yannlie/tgbackup:latest
```

GitHub: https://github.com/yannlie/TgBackup

Docker Hub: https://hub.docker.com/r/yannlie/tgbackup

---

Any questions about setup or features?
```

---

### r/Telegram

**标题**:
```
Built a Telegram media backup tool with bot control - TgBackup
```

**正文**:
```markdown
Hey Telegram community!

Created **TgBackup** to solve my own problem - automatically backing up media from channels I follow.

## What it does

- Monitors channels/groups for new media
- Downloads automatically to local/OneDrive
- Control everything via Telegram bot
- Download channel history with one command

## Bot Commands

- `/status` - Check running status
- `/stats` - View download statistics  
- `/history @channel 100` - Download last 100 messages
- `/add @channel` - Start monitoring new channel
- And 6 more commands

## Why I built this

I follow many resource channels and wanted automatic backup before content gets deleted. Also wanted to access from OneDrive anywhere.

## Try it

One-line Docker install:
```bash
docker pull yannlie/tgbackup:latest
```

GitHub: https://github.com/yannlie/TgBackup

Full docs, FAQ, and Docker guide included.

---

Happy to answer questions!
```

---

## 📝 V2EX 发帖

**节点**: 创造

**标题**:
```
[开源] TgBackup - Telegram 媒体自动备份工具，一键 Docker 部署
```

**正文**:
```
## 项目介绍

TgBackup 是一个 Telegram 媒体自动备份工具，支持实时监听频道/群组，自动下载媒体文件并备份到 OneDrive。

## 为什么做这个

之前用别人的 Telegram 下载工具，但缺少 OneDrive 集成，也没有 Bot 远程控制。于是自己从零写了一个功能更完整的版本。

## 核心功能

- 🔄 实时监听多个频道/群组
- 📥 下载历史消息（支持全部下载）
- 🤖 Bot 远程控制（10 个命令）
- ☁️ OneDrive 自动上传
- 🐳 Docker 一键部署
- 📱 多平台支持（amd64 + arm64）

## 使用场景

1. 自动备份资源频道
2. 群组消息归档
3. 私有频道媒体保存
4. 定时备份到云盘

## 快速开始

```bash
docker pull yannlie/tgbackup:latest
docker-compose up -d
```

## 技术栈

- Python + Telethon
- Docker + GitHub Actions
- 完整的中文文档（30000+ 字）
- 自动化 CI/CD

## 项目地址

- GitHub: https://github.com/yannlie/TgBackup
- Docker Hub: https://hub.docker.com/r/yannlie/tgbackup
- 文档齐全，FAQ 详细

## 开发计划

- v1.2: Web 管理界面（开发中）
- v1.3: 邮件/Telegram 通知
- v1.4: 数据库存储和搜索

## 求 Star ⭐

开源不易，如果觉得有用请给个 Star 支持一下！

欢迎反馈和建议！
```

---

## 📝 少数派投稿

**标题**:
```
用 TgBackup 自动备份 Telegram 频道内容到 OneDrive
```

**大纲**:
```markdown
## 前言
- 为什么需要备份 Telegram 内容
- 现有方案的问题

## TgBackup 介绍
- 功能特性
- 使用场景

## 详细教程
1. 准备工作（获取 API）
2. Docker 部署
3. 配置说明
4. Bot 控制使用
5. 高级技巧

## 实战案例
- 备份资源频道
- 定时任务设置
- 多频道管理

## 总结
- 优势和不足
- 未来规划

## 参考链接
```

---

## 🎨 Twitter/X 发推

**推文 1**:
```
🚀 Built TgBackup - auto backup Telegram media to OneDrive

✅ One-line Docker install
✅ Bot remote control  
✅ History download
✅ Multi-platform support

Perfect for backing up resource channels before they disappear!

🔗 https://github.com/yannlie/TgBackup

#Telegram #Docker #SelfHosted #OpenSource
```

**推文 2** (with screenshot):
```
TgBackup Bot commands 🤖

Control your Telegram backup from anywhere:
• /status - Check status
• /stats - View statistics
• /history - Download past messages
• /add - Monitor new channel

No more manual downloads! 

GitHub: https://github.com/yannlie/TgBackup

#automation #productivity
```

---

## 📱 Telegram 频道/群组

### 推广文案

```
📢 TgBackup - 开源 Telegram 媒体备份工具

功能：
✅ 自动监听频道下载
✅ 历史消息下载
✅ Bot 远程控制
✅ OneDrive 自动上传
✅ Docker 一键部署

适合：
• 备份资源频道
• 归档重要群组
• 自动化下载任务

项目地址：
https://github.com/yannlie/TgBackup

Docker 安装：
docker pull yannlie/tgbackup:latest

完整中文文档，开箱即用！

求 Star ⭐ 支持开源！
```

---

## 📧 Product Hunt 准备

**Tagline**:
```
Automatically backup Telegram media to OneDrive with Docker
```

**Description**:
```
TgBackup automates Telegram media backup with one Docker command. 

Key features:
• Real-time channel monitoring
• Bot remote control (10 commands)
• Download message history
• OneDrive auto-upload
• Multi-platform support
• Complete documentation

Perfect for archiving resource channels, backing up groups, 
and automated cloud storage.

Open source, self-hosted, and easy to deploy.
```

---

## 🎬 YouTube 视频脚本

**标题**: "TgBackup: Backup Telegram Media Automatically"

**时长**: 60 秒

**脚本**:
```
[0-10s] Introduction
"Tired of manually downloading Telegram media? 
Meet TgBackup - automatic Telegram backup to OneDrive"

[10-20s] Problem
"Channels get deleted, groups disappear, 
important media lost forever"

[20-40s] Solution  
"TgBackup monitors channels 24/7
Downloads automatically
Backs up to OneDrive
Control from your phone via bot"

[40-50s] Demo
"One line to install:
docker pull yannlie/tgbackup
Configure and run
That's it!"

[50-60s] CTA
"Link in description
Free and open source
Star on GitHub!"
```

---

## 📊 数据追踪

创建表格追踪推广效果：

| 平台 | 发布日期 | 点赞 | 评论 | GitHub Stars | Docker Pulls |
|------|---------|------|------|--------------|--------------|
| Reddit r/selfhosted | - | - | - | - | - |
| Reddit r/DataHoarder | - | - | - | - | - |
| V2EX | - | - | - | - | - |
| Twitter | - | - | - | - | - |
| Product Hunt | - | - | - | - | - |

---

## 🎯 KPI 指标

**Week 1 目标**:
- Reddit: 50+ upvotes
- V2EX: 100+ 感谢
- GitHub Stars: 100+
- Docker Pulls: 500+

**Week 2 目标**:
- GitHub Stars: 300+
- Docker Pulls: 1500+
- 5+ 用户反馈

**Month 1 目标**:
- GitHub Stars: 1000+
- Docker Pulls: 5000+
- 50+ 活跃用户
- 10+ Pull Requests

---

使用这个素材包开始推广！需要我帮你：
1. 修改任何文案
2. 制作截图
3. 准备其他素材

吗？
