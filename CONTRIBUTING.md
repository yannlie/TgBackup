# 贡献指南

感谢你对本项目的关注！欢迎贡献代码、报告问题或提出建议。

## 如何贡献

### 报告 Bug

如果你发现了 Bug，请[创建 Issue](https://github.com/yannlie/tg-to-onedrive-uploader/issues/new) 并包含：

- 问题描述
- 复现步骤
- 预期行为
- 实际行为
- 运行环境（操作系统、Python 版本）
- 相关日志（脱敏后）

### 提出新功能

欢迎提出新功能建议！请先[创建 Issue](https://github.com/yannlie/tg-to-onedrive-uploader/issues/new) 讨论：

- 功能描述
- 使用场景
- 实现思路（可选）

### 提交代码

1. **Fork 本仓库**

2. **克隆到本地**
   ```bash
   git clone https://github.com/YOUR_USERNAME/tg-to-onedrive-uploader.git
   cd tg-to-onedrive-uploader
   ```

3. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **开发和测试**
   - 遵循现有代码风格
   - 添加必要的注释
   - 测试你的改动

5. **提交改动**
   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   ```

6. **推送到 GitHub**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **创建 Pull Request**
   - 描述你的改动
   - 关联相关 Issue

## 代码规范

### Python 代码风格

- 遵循 [PEP 8](https://pep8.org/)
- 使用 4 空格缩进
- 函数和类添加文档字符串
- 变量命名使用小写下划线

### Commit 信息规范

使用语义化的 commit 信息：

- `feat: 新功能`
- `fix: 修复 Bug`
- `docs: 文档更新`
- `style: 代码格式调整`
- `refactor: 重构代码`
- `test: 测试相关`
- `chore: 构建/工具相关`

示例：
```
feat: 添加多账户支持
fix: 修复大文件上传失败的问题
docs: 更新配置说明
```

## 开发环境设置

```bash
# 安装依赖
pip install -r requirements.txt

# 安装开发依赖（可选）
pip install pytest black flake8

# 代码格式化
black *.py

# 代码检查
flake8 *.py

# 运行测试
pytest
```

## 需要帮助的领域

欢迎在以下方面贡献：

- 📝 文档翻译（英文、日文等）
- 🐛 测试和 Bug 修复
- ✨ 新功能开发
- 🎨 UI/UX 改进（如果添加 Web 界面）
- 📦 打包和分发（Docker、可执行文件等）

## 行为准则

- 尊重所有贡献者
- 保持友好和建设性的讨论
- 接受不同的观点和经验水平

## 许可证

通过贡献代码，你同意你的贡献将在 MIT 许可证下发布。
