# 费城街景交通设施分析 - 后端服务

Flask + GeoPandas 构建的地理空间数据API服务

## 快速开始

### 1️⃣ 安装依赖

```bash
cd dashboard/backend
pip install -r requirements.txt
```

### 2️⃣ 运行服务

```bash
python app.py
```

服务将启动在 `http://localhost:5000`

### 3️⃣ 测试API

```bash
# 健康检查
curl http://localhost:5000/api/health

# 获取所有街区
curl http://localhost:5000/api/neighborhoods

# 获取Center City的地理数据
curl http://localhost:5000/api/data/Center%20City

# 获取统计数据
curl http://localhost:5000/api/stats/Center%20City

# 比较所有街区
curl http://localhost:5000/api/comparison
```

---

## 📡 API 文档

### 基础端点

#### 1. 健康检查
```
GET /api/health
```
**响应：**
```json
{
  "status": "ok",
  "message": "Philadelphia Streetscape Dashboard API is running"
}
```

---

#### 2. 获取所有街区
```
GET /api/neighborhoods
```
**响应：**
```json
{
  "status": "success",
  "data": [
    {
      "name": "Center City",
      "traffic_lights": 141,
      "stop_signs": 12,
      "incidents": 5000
    },
    ...
  ]
}
```

---

#### 3. 获取街区的地理数据
```
GET /api/data/<neighborhood>
```

**参数：**
- `neighborhood`: 街区名称 (Center City, KENSINGTON, POINT_BREEZE, UNIVERSITY_CITY)

**响应：**
```json
{
  "status": "success",
  "neighborhood": "Center City",
  "data": {
    "traffic_lights": {
      "type": "FeatureCollection",
      "features": [...]
    },
    "stop_signs": {
      "type": "FeatureCollection",
      "features": [...]
    }
  }
}
```

---

#### 4. 获取犯罪事件（支持过滤）
```
GET /api/incidents/<neighborhood>
```

**查询参数（可选）：**
- `date_from`: 开始日期 (YYYY-MM-DD)
- `date_to`: 结束日期 (YYYY-MM-DD)
- `hour_from`: 开始小时 (0-23)
- `hour_to`: 结束小时 (0-23)

**示例：**
```
GET /api/incidents/Center%20City?date_from=2025-01-01&date_to=2025-12-31&hour_from=18&hour_to=23
```

**响应：**
```json
{
  "status": "success",
  "neighborhood": "Center City",
  "data": {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "geometry": {
          "type": "Point",
          "coordinates": [-75.18, 39.95]
        },
        "properties": {
          "text_general_code": "Robbery No Firearm",
          "hour": 22,
          "dispatch_date": "2025-08-29"
        }
      }
    ]
  }
}
```

---

#### 5. 获取街区统计
```
GET /api/stats/<neighborhood>
```

**响应：**
```json
{
  "status": "success",
  "data": {
    "neighborhood": "Center City",
    "traffic_lights_count": 141,
    "stop_signs_count": 12,
    "incidents_count": 5000,
    "facility_density": {
      "traffic_lights_per_km2": 56.4,
      "stop_signs_per_km2": 4.8
    },
    "incident_by_type": {
      "Robbery No Firearm": 1200,
      "Theft from Vehicle": 980,
      ...
    },
    "incident_by_hour": {
      "0": 150,
      "1": 120,
      ...
      "23": 180
    }
  }
}
```

---

#### 6. 获取全部街区对比
```
GET /api/comparison
```

**响应：** 返回所有街区的统计数据数组

---

## 🗂️ 文件结构

```
backend/
├── app.py                 # Flask应用主文件
├── config.py             # 配置文件
├── data_manager.py       # 数据加载与管理
├── requirements.txt      # 依赖清单
├── README.md             # 本文件
└── data/                 # 数据目录（GeoJSON、CSV）
    ├── traffic_lights/
    ├── stop_signs/
    └── incidents.csv
```

---

## 🔧 数据管理

### 数据来源
- **交通灯/停止标志**：来自 `philly_streetscape_project/*/outputs/` 目录下的GeoJSON文件
- **犯罪事件**：来自 `incidents/incidents.csv`

### 数据预处理
`DataManager` 类会在应用启动时：
1. 加载所有GeoJSON文件到内存
2. 加载犯罪事件CSV
3. 缓存数据以加速查询

### 扩展分析
可在 `spatial_analysis.py` 中添加更复杂的空间分析操作

---

## 🚀 部署

### 本地开发
```bash
export FLASK_ENV=development
python app.py
```

### 生产环境（示例：Heroku）
```bash
# 创建 Procfile
echo "web: python app.py" > Procfile

# 部署
heroku create your-app-name
git push heroku main
```

---

## 📝 环境变量

创建 `.env` 文件（可选）：
```
FLASK_ENV=development
FLASK_DEBUG=1
```

---

## 🐛 故障排除

### 找不到数据文件
确保项目目录结构正确：
```
streetview yolo3/
├── dashboard/backend/app.py
├── philly_streetscape_project/  ← 确保此目录存在
└── incidents/incidents.csv       ← 确保此文件存在
```

### GeoPandas 错误
```bash
# 重新安装依赖
pip install --upgrade geopandas shapely
```

### CORS 错误（前端调用失败）
检查 `config.py` 中的 `CORS_ORIGINS` 配置

---

## 📚 后续开发

- [ ] 添加空间邻近分析 (`spatial_analysis.py`)
- [ ] 实现缓冲区查询 API
- [ ] 添加热力图数据生成
- [ ] 数据库集成（PostGIS）
- [ ] 认证与授权

