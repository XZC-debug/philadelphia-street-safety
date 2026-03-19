import React, { useEffect, useState } from 'react';
import Map from '../components/Map';
import StatsPanel from '../components/StatsPanel';
import ComparisonChart from '../components/ComparisonChart';
import NeighborhoodSelector from '../components/NeighborhoodSelector';
import { staticDataService } from '../utils/staticDataService';
import '../styles/Dashboard.css';

const Dashboard = () => {
  const [neighborhoods, setNeighborhoods] = useState([]);
  const [selectedNeighborhood, setSelectedNeighborhood] = useState('Center City');
  const [data, setData] = useState(null);
  const [stats, setStats] = useState(null);
  const [comparisonData, setComparisonData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 加载街区列表
  useEffect(() => {
    const loadNeighborhoods = async () => {
      try {
        const response = await staticDataService.getNeighborhoods();
        if (response.status === 'success') {
          // 返回的是 stats 对象数组，每个对象有 'neighborhood' 属性
          const names = response.data.map((item) => item.neighborhood || item.name);
          setNeighborhoods(names);
          if (names.length > 0) {
            setSelectedNeighborhood(names[0]);
          }
        } else {
          setError('Failed to load neighborhoods');
        }
      } catch (err) {
        setError('Failed to load neighborhoods');
        console.error(err);
      }
    };
    loadNeighborhoods();
  }, []);

  // 加载选中街区的数据
  useEffect(() => {
    if (!selectedNeighborhood) return;

    const loadData = async () => {
      setLoading(true);
      try {
        const [dataRes, statsRes] = await Promise.all([
          staticDataService.getNeighborhoodData(selectedNeighborhood),
          staticDataService.getStats(selectedNeighborhood),
        ]);

        if (dataRes.status === 'success') {
          setData(dataRes.data);
        }

        if (statsRes.status === 'success') {
          setStats(statsRes.data);
        }
      } catch (err) {
        setError('Failed to load data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [selectedNeighborhood]);

  // 加载对比数据
  useEffect(() => {
    const loadComparison = async () => {
      try {
        const response = await staticDataService.getComparison();
        if (response.status === 'success') {
          setComparisonData(response.data);
        }
      } catch (err) {
        console.error('Failed to load comparison data', err);
      }
    };
    loadComparison();
  }, []);

  if (loading && !data) {
    return (
      <div className="dashboard loading">
        <div className="loader">Loading...</div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-content">
          <h1>Philadelphia Street Safety Analysis</h1>
          <p>Traffic Facilities and Incident Distribution Dashboard</p>
        </div>

        {/* 街区选择器 */}
        <NeighborhoodSelector
          neighborhoods={neighborhoods}
          selectedNeighborhood={selectedNeighborhood}
          onSelect={setSelectedNeighborhood}
        />
      </header>

      {/* Main Content */}
      <main className="dashboard-main">
        <div className="content-grid">
          {/* Left Panel - Stats */}
          <aside className="left-panel">
            <StatsPanel stats={stats} neighborhood={selectedNeighborhood} />
          </aside>

          {/* Center - Map */}
          <section className="center-panel">
            {error ? (
              <div className="error-message">{error}</div>
            ) : (
              <Map neighborhood={selectedNeighborhood} data={data} />
            )}
          </section>
        </div>

        {/* Bottom - Comparison Chart */}
        <div className="bottom-panel">
          <ComparisonChart data={comparisonData} />
        </div>
      </main>

      {/* Footer */}
      <footer className="dashboard-footer">
        <p>
          Data Source: Google Street View (YOLO Detection) | Crime Incidents |
          Philadelphia Police Department
        </p>
      </footer>
    </div>
  );
};

export default Dashboard;
