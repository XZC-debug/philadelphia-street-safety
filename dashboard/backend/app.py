from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from config import Config, config
from data_manager import data_manager

# 创建Flask应用
app = Flask(__name__)

# 加载配置
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[env])

# 启用CORS
CORS(app, origins=app.config['CORS_ORIGINS'])

# ========================
# 路由 - API 端点
# ========================

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'message': 'Philadelphia Streetscape Dashboard API is running'
    }), 200


@app.route('/api/neighborhoods', methods=['GET'])
def get_neighborhoods():
    """
    返回所有街区及其基础统计
    GET /api/neighborhoods
    """
    try:
        stats = data_manager.get_neighborhoods()
        return jsonify({
            'status': 'success',
            'data': stats
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/data/<neighborhood>', methods=['GET'])
def get_neighborhood_data(neighborhood):
    """
    返回某街区的地理数据（交通灯+停止标志）
    GET /api/data/Center City
    """
    try:
        data = data_manager.get_neighborhood_data(neighborhood)
        if data is None:
            return jsonify({
                'status': 'error',
                'message': f'Neighborhood {neighborhood} not found'
            }), 404

        return jsonify({
            'status': 'success',
            'neighborhood': neighborhood,
            'data': data
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/incidents/<neighborhood>', methods=['GET'])
def get_incidents(neighborhood):
    """
    返回某街区的犯罪事件统计（按小时）
    GET /api/incidents/Center City
    """
    try:
        stats = data_manager.get_statistics(neighborhood)
        if stats is None:
            return jsonify({
                'status': 'error',
                'message': f'Neighborhood {neighborhood} not found'
            }), 404

        return jsonify({
            'status': 'success',
            'neighborhood': neighborhood,
            'data': stats.get('incident_by_hour', {})
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/stats/<neighborhood>', methods=['GET'])
def get_stats(neighborhood):
    """
    返回街区的统计汇总（密度、事件分布等）
    GET /api/stats/Center City
    """
    try:
        stats = data_manager.get_statistics(neighborhood)
        return jsonify({
            'status': 'success',
            'data': stats
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/comparison', methods=['GET'])
def get_comparison():
    """
    返回所有街区的对比数据
    GET /api/comparison
    """
    try:
        comparison_data = data_manager.get_comparison()
        return jsonify({
            'status': 'success',
            'data': comparison_data
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """404 错误处理"""
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """500 错误处理"""
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500


if __name__ == '__main__':
    # 开发环境运行
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
