"""
数据预处理脚本
在启动应用前运行此脚本，预处理所有数据并保存为JSON
这样前端只需要读取预处理好的结果，无需等待长时间的数据加载
"""

import geopandas as gpd
import pandas as pd
import json
import os
from config import Config

# 首先运行空间分析来获得正确的 incident 统计
# 但不在这里运行，因为那需要较长时间和大内存
# 用户应该先手动运行: python preprocess_incidents.py

def preprocess_all_data():
    """预处理所有数据并保存"""
    print("[INFO] Starting data preprocessing...")

    # 计算基础路径
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(backend_dir))
    base_data_path = os.path.join(project_root, "philly_streetscape_project")
    incidents_file = os.path.join(project_root, "incidents", "incidents.csv")
    output_dir = os.path.join(backend_dir, "processed_data")

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 加载空间分析结果（包含每个街区的 incident 统计）
    print("[INFO] Loading incident spatial analysis results...")
    incidents_stats_file = os.path.join(output_dir, "incidents_stats.json")
    incident_counts = {}
    incident_types = {}

    try:
        with open(incidents_stats_file, 'r') as f:
            incidents_stats = json.load(f)
            incident_counts = incidents_stats.get('incident_counts', {})
            incident_types = incidents_stats.get('incident_types', {})
        print(f"[OK] Loaded incident statistics for {len(incident_counts)} neighborhoods")
    except Exception as e:
        print(f"[WARN] Failed to load incidents_stats.json: {e}")
        print("[INFO] Please run: python preprocess_incidents.py first!")
        return False

    # 所有街区的数据处理
    neighborhoods_data = {}

    for neighborhood in Config.NEIGHBORHOODS:
        print(f"\n[INFO] Processing {neighborhood}...")

        # 加载地理数据
        tl_path = os.path.join(base_data_path, neighborhood, "outputs", "traffic_lights.geojson")
        ss_path = os.path.join(base_data_path, neighborhood, "outputs", "stop_signs.geojson")

        traffic_lights = gpd.read_file(tl_path) if os.path.exists(tl_path) else gpd.GeoDataFrame()
        stop_signs = gpd.read_file(ss_path) if os.path.exists(ss_path) else gpd.GeoDataFrame()

        print(f"  - Traffic Lights: {len(traffic_lights)}")
        print(f"  - Stop Signs: {len(stop_signs)}")

        # 获取该街区的 incidents 统计
        nb_incidents_count = incident_counts.get(neighborhood, 0)
        nb_incident_types = incident_types.get(neighborhood, {})

        print(f"  - Incidents: {nb_incidents_count}")

        # 计算统计数据
        stats = {
            'neighborhood': neighborhood,
            'traffic_lights_count': len(traffic_lights),
            'stop_signs_count': len(stop_signs),
            'incidents_count': nb_incidents_count,  # 使用空间分析结果
            'facility_density': {
                'traffic_lights_per_km2': round(len(traffic_lights) / 2.5, 2),
                'stop_signs_per_km2': round(len(stop_signs) / 2.5, 2)
            },
            'incident_by_type': nb_incident_types,  # 使用空间分析结果
            'incident_by_hour': {}  # 可以从完整数据中提取
        }

        # 保存街区数据
        neighborhood_data = {
            'neighborhood': neighborhood,
            'stats': stats,
            'geo_data': {
                'traffic_lights': json.loads(traffic_lights.to_json()),
                'stop_signs': json.loads(stop_signs.to_json())
            }
        }

        neighborhoods_data[neighborhood] = neighborhood_data

        # 保存单个街区文件
        neighborhood_file = os.path.join(output_dir, f"{neighborhood}.json")
        with open(neighborhood_file, 'w') as f:
            json.dump(neighborhood_data, f)
        print(f"[OK] Saved {neighborhood_file}")

    # 生成对比数据（所有街区汇总）
    comparison_data = [neighborhoods_data[nb]['stats'] for nb in Config.NEIGHBORHOODS]

    comparison_file = os.path.join(output_dir, "comparison.json")
    with open(comparison_file, 'w') as f:
        json.dump(comparison_data, f)
    print(f"\n[OK] Saved {comparison_file}")

    # 生成元数据
    total_incidents = sum(incident_counts.get(nb, 0) for nb in Config.NEIGHBORHOODS)
    metadata = {
        'neighborhoods': Config.NEIGHBORHOODS,
        'total_incidents': total_incidents,
        'total_traffic_lights': sum(neighborhoods_data[nb]['stats']['traffic_lights_count']
                                     for nb in Config.NEIGHBORHOODS),
        'total_stop_signs': sum(neighborhoods_data[nb]['stats']['stop_signs_count']
                               for nb in Config.NEIGHBORHOODS),
        'processed_at': pd.Timestamp.now().isoformat()
    }

    metadata_file = os.path.join(output_dir, "metadata.json")
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f)
    print(f"[OK] Saved {metadata_file}")

    print("\n" + "="*50)
    print("[SUCCESS] Data preprocessing completed!")
    print("="*50)
    print(f"\nOutput directory: {output_dir}")
    print(f"Files created:")
    print(f"  - metadata.json")
    print(f"  - comparison.json")
    for nb in Config.NEIGHBORHOODS:
        print(f"  - {nb}.json")

    return True


if __name__ == "__main__":
    success = preprocess_all_data()
    if not success:
        print("[ERROR] Data preprocessing failed!")
        exit(1)
