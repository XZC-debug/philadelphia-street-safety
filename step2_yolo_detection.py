import os
from pathlib import Path
import numpy as np
import pandas as pd
import cv2
import json
from tqdm import tqdm
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("Warning: ultralytics not installed. Install with: pip install ultralytics")

    print("Warning: geopandas not installed. GeoJSON output will be skipped.")

# ============================================================================
# 配置参数
# ============================================================================

YOLO_MODEL = "yolov8m.pt"
YOLO_CONFIDENCE_THRESHOLD = 0.5

PROJECT_DIR = Path('./philly_streetscape_project')

NEIGHBORHOODS = [
    'Center City',
    'KENSINGTON',
    'POINT_BREEZE',
    'UNIVERSITY_CITY',
]

# ============================================================================
# YOLO 检测器
# ============================================================================

class YOLODetector:
    def __init__(self, model_name=YOLO_MODEL, confidence_threshold=YOLO_CONFIDENCE_THRESHOLD):
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.available = False

        if YOLO_AVAILABLE:
            try:
                print(f"  Loading YOLO model: {model_name}")
                self.model = YOLO(model_name)
                self.available = True
                print(f"  Model loaded successfully")
            except Exception as e:
                print(f"  Failed to load YOLO: {e}")

    def detect(self, image_path):
        if not self.available:
            return {'traffic_lights': [], 'stop_signs': [],
                    'has_traffic_light': False, 'has_stop_sign': False}

        try:
            image = cv2.imread(str(image_path))
            if image is None:
                return {'traffic_lights': [], 'stop_signs': [],
                        'has_traffic_light': False, 'has_stop_sign': False}

            results = self.model(image, verbose=False)
            traffic_lights = []
            stop_signs = []

            for result in results:
                for box in result.boxes:
                    conf = float(box.conf)
                    if conf < self.confidence_threshold:
                        continue
                    class_name = result.names[int(box.cls)]
                    bbox = [float(x) for x in box.xyxy.tolist()[0]]

                    if 'traffic light' in class_name.lower():
                        traffic_lights.append({'confidence': conf, 'class': class_name, 'bbox': bbox})
                    elif 'stop' in class_name.lower():
                        stop_signs.append({'confidence': conf, 'class': class_name, 'bbox': bbox})

            return {
                'traffic_lights': traffic_lights,
                'stop_signs': stop_signs,
                'has_traffic_light': len(traffic_lights) > 0,
                'has_stop_sign': len(stop_signs) > 0,
            }
        except Exception:
            return {'traffic_lights': [], 'stop_signs': [],
                    'has_traffic_light': False, 'has_stop_sign': False}


# ============================================================================
# 主流程
# ============================================================================

print("=" * 70)
print("STEP 2: YOLO DETECTION — Per Neighborhood")
print("=" * 70)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 初始化模型（只加载一次）
yolo = YOLODetector()

all_summary = []

for neighborhood in NEIGHBORHOODS:
    nbr_dir = PROJECT_DIR / neighborhood
    outputs_dir = nbr_dir / 'outputs'
    images_dir = outputs_dir / 'images_15deg'
    log_csv = outputs_dir / 'download_log.csv'

    print("\n" + "=" * 70)
    print(f"Neighborhood: {neighborhood}")
    print("=" * 70)

    if not log_csv.exists():
        print(f"  download_log.csv not found, skipping.")
        continue

    log_df = pd.read_csv(log_csv)
    print(f"  Loaded {len(log_df)} records from download_log.csv")

    # 检查图片是否存在
    valid_rows = []
    for _, row in log_df.iterrows():
        img_path = images_dir / row['filename']
        if img_path.exists():
            valid_rows.append((row, img_path))

    print(f"  Found {len(valid_rows)} image files")

    if len(valid_rows) == 0:
        print(f"  No images found, skipping.")
        continue

    # ---- YOLO 检测 ----
    detection_results = []

    for row, img_path in tqdm(valid_rows, desc=f"  Detecting [{neighborhood}]"):
        det = yolo.detect(img_path)

        detection_results.append({
            'filename':         row['filename'],
            'point_id':         row['point_id'],
            'intersection_idx': row['intersection_idx'],
            'lat':              row['lat'],
            'lon':              row['lon'],
            'arm_direction':    row['arm_direction'],
            'heading':          row['heading'],
            'gsv_pano_id':      row.get('gsv_pano_id', ''),
            'gsv_date':         row.get('gsv_date', ''),
            'has_traffic_light': det['has_traffic_light'],
            'has_stop_sign':     det['has_stop_sign'],
            'num_traffic_lights': len(det['traffic_lights']),
            'num_stop_signs':     len(det['stop_signs']),
            'detections_json':   json.dumps({
                'traffic_lights': det['traffic_lights'],
                'stop_signs': det['stop_signs']
            }),
        })

    det_df = pd.DataFrame(detection_results)

    # ---- 保存 detection_log.csv ----
    det_log_path = outputs_dir / 'detection_log.csv'
    det_df.to_csv(det_log_path, index=False)
    print(f"\n  Saved detection_log.csv  ({len(det_df)} rows)")

    # ---- 生成 GeoJSON（纯 json 写入，不依赖 fiona/pyogrio）----
    def save_geojson(df, path):
        features = []
        for _, r in df.iterrows():
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [r['lon'], r['lat']]},
                "properties": {
                    "point_id":         r['point_id'],
                    "intersection_idx": int(r['intersection_idx']),
                    "arm_direction":    int(r['arm_direction']),
                    "heading":          int(r['heading']),
                    "gsv_pano_id":      r['gsv_pano_id'],
                    "gsv_date":         r['gsv_date'],
                    "num_traffic_lights": int(r['num_traffic_lights']),
                    "num_stop_signs":     int(r['num_stop_signs']),
                }
            })
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({"type": "FeatureCollection", "features": features}, f, ensure_ascii=False, indent=2)

    tl_df = det_df[det_df['has_traffic_light']].copy()
    if len(tl_df) > 0:
        save_geojson(tl_df, outputs_dir / 'traffic_lights.geojson')
        print(f"  Saved traffic_lights.geojson  ({len(tl_df)} points)")
    else:
        print(f"  No traffic lights detected in {neighborhood}")

    ss_df = det_df[det_df['has_stop_sign']].copy()
    if len(ss_df) > 0:
        save_geojson(ss_df, outputs_dir / 'stop_signs.geojson')
        print(f"  Saved stop_signs.geojson      ({len(ss_df)} points)")
    else:
        print(f"  No stop signs detected in {neighborhood}")

    # ---- 统计 ----
    n_total = len(det_df)
    n_tl    = int(det_df['has_traffic_light'].sum())
    n_ss    = int(det_df['has_stop_sign'].sum())
    print(f"\n  Summary: {n_total} images | {n_tl} with traffic light | {n_ss} with stop sign")

    all_summary.append({
        'neighborhood':       neighborhood,
        'total_images':       n_total,
        'images_with_tl':     n_tl,
        'images_with_ss':     n_ss,
        'total_tl_detections': int(det_df['num_traffic_lights'].sum()),
        'total_ss_detections': int(det_df['num_stop_signs'].sum()),
    })

# ============================================================================
# 跨街区汇总
# ============================================================================

print("\n" + "=" * 70)
print("OVERALL SUMMARY")
print("=" * 70)

if all_summary:
    summary_df = pd.DataFrame(all_summary)
    print(summary_df.to_string(index=False))
    summary_path = PROJECT_DIR / 'outputs' / 'detection_summary_all.csv'
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(summary_path, index=False)
    print(f"\nSaved overall summary to: {summary_path}")

print(f"\nFinished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
