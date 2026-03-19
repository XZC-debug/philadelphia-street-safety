"""
简化的数据管理器 - 只从预处理的JSON文件加载数据
所有复杂的数据处理都在 preprocess_data.py 中完成
"""

import json
import os
from config import Config


class DataManager:
    """从预处理的JSON文件加载数据"""

    def __init__(self):
        self.neighborhoods = Config.NEIGHBORHOODS
        self.neighborhoods_data = {}
        self.comparison_data = []
        self.metadata = {}

        # 计算预处理数据目录
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        self.processed_data_dir = os.path.join(backend_dir, "processed_data")

        self._load_processed_data()

    def _load_processed_data(self):
        """加载预处理的JSON数据"""
        print("[INFO] Loading preprocessed data...")

        # 检查预处理目录是否存在
        if not os.path.exists(self.processed_data_dir):
            print(f"[ERROR] Processed data directory not found: {self.processed_data_dir}")
            print("[ERROR] Please run: python preprocess_data.py first!")
            raise FileNotFoundError("Run preprocess_data.py first")

        # 加载元数据
        metadata_file = os.path.join(self.processed_data_dir, "metadata.json")
        try:
            with open(metadata_file, 'r') as f:
                self.metadata = json.load(f)
            print(f"[OK] Loaded metadata: {self.metadata['total_incidents']} incidents")
        except Exception as e:
            print(f"[WARN] Failed to load metadata: {e}")

        # 加载每个街区的数据
        for neighborhood in self.neighborhoods:
            neighborhood_file = os.path.join(self.processed_data_dir, f"{neighborhood}.json")
            try:
                with open(neighborhood_file, 'r') as f:
                    self.neighborhoods_data[neighborhood] = json.load(f)
                print(f"[OK] Loaded {neighborhood}")
            except Exception as e:
                print(f"[ERROR] Failed to load {neighborhood}: {e}")

        # 加载对比数据
        comparison_file = os.path.join(self.processed_data_dir, "comparison.json")
        try:
            with open(comparison_file, 'r') as f:
                self.comparison_data = json.load(f)
            print(f"[OK] Loaded comparison data for {len(self.comparison_data)} neighborhoods")
        except Exception as e:
            print(f"[WARN] Failed to load comparison data: {e}")

    def get_neighborhoods(self):
        """返回所有街区列表及其统计信息"""
        return [data['stats'] for data in self.neighborhoods_data.values()]

    def get_neighborhood_data(self, neighborhood):
        """返回某街区的地理数据（交通灯+停止标志）"""
        if neighborhood not in self.neighborhoods_data:
            return None

        return self.neighborhoods_data[neighborhood]['geo_data']

    def get_statistics(self, neighborhood):
        """返回街区的统计汇总"""
        if neighborhood not in self.neighborhoods_data:
            return None

        return self.neighborhoods_data[neighborhood]['stats']

    def get_comparison(self):
        """返回所有街区的对比数据"""
        return self.comparison_data


# 全局数据管理器实例
data_manager = DataManager()
