# 快速开始 - 预处理数据工作流

新的数据加载方式已优化为**离线预处理 + 快速API响应**

## 工作流程

```
1. 运行预处理脚本 (一次性)
   ↓
2. 启动Flask后端 (秒级启动)
   ↓
3. 前端快速加载数据 (无超时问题)
```

---

## 🚀 运行步骤

### **第1次：数据预处理（5-10分钟）**

```powershell
cd "E:\MUSA\MUSA 8010\streetview yolo3\dashboard\backend"
.\venv\Scripts\Activate.ps1
python preprocess_data.py
```

你会看到：
```
[INFO] Starting data preprocessing...
[OK] Loaded 152555 incident records
[INFO] Processing Center City...
  - Traffic Lights: 76
  - Stop Signs: 12
[OK] Saved Center City.json
...
[SUCCESS] Data preprocessing completed!
```

**结果文件保存在：** `backend/processed_data/`

```
processed_data/
├── metadata.json
├── comparison.json
├── Center City.json
├── KENSINGTON.json
├── POINT_BREEZE.json
└── UNIVERSITY_CITY.json
```

### **第2次及之后：正常启动**

**启动后端：**
```powershell
cd "E:\MUSA\MUSA 8010\streetview yolo3\dashboard\backend"
.\venv\Scripts\Activate.ps1
python app.py
```

后端会在 **1-2 秒内启动**：
```
[INFO] Loading preprocessed data...
[OK] Loaded metadata: 152555 incidents
[OK] Loaded Center City
[OK] Loaded KENSINGTON
[OK] Loaded POINT_BREEZE
[OK] Loaded UNIVERSITY_CITY
[OK] Loaded comparison data for 4 neighborhoods
* Running on http://127.0.0.1:5000
```

**启动前端：**
```powershell
cd "E:\MUSA\MUSA 8010\streetview yolo3\dashboard\frontend"
npm start
```

前端会立即加载（无超时！）

---

## 📊 数据更新

如果源数据有改动（GeoJSON或CSV）：

1. **重新运行预处理：**
   ```powershell
   python preprocess_data.py
   ```

2. **重启后端：**
   ```powershell
   python app.py
   ```

就这样，无需其他操作！

---

## ⚡ 性能改进对比

| 指标 | 旧方式 | 新方式 |
|------|--------|--------|
| **后端启动时间** | 15-30秒 | 1-2秒 |
| **API响应时间** | 2-5秒 | <100ms |
| **前端加载时间** | 30秒+ (超时) | 3-5秒 |
| **数据刷新** | 每次启动 | 按需运行 |

---

## 🔧 故障排除

### 后端启动失败："Run preprocess_data.py first!"

```powershell
python preprocess_data.py
```

首次必须运行预处理！

### 修改源数据后没有更新

```powershell
python preprocess_data.py  # 重新预处理
python app.py              # 重启后端
```

### 预处理速度慢

这是正常的！152万条数据只需要处理一次。之后API会非常快。

---

## 📁 各文件用途

| 文件 | 作用 |
|------|------|
| `preprocess_data.py` | **一次性运行**：预处理所有数据 |
| `processed_data/` | 预处理后的JSON数据（用于快速读取） |
| `data_manager.py` | 简化的数据管理器（只读JSON） |
| `app.py` | Flask API（调用data_manager） |

---

## 💡 下一步

1. ✅ 运行 `python preprocess_data.py`
2. ✅ 启动后端 `python app.py`
3. ✅ 启动前端 `npm start`
4. ✅ 打开 `http://localhost:3000`

享受快速的仪表板！🎉

