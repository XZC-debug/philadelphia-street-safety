# 费城街景交通设施与安全分析 - 网页应用架构

## 项目整体架构

```
philly-streetscape-web/
├── backend/
│   ├── app.py (Flask主应用)
│   ├── config.py
│   ├── requirements.txt
│   ├── spatial_analysis.py (空间分析模块)
│   ├── data_processor.py (数据预处理)
│   └── data/
│       ├── traffic_lights/ (geojson)
│       ├── stop_signs/ (geojson)
│       └── incidents.csv
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Map.jsx (交互式地图)
│   │   │   ├── StatsPanel.jsx (统计面板)
│   │   │   ├── Timeline.jsx (时间筛选)
│   │   │   └── ComparisonChart.jsx (街区对比)
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx (主页面)
│   │   │   └── Analysis.jsx (分析页面)
│   │   ├── utils/
│   │   │   └── api.js (API调用)
│   │   └── App.jsx
│   └── package.json
└── README.md
```

---

## 后端设计（Flask）

### 核心API端点

```
GET  /api/neighborhoods
     返回：四个街区的元数据

GET  /api/data/<neighborhood>
     返回：该街区的traffic lights + stop signs (GeoJSON)

GET  /api/incidents/<neighborhood>?date_from=&date_to=&hour_from=&hour_to=
     返回：筛选后的犯罪事件(GeoJSON)

GET  /api/stats/<neighborhood>
     返回：
     {
       "facility_density": {...},
       "incident_count": {...},
       "incident_by_type": {...},
       "incident_by_hour": {...}
     }

POST /api/spatial-analysis
     请求体：
     {
       "neighborhood": "Center City",
       "buffer_radius": 100  // 单位：米
     }
     返回：在缓冲区内的设施和事件关联统计
```

### 关键模块

**spatial_analysis.py** - 空间分析引擎
- 计算设施密度热力图
- 缓冲区分析
- 点-事件邻近性统计

**data_processor.py** - 数据预处理
- 统一坐标系
- 时间格式标准化
- GeoJSON生成

---

## 前端设计（React + Mapbox）

### 页面布局

```
Dashboard
├── 顶部导航栏
│   ├── 街区选择下拉菜单
│   ├── 时间范围筛选
│   └── 图层切换按钮
│
├── 左侧面板（30%宽）
│   ├── 街区基础统计
│   ├── 设施分布统计表
│   └── 事件类型分布（饼图）
│
├── 中间地图（70%宽）
│   ├── Mapbox GL JS
│   ├── 图层：
│   │   - 红绿灯标记（红色）
│   │   - 停止标志标记（黄色）
│   │   - 犯罪事件热力图（红→绿）
│   │   - 街区边界（轮廓线）
│   └── 可交互的聚类和缩放
│
└── 底部时间轴
    └── 可拖动滑块按小时过滤事件
```

### 关键组件

**Map.jsx**
- 加载Mapbox
- 渲染traffic lights / stop signs图层
- 热力图层动态更新
- 点击标记显示详情弹窗

**StatsPanel.jsx**
- 显示街区汇总统计
- 更新响应数据变化

**TimelineSlider.jsx**
- 按小时/日期范围过滤
- 实时更新地图

**ComparisonChart.jsx**
- 四个街区的并排对比
- 柱状图展示设施密度、事件数量

---

## 关键分析功能

### 1. 热力图生成
```python
# 后端生成热力网格数据
# 网格大小：50m x 50m
# 值：该网格内的犯罪事件密度
# 返回给前端用Mapbox heatmap图层展示
```

### 2. 空间邻近分析
```python
# 对每个犯罪事件，查询周围200m内的设施
# 生成统计：
# - 高设施密度区域的低犯罪率
# - 低设施密度区域的高犯罪率
```

### 3. 时间模式分析
```python
# 按小时统计犯罪
# 与交通灯照明时间(如夜间)相关性
# 可生成小时-事件密度的热力矩阵
```

---

## 数据流

```
1. 用户在网页选择街区 + 时间范围
   ↓
2. React组件调用API /api/data/<neighborhood>?...
   ↓
3. Flask后端查询CSV/GeoJSON，执行空间分析
   ↓
4. 返回JSON: {traffic_lights: [...], stop_signs: [...], incidents: [...]}
   ↓
5. Mapbox渲染多个图层
   ↓
6. 同时更新右侧统计面板（图表）
```

---

## 部署方案

### 开发环境
```bash
# 后端
cd backend
pip install -r requirements.txt
python app.py  # 运行在 localhost:5000

# 前端
cd frontend
npm install
npm start  # 运行在 localhost:3000
```

### 生产环境（推荐）
- 后端：Heroku / Railway (Flask)
- 前端：Vercel / Netlify (React)
- 地图API Key: Mapbox (免费tier支持)

---

## 实现优先级

**Phase 1（MVP - 2-3天）**
- ✓ Flask API 基础框架
- ✓ 数据加载与处理
- ✓ 简单地图展示（交通灯+停止标志标记）
- ✓ 基础统计表格

**Phase 2（核心功能 - 2-3天）**
- ✓ 热力图集成
- ✓ 时间筛选器
- ✓ 街区对比图表
- ✓ 地图交互优化

**Phase 3（增强 - 可选）**
- 空间邻近分析的可视化
- 事件详情弹窗
- 导出报告功能
- 响应式设计优化

---

## 技术栈总结

| 组件 | 选择 | 原因 |
|------|------|------|
| **后端** | Flask + GeoPandas | 轻量级、Python空间库强大 |
| **前端** | React + TypeScript | 组件化、类型安全、社区大 |
| **地图** | Mapbox GL JS | 高性能、热力图支持好 |
| **数据库** | GeoJSON文件 | 无需DB即可启动，后期可升级PostGIS |
| **图表** | Recharts / Chart.js | 响应式、React友好 |
| **部署** | Vercel + Railway | 免费、自动部署、冷启动快 |

