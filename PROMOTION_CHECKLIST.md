# 🚀 TgBackup 推广执行清单

## ⏰ 今天立即完成（2小时）

### 第一步：完善 GitHub 仓库（30分钟）

- [ ] **添加 Topics**
  - 访问：https://github.com/yannlie/TgBackup
  - 点击右侧 "About" 旁边的齿轮图标
  - 添加：`telegram`, `backup`, `onedrive`, `docker`, `python`, `telegram-bot`, `automation`, `media-downloader`, `self-hosted`, `cloud-storage`

- [ ] **更新仓库描述**
  ```
  🚀 TgBackup - Automatically backup Telegram media to OneDrive with Docker. Real-time monitoring, bot control, history download.
  ```

- [ ] **添加网站链接**
  - https://hub.docker.com/r/yannlie/tgbackup

- [ ] **创建 GitHub Social Preview**
  - 访问：Settings → Options → Social preview
  - 上传图片（1200x630px）或使用 GitHub 自动生成

### 第二步：准备截图（30分钟）

创建 3 张关键截图并保存到 `docs/screenshots/`：

- [ ] **Screenshot 1: Docker 一键部署**
  ```bash
  # 截图终端执行这些命令
  docker pull yannlie/tgbackup:latest
  docker-compose up -d
  docker ps
  ```

- [ ] **Screenshot 2: Bot 控制界面**
  ```
  # 截图 Telegram Bot 对话
  /status
  /stats  
  /list
  ```

- [ ] **Screenshot 3: 下载进度**
  ```bash
  # 截图日志输出
  docker-compose logs -f
  ```

### 第三步：发布到 Reddit（30分钟）

- [ ] **Reddit 账号准备**
  - 确保账号有足够 Karma（至少 100+）
  - 如果没有，先在其他帖子评论积累

- [ ] **发布到 r/selfhosted**
  - 访问：https://www.reddit.com/r/selfhosted/submit
  - 选择 "Text Post"
  - 复制 PROMOTION.md 中的内容
  - 添加 Flair: "Project Showcase"
  - 发布时间：美国时间早上 9-11点（北京时间晚上 9-11点）

- [ ] **准备回复模板**
  ```markdown
  ## 常见问题回复

  Q: 需要付费吗？
  A: 完全免费开源！MIT 协议。

  Q: 安全吗？会偷我的数据吗？
  A: 完全本地运行，代码开源可审计，不会上传任何数据到第三方。

  Q: 支持 Google Drive 吗？
  A: 目前只支持 OneDrive，Google Drive 在路线图中（v2.1）。

  Q: 可以下载付费频道吗？
  A: 只要你有权限访问的频道都可以下载。

  Q: 占用多少资源？
  A: 默认限制 2GB 内存，0.5-2 CPU，可以自己调整。
  ```

### 第四步：发布到 V2EX（30分钟）

- [ ] **V2EX 账号准备**
  - 确保账号注册超过 30 天
  - 有一定活跃度

- [ ] **发布到创造节点**
  - 访问：https://v2ex.com/new/create
  - 复制 PROMOTION.md 中的中文内容
  - 添加标签：`开源`, `docker`, `telegram`
  - 发布时间：工作日早上 9-10点或晚上 8-9点

---

## 📅 本周计划（每天1-2小时）

### Day 1（周一）- Reddit 和 V2EX

- [x] 准备截图
- [x] 发布到 r/selfhosted
- [x] 发布到 V2EX
- [ ] 监控评论，及时回复

**重要**：发帖后 **前2小时** 是黄金时间，要：
- 每 15 分钟刷新一次
- 所有评论都要回复
- 回复要友好、详细

### Day 2（周二）- 扩大影响

- [ ] 发布到 r/DataHoarder
  - 时间：美国时间早上 9-11点
  
- [ ] 发布到 r/Telegram
  - 时间：美国时间下午 2-4点

- [ ] 在 V2EX 帖子持续回复

- [ ] 记录数据：
  ```
  Reddit upvotes: ___
  V2EX 感谢: ___
  GitHub Stars: ___
  Docker Pulls: ___
  ```

### Day 3（周三）- 社交媒体

- [ ] **Twitter/X 发推**
  - 3 条推文（带截图）
  - 使用话题标签
  - @相关大号（如 @Docker, @Telegram）

- [ ] **制作 30 秒演示视频**
  - 工具：OBS Studio / QuickTime
  - 上传到 YouTube
  - 标题：TgBackup - Telegram Media Backup Tool

- [ ] **少数派投稿**
  - 访问：https://sspai.com/write
  - 使用教程形式
  - 3000+ 字详细教程

### Day 4（周四）- Telegram 推广

- [ ] **加入相关 Telegram 群组**
  - Docker 中文群
  - Self-hosted 群组
  - Telegram 开发者群
  - Python 中文社区

- [ ] **适度推广**（不要刷屏）
  ```
  Hi 大家，做了一个 Telegram 媒体备份工具，
  可以自动下载频道内容到 OneDrive，
  开源免费，Docker 部署。
  
  GitHub: https://github.com/yannlie/TgBackup
  
  有在用的朋友吗？欢迎反馈！
  ```

### Day 5（周五）- 内容营销

- [ ] **写技术博客**
  - 标题：《从零开发 Telegram 备份工具的踩坑记录》
  - 发布到：掘金、CSDN、博客园
  
- [ ] **发布到 Hacker News**
  - https://news.ycombinator.com/submit
  - 标题：Show HN: TgBackup - Backup Telegram media to OneDrive
  - 最佳时间：美国时间早上 7-9点

### Day 6-7（周末）- 总结和优化

- [ ] **收集反馈**
  - 整理所有评论和建议
  - 创建 GitHub Issues
  - 优先级排序

- [ ] **数据分析**
  ```
  总结表格：
  平台        | 曝光 | 点击 | Stars | 转化率
  ------------|------|------|-------|-------
  Reddit      |      |      |       |
  V2EX        |      |      |       |
  Twitter     |      |      |       |
  Telegram    |      |      |       |
  ```

- [ ] **准备下周计划**

---

## 📊 追踪指标

### 每天更新

```markdown
## Day 1 - 2024-06-__

### 数据
- GitHub Stars: ___
- Docker Pulls: ___
- GitHub Traffic: ___ visitors
- Reddit upvotes: ___
- V2EX 感谢: ___

### 用户反馈
1. 
2. 
3. 

### 改进点
1. 
2. 
```

---

## 🎯 Week 1 目标检查

- [ ] Reddit r/selfhosted: 50+ upvotes
- [ ] V2EX: 100+ 感谢
- [ ] GitHub Stars: 100+
- [ ] Docker Pulls: 500+
- [ ] 收到 5+ 用户反馈
- [ ] 创建 3+ GitHub Issues（来自用户）

---

## ✅ 成功标志

### 短期（1周内）
- ✅ 帖子出现在 r/selfhosted 首页
- ✅ V2EX 帖子进入今日热门
- ✅ GitHub Trending（任何语言）

### 中期（2-4周）
- ✅ 有用户主动提 PR
- ✅ 有人在其他平台推荐你的项目
- ✅ Docker Hub 有用户留下 Star

### 长期（1-3月）
- ✅ Awesome 系列收录
- ✅ 有公司/团队使用
- ✅ 被其他项目集成

---

## 🚫 避坑指南

### 不要做的事

1. **不要刷屏**
   - 同一个群不要重复发
   - 不要连续发多个平台

2. **不要防御性**
   - 收到批评虚心接受
   - 不要和用户争论

3. **不要夸大宣传**
   - 实事求是介绍功能
   - 不要说"最好"、"完美"

4. **不要忽视反馈**
   - 每个评论都要回复
   - 24 小时内响应 Issue

### 要做的事

1. **真诚友好**
   - 把用户当朋友
   - 感谢每个反馈

2. **快速响应**
   - 发帖后 2 小时内高度关注
   - Issue 24 小时内回复

3. **持续更新**
   - 根据反馈快速迭代
   - 让用户看到进展

4. **建立信任**
   - 代码开源
   - 文档详细
   - 承诺能兑现

---

## 📞 需要帮助？

如果遇到：
- 不知道怎么回复评论
- 遇到技术问题反馈
- 不确定下一步做什么

随时问我！

---

## 🎊 开始行动！

**现在就开始第一步**：

1. 打开 https://github.com/yannlie/TgBackup
2. 添加 Topics
3. 准备第一张截图

**记住**：
- 执行 > 完美
- 发布 > 准备
- 行动 > 计划

祝你成功！🚀
