# 部署后端到云端（Render.com）

本指南说明如何将Flask后端部署到Render.com（免费）。

## 🚀 使用 Render.com 部署（推荐）

### 第1步：创建 Render 账户

1. 访问 https://render.com
2. 点击 **Sign Up**
3. 使用 GitHub 账户登录（推荐）

### 第2步：准备GitHub仓库

确保以下文件已提交到GitHub：

```
✓ dashboard/backend/requirements.txt（包含gunicorn）
✓ dashboard/backend/Procfile
✓ dashboard/backend/app.py
✓ dashboard/backend/config.py
✓ dashboard/backend/data_manager.py
✓ dashboard/backend/preprocess_data.py
✓ dashboard/backend/preprocess_incidents.py
✓ dashboard/backend/processed_data/（JSON文件）
```

推送到GitHub：
```bash
cd "E:\MUSA\MUSA 8010\streetview yolo3"
git add .
git commit -m "Prepare for cloud deployment: Add Procfile and gunicorn"
git push origin main
```

### 第3步：在 Render 创建新服务

1. 登录 Render 仪表板
2. 点击 **New** → **Web Service**
3. 连接 GitHub 仓库：
   - 选择你的 `philadelphia-street-safety` 仓库
   - 点击 **Connect**

### 第4步：配置部署

在部署配置表单中填写：

| 字段 | 值 |
|------|-----|
| **Name** | `philadelphia-street-safety-api` |
| **Region** | 选择离你最近的地区 |
| **Branch** | `main` |
| **Root Directory** | `dashboard/backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn -w 1 -b 0.0.0.0:$PORT app:app` |

### 第5步：添加环境变量（可选）

如果后端需要环境变量（如API密钥），在 **Environment** 部分添加：

```
FLASK_ENV=production
```

### 第6步：部署

1. 点击 **Create Web Service**
2. 等待部署完成（约 2-5 分钟）
3. 你会看到一个 **Live URL**，类似：
   ```
   https://philadelphia-street-safety-api-xxxx.onrender.com
   ```

---

## 🔗 更新前端配置

部署成功后，你需要更新前端的 API 地址：

### 步骤 1：创建 .env 文件

在 `dashboard/frontend/` 目录创建 `.env` 文件：

```bash
cd "E:\MUSA\MUSA 8010\streetview yolo3\dashboard\frontend"
```

创建 `.env` 文件，内容为：

```
REACT_APP_API_URL=https://philadelphia-street-safety-api-xxxx.onrender.com
```

**替换 `xxxx` 为你的 Render URL**

### 步骤 2：重新构建前端

```bash
npm run build
```

### 步骤 3：复制到 docs 文件夹

```bash
cp -r build/* ../docs/
```

### 步骤 4：推送到 GitHub

```bash
cd ..
git add .
git commit -m "Update: API endpoint for cloud deployment"
git push origin main
```

---

## ✅ 验证部署

### 测试后端 API

访问：`https://philadelphia-street-safety-api-xxxx.onrender.com/api/health`

你应该看到：
```json
{
  "status": "ok",
  "message": "Philadelphia Streetscape Dashboard API is running"
}
```

### 测试完整应用

访问 GitHub Pages：
https://xzc-debug.github.io/philadelphia-street-safety/

应该能看到地图和数据加载正常！

---

## 🐛 常见问题

### 问题 1：部署失败

**检查**：
- Procfile 文件名是否正确（无 .txt 扩展名）
- requirements.txt 是否包含 gunicorn
- app.py 是否在 dashboard/backend 目录

### 问题 2：API 返回 404 或超时

**原因**：后端尚未启动或数据未加载
**解决**：
- 在 Render 仪表板中查看日志
- 等待部署完全完成（通常 5 分钟）
- 检查 `processed_data/` 文件夹是否已上传

### 问题 3：GitHub Pages 显示空白

**原因**：前端 .env 文件中的 API 地址错误
**解决**：
1. 检查 `.env` 文件中的 URL 是否正确
2. 重新运行 `npm run build` 和 `cp -r build/* ../docs/`
3. 推送到 GitHub

### 问题 4：CORS 错误

**原因**：前端和后端域名不匹配
**解决**：后端 Flask 应用已配置 CORS，应该不会有此问题。如有问题，检查 `app.py` 中的 CORS 配置。

---

## 📊 监控应用

登录 Render 仪表板：
- 查看实时日志
- 监控 CPU 和内存使用
- 设置告警

---

## 🔄 更新应用

每次更新代码时：

```bash
# 1. 在 dashboard/backend 中修改代码
# 2. 提交并推送到 GitHub
git add .
git commit -m "Update: backend improvements"
git push origin main

# 3. Render 会自动重新部署（您可以在 Render 仪表板中查看）

# 4. 如果更新了前端，也要重新构建并推送
cd dashboard/frontend
npm run build
cp -r build/* ../docs/
cd ..
git add docs/
git commit -m "Update: frontend build"
git push origin main
```

---

## 💰 费用

**Render.com 免费计划**：
- 每月 750 小时免费运行时间
- 足以运行一个应用全天（24×30≈720小时）
- 如需额外资源，可升级到付费计划

---

## 🎉 完成！

你的应用现在已经在云端运行！

- **前端**：https://xzc-debug.github.io/philadelphia-street-safety/
- **后端 API**：https://philadelphia-street-safety-api-xxxx.onrender.com/api/

任何人都可以通过 GitHub Pages 链接访问你的应用了！

