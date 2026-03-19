/**
 * Static Data Service
 * 从GitHub Pages直接加载预处理的JSON数据，无需后端API
 */

const DATA_BASE_URL = '/philadelphia-street-safety/data';

// 从本地 /data 文件夹读取数据
const loadJSON = async (filename) => {
  try {
    const response = await fetch(`${DATA_BASE_URL}/${filename}`);
    if (!response.ok) {
      throw new Error(`Failed to load ${filename}: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Error loading ${filename}:`, error);
    throw error;
  }
};

export const staticDataService = {
  // 获取所有街区的统计信息
  getNeighborhoods: async () => {
    try {
      const comparison = await loadJSON('comparison.json');
      return {
        status: 'success',
        data: comparison
      };
    } catch (error) {
      return {
        status: 'error',
        message: error.message
      };
    }
  },

  // 获取特定街区的地理数据
  getNeighborhoodData: async (neighborhood) => {
    try {
      const data = await loadJSON(`${neighborhood}.json`);
      return {
        status: 'success',
        data: data.geo_data,
        neighborhood
      };
    } catch (error) {
      return {
        status: 'error',
        message: error.message
      };
    }
  },

  // 获取街区统计信息
  getStats: async (neighborhood) => {
    try {
      const data = await loadJSON(`${neighborhood}.json`);
      return {
        status: 'success',
        data: data.stats
      };
    } catch (error) {
      return {
        status: 'error',
        message: error.message
      };
    }
  },

  // 获取所有街区对比数据
  getComparison: async () => {
    try {
      const data = await loadJSON('comparison.json');
      return {
        status: 'success',
        data
      };
    } catch (error) {
      return {
        status: 'error',
        message: error.message
      };
    }
  }
};

export default staticDataService;
