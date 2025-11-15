import React from 'react';
import { motion } from 'framer-motion';
import { SystemStatus } from '../types';
import './StatusScreen.css';

interface StatusScreenProps {
  status: SystemStatus;
  onBack: () => void;
}

export const StatusScreen: React.FC<StatusScreenProps> = ({ status, onBack }) => {
  const pumps = status.pumps || [];

  return (
    <div className="status-screen">
      <div className="display-screen">
        <div className="display-title">SYSTEM STATUS</div>

        <div className="status-section">
          <div className="section-header">SYSTEM INFORMATION</div>
          <div className="status-info-grid">
            <div className="status-row">
              <span className="status-label">SYSTEM STATUS</span>
              <span className={`status-value ${status.is_mixing ? 'warning' : 'success'}`}>
                {status.is_mixing ? 'MIXING' : 'ONLINE'}
              </span>
            </div>
            <div className="status-row">
              <span className="status-label">ARDUINO CONNECTION</span>
              <span className="status-value success">CONNECTED</span>
            </div>
            <div className="status-row">
              <span className="status-label">COCKTAILS AVAILABLE</span>
              <span className="status-value info">{pumps.filter(p => p.liquid).length} / 45</span>
            </div>
            <div className="status-row">
              <span className="status-label">ACTIVE PUMPS</span>
              <span className="status-value info">{pumps.filter(p => p.is_active).length} / {pumps.length}</span>
            </div>
          </div>
        </div>

        <div className="status-section">
          <div className="section-header">PUMP STATUS</div>
          <div className="pump-status-list">
            {pumps.map((pump) => (
              <div key={pump.id} className="pump-status-row">
                <span className="pump-status-label">PUMP {pump.id} - {pump.liquid ? pump.liquid.toUpperCase() : 'EMPTY'}</span>
                <span className={`pump-status-value ${
                  !pump.liquid ? 'error' :
                  pump.liquid.toLowerCase().includes('low') ? 'warning' :
                  'success'
                }`}>
                  {!pump.liquid ? 'NOT CONFIGURED' :
                   pump.liquid.toLowerCase().includes('low') ? 'LOW LIQUID' :
                   'READY'}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="status-control-buttons">
        <button className="kitt-button">
          REFRESH
        </button>
        <button className="kitt-button">
          DIAGNOSTICS
        </button>
        <button className="kitt-button green">
          TEST ALL
        </button>
        <button className="kitt-button" onClick={onBack}>
          BACK
        </button>
      </div>
    </div>
  );
};
