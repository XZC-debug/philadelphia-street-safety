# GitHub 推送说明

本文档说明如何将本地项目推送到GitHub。

## 前置条件

1. **GitHub 账户**：如果还没有，请访问 [github.com](https://github.com) 注册
2. **Git 已安装**：验证方法：`git --version`
3. **GitHub CLI 或 SSH 密钥已配置**（可选但推荐）

## 步骤 1：在 GitHub 创建新仓库

### 方法 A：使用网页界面

1. 登录 [GitHub](https://github.com)
2. 点击右上角头像 → **Your repositories**
3. 点击 **New** 按钮
4. 填写信息：
   - **Repository name**: `philadelphia-street-safety` （或你喜欢的名字）
   - **Description**: `Street-level traffic infrastructure and crime data analysis using Google Street View, YOLO, and geospatial analysis`
   - **Visibility**: 选择 **Public**（如果你想让所有人看到）或 **Private**（仅限邀请的人）
   - **Initialize this repository with**: **不要勾选** （我们已有本地代码）
5. 点击 **Create repository**

### 方法 B：使用 GitHub CLI

```bash
gh repo create philadelphia-street-safety --public --source=. --remote=origin --push
```

## 步骤 2：配置远程仓库

替换下面的 `<username>` 为你的 GitHub 用户名，然后运行：

```bash
cd "E:\MUSA\MUSA 8010\streetview yolo3"
git remote add origin https://github.com/<username>/philadelphia-street-safety.git
```

## 步骤 3：推送代码到 GitHub

### 方法 A：使用 HTTPS（需要 Personal Access Token）

如果使用 HTTPS，GitHub 现在需要 Personal Access Token 而不是密码：

1. 生成 Token：
   - GitHub 网页 → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - 点击 **Generate new token (classic)**
   - 勾选 `repo` 和 `workflow` 权限
   - 生成并复制 Token

2. 推送代码：
```bash
git branch -M main
git push -u origin main
```
当要求输入密码时，粘贴上面生成的 Token。

### 方法 B：使用 SSH（推荐）

1. **检查是否已有 SSH 密钥**：
```bash
ls ~/.ssh/
```

如果看到 `id_rsa.pub` 和 `id_rsa`，跳到步骤 3。

2. **生成新的 SSH 密钥**（如果还没有）：
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```
按 Enter 保持默认位置，可选地设置密码。

3. **添加密钥到 SSH agent**：
```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

4. **在 GitHub 添加公钥**：
   - 复制公钥内容：`cat ~/.ssh/id_ed25519.pub`
   - GitHub 网页 → Settings → SSH and GPG keys → New SSH key
   - 粘贴公钥，给它命名（如 "My Windows Machine"）

5. **更改远程 URL 为 SSH**：
```bash
git remote set-url origin git@github.com:<username>/philadelphia-street-safety.git
```

6. **推送代码**：
```bash
git branch -M main
git push -u origin main
```

## 步骤 4：验证推送成功

1. 打开浏览器访问：`https://github.com/<username>/philadelphia-street-safety`
2. 你应该看到你的代码、README、以及所有文件

## 后续操作

### 添加主题标签（Topics）

1. 在仓库网页上，点击右边的 **About** 齿轮图标
2. 添加以下主题标签：
   - `machine-learning`
   - `object-detection`
   - `yolo`
   - `geospatial-analysis`
   - `crime-analysis`
   - `street-view`
   - `urban-planning`
   - `react`
   - `flask`

### 配置 Repository Settings（可选）

1. **保护 main 分支**：
   - Settings → Branches → Add rule
   - Branch name pattern: `main`
   - 启用 "Require pull request reviews before merging"

2. **启用 GitHub Pages**（如果想发布网站）：
   - Settings → Pages
   - Source: `gh-pages` branch（需要额外设置）

### 更新本地配置（可选但推荐）

设置 global git 配置，避免每次都输入用户信息：

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## 常见问题

### Q: 推送时出现 "fatal: not a git repository"
**A**: 确保你在项目根目录中运行命令：
```bash
cd "E:\MUSA\MUSA 8010\streetview yolo3"
```

### Q: 收到 "remote origin already exists" 错误
**A**: 之前已添加过 remote。查看和修改：
```bash
git remote -v
git remote set-url origin <new-url>
```

### Q: HTTPS 推送时收到 "Authentication failed"
**A**: 使用 Personal Access Token 而不是密码。或改用 SSH。

### Q: 推送非常慢或超时
**A**: 项目中有大文件（如 `.gitignore` 中的模型文件）。检查：
```bash
git lfs install  # 如果需要处理大文件
```

## 日后更新代码

每次修改代码后，按照标准 git 工作流推送更新：

```bash
# 查看修改
git status

# 添加所有修改
git add .

# 创建提交
git commit -m "描述你的修改"

# 推送到 GitHub
git push
```

## 协作工作流

如果多人协作，建议：

1. **为新功能创建分支**：
```bash
git checkout -b feature/your-feature-name
git push -u origin feature/your-feature-name
```

2. **提交 Pull Request**：
   - 在 GitHub 网页上，你会看到"Compare & pull request"按钮
   - 填写 PR 描述，申请合并

3. **从 main 更新代码**：
```bash
git fetch origin
git pull origin main
```

## 许可证

项目已包含 README 中的许可证信息。如果需要添加明确的 LICENSE 文件：

1. 访问 GitHub 仓库页面
2. 点击 "Add file" → "Create new file"
3. 文件名：`LICENSE`
4. 选择许可证模板（推荐 MIT 或 Apache 2.0）

## 后续资源

- [GitHub 文档](https://docs.github.com)
- [Git 教程](https://git-scm.com/doc)
- [Markdown 语法](https://guides.github.com/features/mastering-markdown/)

---

完成推送后，你可以分享仓库链接给朋友、同学和导师查看你的项目！
