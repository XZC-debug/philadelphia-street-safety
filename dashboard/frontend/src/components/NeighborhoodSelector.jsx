import React, { useState } from 'react';
import '../styles/NeighborhoodSelector.css';

const NeighborhoodSelector = ({ neighborhoods, selectedNeighborhood, onSelect }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="neighborhood-selector">
      <label htmlFor="neighborhood-dropdown">Select Neighborhood:</label>
      <div className="custom-select">
        <button
          className="select-button"
          onClick={() => setIsOpen(!isOpen)}
        >
          {selectedNeighborhood || 'Choose...'}
        </button>
        {isOpen && (
          <div className="select-dropdown">
            {neighborhoods.map((nb) => (
              <div
                key={nb}
                className={`select-option ${selectedNeighborhood === nb ? 'active' : ''}`}
                style={{
                  padding: '12px',
                  cursor: 'pointer',
                  color: selectedNeighborhood === nb ? 'white' : '#333',
                  backgroundColor: selectedNeighborhood === nb ? '#2196F3' : 'white',
                  borderBottom: '1px solid #f0f0f0',
                  fontSize: '14px',
                  fontWeight: selectedNeighborhood === nb ? '600' : '500',
                  transition: 'all 0.2s ease',
                }}
                onMouseEnter={(e) => {
                  if (selectedNeighborhood !== nb) {
                    e.currentTarget.style.backgroundColor = '#f0f7ff';
                    e.currentTarget.style.color = '#1976d2';
                  }
                }}
                onMouseLeave={(e) => {
                  if (selectedNeighborhood !== nb) {
                    e.currentTarget.style.backgroundColor = 'white';
                    e.currentTarget.style.color = '#333';
                  }
                }}
                onClick={() => {
                  onSelect(nb);
                  setIsOpen(false);
                }}
              >
                {nb}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default NeighborhoodSelector;
