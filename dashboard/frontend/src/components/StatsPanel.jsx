import React from 'react';
import '../styles/StatsPanel.css';

const StatsPanel = ({ stats, neighborhood }) => {
  if (!stats) {
    return (
      <div className="stats-panel">
        <p>Loading statistics...</p>
      </div>
    );
  }

  return (
    <div className="stats-panel">
      <h2>{neighborhood}</h2>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Traffic Lights</div>
          <div className="stat-value">{stats.traffic_lights_count || 0}</div>
          <div className="stat-unit">facilities</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Stop Signs</div>
          <div className="stat-value">{stats.stop_signs_count || 0}</div>
          <div className="stat-unit">facilities</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Incidents</div>
          <div className="stat-value">{stats.incidents_count || 0}</div>
          <div className="stat-unit">reported</div>
        </div>
      </div>

      <div className="stats-section">
        <h3>Facility Density</h3>
        <div className="density-stats">
          {stats.facility_density && (
            <>
              <div className="density-item">
                <span>Traffic Lights per km²:</span>
                <strong>{stats.facility_density.traffic_lights_per_km2}</strong>
              </div>
              <div className="density-item">
                <span>Stop Signs per km²:</span>
                <strong>{stats.facility_density.stop_signs_per_km2}</strong>
              </div>
            </>
          )}
        </div>
      </div>

      {stats.incident_by_type && Object.keys(stats.incident_by_type).length > 0 && (
        <div className="stats-section">
          <h3>Top Incident Types</h3>
          <div className="incident-types">
            {Object.entries(stats.incident_by_type)
              .slice(0, 5)
              .map(([type, count]) => (
                <div key={type} className="incident-type-item">
                  <span className="type-name">{type}</span>
                  <span className="type-count">{count}</span>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default StatsPanel;
