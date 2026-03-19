import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import '../styles/ComparisonChart.css';

const ComparisonChart = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="comparison-chart">
        <p>No comparison data available</p>
      </div>
    );
  }

  // 准备数据用于Recharts
  const chartData = data.map((item) => ({
    name: item.neighborhood,
    'Traffic Lights': item.traffic_lights_count,
    'Stop Signs': item.stop_signs_count,
    'Incidents': Math.min(item.incidents_count / 100, 500), // 缩放以便可视化
  }));

  return (
    <div className="comparison-chart">
      <h3>Neighborhood Comparison</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 60 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="name"
            angle={-45}
            textAnchor="end"
            height={100}
            tick={{ fontSize: 12 }}
          />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#f9f9f9',
              border: '1px solid #ccc',
              borderRadius: '4px',
            }}
          />
          <Legend />
          <Bar dataKey="Traffic Lights" fill="#ff0000" />
          <Bar dataKey="Stop Signs" fill="#ffaa00" />
          <Bar dataKey="Incidents" fill="#4facfe" />
        </BarChart>
      </ResponsiveContainer>
      <p className="chart-note">* Incidents count scaled for visualization</p>
    </div>
  );
};

export default ComparisonChart;
