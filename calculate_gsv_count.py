from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import transform
import pyproj
from tqdm import tqdm
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

# ============================================================================
# 配置参数
# ============================================================================

# 数据路径
STREET_CENTERLINE_SHP_PATH = "Street_Centerline/Street_Centerline.shp"

# 采样参数 - 只在交叉口采样
INTERSECTION_BUFFER_METERS = 30  # 交叉口周围缓冲区 (米)
SAMPLE_DISTANCE_FROM_INTERSECTION = 20  # 距离交叉点多远采样 (米)

# 图片采样参数
BEARINGS = [0, 90, 180, 270]  # 4个方向，每个路口4张图，相机朝向路口
IMAGE_SIZE = "640x640"
IMAGE_FOV = 15  # 视野角度（度），窄角以减少畸变

# 输出目录
PROJECT_DIR = Path('./philly_streetscape_project')
OUTPUT_DIR = PROJECT_DIR / 'outputs'

# ============================================================================
# 开始执行
# ============================================================================

print("="*70)
print("GSV IMAGE DOWNLOAD ESTIMATION")
print("估算需要下载的街景图片数量")
print("="*70)
print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 创建输出目录
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
print(f"\n✓ Output directory: {OUTPUT_DIR.absolute()}")

# ============================================================================
# SECTION 1: 识别交叉口并生成采样点（仅计算，不下载）
# ============================================================================

print("\n" + "="*70)
print("STEP 1: Detecting intersections and generating sampling points")
print("识别交叉口并生成采样点")
print("="*70)

def detect_intersections_from_roads(roads_path, buffer_meters=30):
    """
    从路网数据检测交叉口
    
    Parameters:
        roads_path: 路网 shapefile 路径
        buffer_meters: 交叉口判定的缓冲区大小
    
    Returns:
        GeoDataFrame: 包含交叉口位置和相关信息
    """
    print(f"\n  Loading roads from: {roads_path}")
    
    # 读取路网
    roads_gdf = gpd.read_file(roads_path)
    print(f"  ✓ Loaded {len(roads_gdf)} road segments")
    print(f"  CRS: {roads_gdf.crs}")
    
    # 确保是 WGS84 坐标系
    if roads_gdf.crs is None:
        print("  ⚠ No CRS found, assuming EPSG:4326")
        roads_gdf = roads_gdf.set_crs("EPSG:4326")
    elif roads_gdf.crs.to_epsg() != 4326:
        print(f"  Converting from {roads_gdf.crs} to EPSG:4326")
        roads_gdf = roads_gdf.to_crs("EPSG:4326")
    
    # 提取所有端点
    endpoints = []
    for idx, row in roads_gdf.iterrows():
        geom = row.geometry
        if geom and not geom.is_empty:
            if geom.geom_type == 'MultiLineString':
                lines = list(geom.geoms)
            else:
                lines = [geom]
            
            for line in lines:
                coords = list(line.coords)
                if len(coords) >= 2:
                    endpoints.append(Point(coords[0]))
                    endpoints.append(Point(coords[-1]))
    
    # 转换为 GeoDataFrame
    endpoints_gdf = gpd.GeoDataFrame(
        geometry=endpoints,
        crs="EPSG:4326"
    )
    
    # 转换到投影坐标系进行聚类 (Pennsylvania State Plane South)
    endpoints_projected = endpoints_gdf.to_crs("EPSG:2272")
    
    # 使用 STRtree 空间索引 + 缓冲区聚类找交叉口
    intersections = []
    processed = set()

    print(f"\n  Detecting intersections (buffer={buffer_meters}m)...")

    # 提取点列表并建立空间索引（只建一次，O(n log n)）
    from shapely.strtree import STRtree
    points_list = list(endpoints_projected.geometry)
    tree = STRtree(points_list)

    for i, geom1 in enumerate(tqdm(points_list, desc="  Clustering endpoints")):
        if i in processed:
            continue

        # 创建缓冲区，用索引快速找候选点（O(log n)）
        buffer_geom = geom1.buffer(buffer_meters)
        candidate_indices = tree.query(buffer_geom)

        # 精确过滤：确认在缓冲区内
        cluster_indices = [j for j in candidate_indices if buffer_geom.contains(points_list[j])]
        cluster_points = [points_list[j] for j in cluster_indices]

        if len(cluster_indices) >= 3:  # 至少3条道路交汇 = 交叉口
            processed.update(cluster_indices)

            # 计算簇的质心
            centroid_x = np.mean([p.x for p in cluster_points])
            centroid_y = np.mean([p.y for p in cluster_points])
            centroid = Point(centroid_x, centroid_y)

            # 转回 WGS84
            centroid_wgs84 = gpd.GeoSeries([centroid], crs="EPSG:2272").to_crs("EPSG:4326")[0]

            intersections.append({
                'geometry': centroid_wgs84,
                'num_roads': len(cluster_indices),
                'lat': centroid_wgs84.y,
                'lon': centroid_wgs84.x
            })
    
    intersections_gdf = gpd.GeoDataFrame(intersections, crs="EPSG:4326")
    
    print(f"\n  ✓ Detected {len(intersections_gdf)} intersections")
    print(f"    Mean roads per intersection: {intersections_gdf['num_roads'].mean():.1f}")
    print(f"    Min roads: {intersections_gdf['num_roads'].min()}, Max: {intersections_gdf['num_roads'].max()}")
    
    return intersections_gdf


def generate_sampling_points_at_intersections(intersections_gdf, distance_meters=20, bearings=[0, 90]):
    """
    在每个交叉口周围的指定距离处生成采样点
    
    Parameters:
        intersections_gdf: 交叉口 GeoDataFrame
        distance_meters: 离交叉点的距离
        bearings: 方向列表 (0=北, 90=东, 180=南, 270=西)
    
    Returns:
        list: [{'point_id': ..., 'lat': ..., 'lon': ..., 'bearing': ...}, ...]
    """
    print(f"\n  Generating sampling points around intersections...")
    print(f"  Distance from intersection: {distance_meters}m")
    print(f"  Directions (bearings): {bearings}")
    
    # 创建投影转换器 (用于计算距离)
    proj_to_meters = pyproj.Transformer.from_crs(
        "EPSG:4326", "EPSG:2272", always_xy=True
    ).transform
    proj_to_wgs84 = pyproj.Transformer.from_crs(
        "EPSG:2272", "EPSG:4326", always_xy=True
    ).transform
    
    sampling_points = []
    point_counter = 0
    
    for idx, intersection in tqdm(intersections_gdf.iterrows(), total=len(intersections_gdf), 
                                  desc="  Processing intersections"):
        lat_center = intersection['lat']
        lon_center = intersection['lon']
        
        for bearing in bearings:
            # 计算方向的单位向量 (在米坐标系中)
            # bearing: 0=北(+y), 90=东(+x), 180=南(-y), 270=西(-x)
            bearing_rad = np.radians(bearing)
            dx = distance_meters * np.sin(bearing_rad)  # 东西方向
            dy = distance_meters * np.cos(bearing_rad)  # 南北方向
            
            # 投影中心点到米坐标系
            center_meters_point = Point(lon_center, lat_center)
            center_meters = transform(proj_to_meters, center_meters_point)
            
            # 计算新位置 (米坐标系)
            new_x = center_meters.x + dx
            new_y = center_meters.y + dy
            new_point_meters = Point(new_x, new_y)
            
            # 转回 WGS84
            new_point_wgs84 = transform(proj_to_wgs84, new_point_meters)
            
            lat, lon = new_point_wgs84.y, new_point_wgs84.x
            
            # 检查坐标合理性 (费城范围)
            if 39.8 < lat < 40.2 and -75.4 < lon < -74.9:
                # 相机朝向路口：放置方向的反方向
                camera_bearing = (bearing + 180) % 360
                sampling_points.append({
                    'point_id': f"pt_{point_counter:06d}",
                    'lat': lat,
                    'lon': lon,
                    'bearing': camera_bearing,  # 朝向路口中心
                    'arm_direction': bearing,    # 从路口出发的方向（调试用）
                    'intersection_idx': idx
                })
                point_counter += 1
    
    print(f"\n  ✓ Generated {len(sampling_points)} sampling points")
    
    return sampling_points


# 检查路网文件是否存在
if not Path(STREET_CENTERLINE_SHP_PATH).exists():
    print(f"\n  ❌ ERROR: Street Centerline file not found: {STREET_CENTERLINE_SHP_PATH}")
    print("  Expected files: Street_Centerline/Street_Centerline.shp, Street_Centerline/Street_Centerline.shx, Street_Centerline/Street_Centerline.dbf")
    print("  Download from: https://www.opendataphilly.org/datasets/street-centerlines/")
    
    intersections_gdf = None
    sampling_points = []
else:
    intersections_gdf = detect_intersections_from_roads(STREET_CENTERLINE_SHP_PATH, INTERSECTION_BUFFER_METERS)
    sampling_points = generate_sampling_points_at_intersections(
        intersections_gdf,
        distance_meters=SAMPLE_DISTANCE_FROM_INTERSECTION,
        bearings=BEARINGS
    )

# ============================================================================
# SECTION 2: 计算估算数据 (不进行实际下载)
# ============================================================================

print("\n" + "="*70)
print("STEP 2: Estimating GSV Image Download Requirements")
print("估算街景图片下载需求")
print("="*70)

if len(sampling_points) == 0:
    print("\n  ⚠️  No sampling points generated. Unable to estimate.")
    
    print("\n" + "="*70)
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
else:
    # 基本统计
    num_intersections = len(intersections_gdf)
    num_bearings = len(BEARINGS)
    total_images = num_intersections * num_bearings  # 每个路口 × 4个方向

    print(f"\n  📊 ESTIMATION SUMMARY:")
    print(f"  ─" * 35)
    print(f"  Total intersections detected:  {num_intersections:>8,}")
    print(f"  Images per intersection:       {num_bearings:>8}  (4 directions × FOV {IMAGE_FOV}°)")
    print(f"  ─" * 35)
    print(f"  Total images to download:      {total_images:>8,}  ({num_intersections:,} × {num_bearings})")
    print(f"  Free quota remaining:          {'10,000':>8}  (Google Street View)")
    print(f"  Shortfall:                     {max(0, total_images - 10000):>8,}  images over quota")
    print(f"  Image size: {IMAGE_SIZE}, FOV: {IMAGE_FOV}°")
    print(f"  Estimated size per image: ~150-300 KB")
    
    # 估算存储空间
    estimated_min_size_gb = (total_images * 150) / (1024 * 1024)
    estimated_max_size_gb = (total_images * 300) / (1024 * 1024)
    
    print(f"\n  💾 STORAGE ESTIMATION:")
    print(f"  ─" * 35)
    print(f"  Estimated disk space (min): {estimated_min_size_gb:.2f} GB")
    print(f"  Estimated disk space (max): {estimated_max_size_gb:.2f} GB")
    
    # 估算下载时间（基于API限速 0.1秒/请求）
    # 加上metadata check的时间
    time_per_request = 0.2  # 秒 (check_availability + download)
    estimated_time_seconds = total_images * time_per_request
    estimated_time_hours = estimated_time_seconds / 3600
    estimated_time_minutes = estimated_time_seconds / 60
    
    print(f"\n  ⏱️  TIME ESTIMATION:")
    print(f"  ─" * 35)
    print(f"  Estimated download time: {estimated_time_hours:.2f} hours ({estimated_time_minutes:.0f} minutes)")
    print(f"  (Assuming 0.2s per request with API rate limiting)")
    
    # 按bearing的分布
    print(f"\n  📍 SAMPLING DISTRIBUTION BY BEARING:")
    print(f"  ─" * 35)
    bearing_counts = {}
    for point in sampling_points:
        bearing = point['bearing']
        bearing_counts[bearing] = bearing_counts.get(bearing, 0) + 1
    
    for bearing in sorted(bearing_counts.keys()):
        count = bearing_counts[bearing]
        percentage = (count / total_images) * 100
        print(f"  Bearing {bearing:3d}°: {count:6d} images ({percentage:5.1f}%)")
    
    # 保存估算结果到CSV
    estimation_summary = {
        'Metric': [
            'Total Intersections',
            'Images per Intersection (directions)',
            'Total Images to Download',
            f'Image Size (pixels)',
            f'Image FOV (degrees)',
            'Estimated Min Storage (GB)',
            'Estimated Max Storage (GB)',
            'Estimated Download Time (hours)',
            'Estimated Download Time (minutes)',
            'Time per Request (seconds)'
        ],
        'Value': [
            num_intersections,
            num_bearings,
            total_images,
            IMAGE_SIZE,
            IMAGE_FOV,
            f'{estimated_min_size_gb:.2f}',
            f'{estimated_max_size_gb:.2f}',
            f'{estimated_time_hours:.2f}',
            f'{estimated_time_minutes:.0f}',
            time_per_request
        ]
    }
    
    summary_df = pd.DataFrame(estimation_summary)
    summary_path = OUTPUT_DIR / 'gsv_download_estimation.csv'
    summary_df.to_csv(summary_path, index=False)
    print(f"\n  ✓ Estimation summary saved to: {summary_path}")
    
    # 保存采样点信息
    sampling_points_df = pd.DataFrame(sampling_points)
    sampling_points_path = OUTPUT_DIR / 'sampling_points.csv'
    sampling_points_df.to_csv(sampling_points_path, index=False)
    print(f"  ✓ Sampling points saved to: {sampling_points_path}")
    
    # 保存交叉口信息
    intersections_output = OUTPUT_DIR / 'detected_intersections.geojson'
    intersections_gdf.to_file(intersections_output, driver='GeoJSON')
    print(f"  ✓ Intersections saved to: {intersections_output}")
    
    print("\n" + "="*70)
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    print(f"\n✓ Estimation complete!")
    print(f"  Files saved to: {OUTPUT_DIR.absolute()}")
    print(f"\n  To proceed with actual download, use: step1_download_gsv.py")

