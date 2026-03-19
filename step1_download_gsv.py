import os
import sys
import requests
import time
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

# ⚠️ 在这里填入你的 Google Street View API Key
GSV_API_KEY = "AIzaSyA5dK4SMNTHecNzfpSHt9wQcq2vTy2jvTo"

# 数据路径
ROADS_SHP_PATH = "roads/roads.shp"

# 采样参数 - 只在交叉口采样
INTERSECTION_BUFFER_METERS = 30  # 交叉口周围缓冲区 (米)
SAMPLE_DISTANCE_FROM_INTERSECTION = 20  # 距离交叉点多远采样 (米)

# 图片采样参数
IMAGE_SIZE = "640x480"
BEARINGS = [0, 90]  # 只需要2个垂直方向

# 输出目录
PROJECT_DIR = Path('./philly_streetscape_project')
DATA_DIR = PROJECT_DIR / 'data'
GSV_DIR = DATA_DIR / 'gsv_images'
OUTPUT_DIR = PROJECT_DIR / 'outputs'
FIGURES_DIR = PROJECT_DIR / 'figures'

# ============================================================================
# 开始执行
# ============================================================================

print("="*70)
print("STEP 1: STREETSCAPE IMAGE DOWNLOAD")
print("Google Street View Image Downloader")
print("="*70)
print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 创建目录
for d in [PROJECT_DIR, DATA_DIR, GSV_DIR, OUTPUT_DIR, FIGURES_DIR]:
    d.mkdir(parents=True, exist_ok=True)
print(f"\n✓ Project directory: {PROJECT_DIR.absolute()}")

# ============================================================================
# SECTION 1: 识别交叉口并生成采样点
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
    
    # 使用缓冲区聚类找交叉口
    intersections = []
    processed = set()
    
    print(f"\n  Detecting intersections (buffer={buffer_meters}m)...")
    
    for i, (idx1, point1) in enumerate(endpoints_projected.iterrows()):
        if i in processed:
            continue
        
        geom1 = point1.geometry
        # 创建缓冲区
        buffer_geom = geom1.buffer(buffer_meters)
        
        # 找所有在缓冲区内的点
        cluster_indices = []
        cluster_points = []
        
        for j, (idx2, point2) in enumerate(endpoints_projected.iterrows()):
            if buffer_geom.contains(point2.geometry):
                cluster_indices.append(j)
                cluster_points.append(point2.geometry)
        
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
                sampling_points.append({
                    'point_id': f"pt_{point_counter:06d}",
                    'lat': lat,
                    'lon': lon,
                    'bearing': bearing,
                    'intersection_idx': idx
                })
                point_counter += 1
    
    print(f"\n  ✓ Generated {len(sampling_points)} sampling points")
    
    return sampling_points


# 检查路网文件是否存在
if not Path(ROADS_SHP_PATH).exists():
    print(f"\n  ❌ ERROR: Roads file not found: {ROADS_SHP_PATH}")
    print("  Expected files: roads/roads.shp, roads/roads.shx, roads/roads.dbf")
    print("  Download from: https://www.opendataphilly.org/datasets/street-centerlines/")
    
    intersections_gdf = None
    sampling_points = []
else:
    intersections_gdf = detect_intersections_from_roads(ROADS_SHP_PATH, INTERSECTION_BUFFER_METERS)
    sampling_points = generate_sampling_points_at_intersections(
        intersections_gdf,
        distance_meters=SAMPLE_DISTANCE_FROM_INTERSECTION,
        bearings=BEARINGS
    )

# ============================================================================
# SECTION 2: Google Street View 图片下载
# ============================================================================

print("\n" + "="*70)
print("STEP 2: Downloading Google Street View images")
print("下载谷歌街景图片")
print("="*70)

class GoogleStreetViewDownloader:
    """
    Google Street View 图片下载器
    """
    
    def __init__(self, api_key, output_dir, image_size="640x480"):
        self.api_key = api_key
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.image_size = image_size
        
        self.base_url = "https://maps.googleapis.com/maps/api/streetview"
        self.metadata_url = f"{self.base_url}/metadata"
        
        self.collection_log = []
        self.failed_points = []
        
    def check_availability(self, lat, lon):
        """检查该位置是否有街景图像"""
        params = {
            'location': f'{lat},{lon}',
            'key': self.api_key
        }
        
        try:
            response = requests.get(self.metadata_url, params=params, timeout=10)
            data = response.json()
            
            if data.get('status') == 'OK':
                return data
            return None
        except Exception as e:
            return None
    
    def download_image(self, lat, lon, heading, pitch=0, fov=90):
        """下载单张街景图片"""
        params = {
            'size': self.image_size,
            'location': f'{lat},{lon}',
            'heading': heading,
            'pitch': pitch,
            'fov': fov,
            'key': self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            if response.status_code == 200 and len(response.content) > 1000:
                return response.content
            return None
        except Exception as e:
            return None
    
    def download_point(self, point_info):
        """
        下载一个采样点的图片
        
        Parameters:
            point_info: {'point_id': ..., 'lat': ..., 'lon': ..., 'bearing': ...}
        """
        point_id = point_info['point_id']
        lat = point_info['lat']
        lon = point_info['lon']
        bearing = point_info['bearing']
        
        # 先检查是否有街景
        metadata = self.check_availability(lat, lon)
        if not metadata:
            self.failed_points.append({
                'point_id': point_id,
                'lat': lat,
                'lon': lon,
                'bearing': bearing,
                'reason': 'no_coverage'
            })
            return None
        
        # 下载图片
        image_content = self.download_image(lat, lon, bearing)
        
        if not image_content:
            self.failed_points.append({
                'point_id': point_id,
                'lat': lat,
                'lon': lon,
                'bearing': bearing,
                'reason': 'download_failed'
            })
            return None
        
        # 保存图片
        filename = f"{point_id}_{bearing}.jpg"
        filepath = self.output_dir / filename
        
        with open(filepath, 'wb') as f:
            f.write(image_content)
        
        # 记录日志
        log_entry = {
            'image_id': f"{point_id}_{bearing}",
            'point_id': point_id,
            'lat': lat,
            'lon': lon,
            'bearing': bearing,
            'filepath': str(filepath),
            'pano_id': metadata.get('pano_id', ''),
            'capture_date': metadata.get('date', ''),
            'status': 'success'
        }
        self.collection_log.append(log_entry)
        
        # API 限速 (避免请求过快)
        time.sleep(0.1)
        
        return log_entry
    
    def download_batch(self, sampling_points, max_points=None, save_interval=50):
        """
        批量下载街景图片
        
        Parameters:
            sampling_points: list of dicts
            max_points: 最大下载点数 (None = 全部)
            save_interval: 每隔多少个点保存一次日志
        """
        if max_points:
            sampling_points = sampling_points[:max_points]
        
        total_points = len(sampling_points)
        print(f"\n  Starting download of {total_points} points...")
        print(f"  Expected total images: {total_points}")
        
        success_count = 0
        
        for i, point_info in enumerate(tqdm(sampling_points, desc="  Downloading")):
            log_entry = self.download_point(point_info)
            
            if log_entry:
                success_count += 1
            
            # 定期保存日志
            if (i + 1) % save_interval == 0:
                self.save_log()
        
        # 最终保存
        self.save_log()
        
        print(f"\n  ✓ Download complete!")
        print(f"    Successful downloads: {success_count}/{total_points}")
        print(f"    Failed points: {len(self.failed_points)}")
        
        return self.collection_log
    
    def save_log(self, log_filename='gsv_collection_log.csv', failed_filename='gsv_failed_points.csv'):
        """保存采集日志"""
        if self.collection_log:
            log_df = pd.DataFrame(self.collection_log)
            log_path = DATA_DIR / log_filename
            log_df.to_csv(log_path, index=False)
        
        if self.failed_points:
            failed_df = pd.DataFrame(self.failed_points)
            failed_path = DATA_DIR / failed_filename
            failed_df.to_csv(failed_path, index=False)


# 检查 API Key
if GSV_API_KEY == "YOUR_API_KEY_HERE":
    print("\n  ⚠️  WARNING: Please set your Google Street View API Key!")
    print("  Edit line 23 and replace with your actual API key.")
    print("\n  To get an API key:")
    print("  1. Go to https://console.cloud.google.com/")
    print("  2. Create a project and enable Street View Static API")
    print("  3. Create credentials (API Key)")
    print("  4. Copy the key and paste it in this script")
    
    print("\n  Skipping GSV download for now...")
    gsv_log_df = None

elif len(sampling_points) == 0:
    print("\n  ⚠️  No sampling points generated. Skipping GSV download.")
    gsv_log_df = None

else:
    # 初始化下载器
    downloader = GoogleStreetViewDownloader(
        api_key=GSV_API_KEY,
        output_dir=GSV_DIR,
        image_size=IMAGE_SIZE
    )
    
    # 开始下载
    # 可以设置 max_points 来限制下载数量进行测试
    # 例如: max_points=10 只下载前10个点
    collection_log = downloader.download_batch(
        sampling_points,
        max_points=None,  # 设置为 None 下载全部，或设置数字限制
        save_interval=50
    )
    
    gsv_log_df = pd.DataFrame(collection_log) if collection_log else None
    
    if gsv_log_df is not None:
        print(f"\n  ✓ GSV collection log saved to: {DATA_DIR / 'gsv_collection_log.csv'}")

# ============================================================================
# SECTION 3: 完成
# ============================================================================

print("\n" + "="*70)
print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70)

if gsv_log_df is not None and len(gsv_log_df) > 0:
    print(f"\n✓ Download successful!")
    print(f"  Total images: {len(gsv_log_df)}")
    print(f"  Location: {GSV_DIR.absolute()}")
    print(f"  Log file: {DATA_DIR / 'gsv_collection_log.csv'}")
    print(f"\n  Next step: Run step2_yolo_detection.py to detect traffic signs")
