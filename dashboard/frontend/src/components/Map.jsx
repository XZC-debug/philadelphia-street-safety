import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import '../styles/Map.css';

// 修复 Leaflet 默认图标问题
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const Map = ({ neighborhood, data }) => {
  const mapContainer = useRef(null);
  const map = useRef(null);
  const markersRef = useRef({ trafficLights: [], stopSigns: [] });

  // 初始化地图
  useEffect(() => {
    if (!mapContainer.current) return;
    if (map.current) return; // 防止重复初始化

    map.current = L.map(mapContainer.current).setView([39.95, -75.17], 12);

    // 添加 OpenStreetMap 图层
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(map.current);

    return () => {
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, []);

  // 当数据改变时更新地图标记
  useEffect(() => {
    if (!map.current || !data) return;

    // 清除旧的标记
    markersRef.current.trafficLights.forEach((marker) => marker.remove());
    markersRef.current.stopSigns.forEach((marker) => marker.remove());
    markersRef.current = { trafficLights: [], stopSigns: [] };

    // 添加交通灯标记
    if (data.traffic_lights && data.traffic_lights.features) {
      data.traffic_lights.features.forEach((feature) => {
        const { coordinates } = feature.geometry;
        const marker = L.circleMarker([coordinates[1], coordinates[0]], {
          radius: 6,
          fillColor: '#ff0000',
          color: '#ff0000',
          weight: 2,
          opacity: 0.7,
          fillOpacity: 0.7,
        })
          .bindPopup(`<b>Traffic Light</b><br/>ID: ${feature.properties?.point_id || 'N/A'}`)
          .addTo(map.current);

        markersRef.current.trafficLights.push(marker);
      });
    }

    // 添加停止标志标记
    if (data.stop_signs && data.stop_signs.features) {
      data.stop_signs.features.forEach((feature) => {
        const { coordinates } = feature.geometry;
        const marker = L.circleMarker([coordinates[1], coordinates[0]], {
          radius: 5,
          fillColor: '#ffaa00',
          color: '#ffaa00',
          weight: 2,
          opacity: 0.7,
          fillOpacity: 0.7,
        })
          .bindPopup(`<b>Stop Sign</b><br/>ID: ${feature.properties?.point_id || 'N/A'}`)
          .addTo(map.current);

        markersRef.current.stopSigns.push(marker);
      });
    }
  }, [data]);

  return (
    <div className="map-container">
      <div ref={mapContainer} className="map" />
      <div className="map-legend">
        <div className="legend-item">
          <div className="legend-color traffic-light"></div>
          <span>Traffic Light</span>
        </div>
        <div className="legend-item">
          <div className="legend-color stop-sign"></div>
          <span>Stop Sign</span>
        </div>
      </div>
      <div className="map-info">
        {neighborhood && <p>{neighborhood}</p>}
      </div>
    </div>
  );
};

export default Map;
