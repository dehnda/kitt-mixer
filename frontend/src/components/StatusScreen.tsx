import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { SystemStatus } from '../types';
import './StatusScreen.css';

interface StatusScreenProps {
  status: SystemStatus;
  onBack: () => void;
  onRefresh: () => void;
}

export const StatusScreen: React.FC<StatusScreenProps> = ({ status, onBack, onRefresh }) => {
  const [testing, setTesting] = useState(false);
  const [diagnostics, setDiagnostics] = useState<any>(null);
  const pumps = status.pumps || [];
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const handleTestAll = async () => {
    try {
      setTesting(true);
      const response = await fetch(`${API_BASE_URL}/api/v1/pumps/test-all`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ duration_seconds: 3 }),
      });
      if (!response.ok) throw new Error('Test failed');
      alert('All pumps tested successfully');
    } catch (err) {
      console.error('Test all failed:', err);
      alert('Failed to test pumps');
    } finally {
      setTesting(false);
    }
  };

  const handleDiagnostics = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/status/diagnostics`);
      if (!response.ok) throw new Error('Diagnostics failed');
      const data = await response.json();
      setDiagnostics(data);
      alert(`Diagnostics:\nDatabase: ${data.database}\nArduino: ${data.arduino}\nPumps: ${data.pumps_ok}/${data.total_pumps}`);
    } catch (err) {
      console.error('Diagnostics failed:', err);
      alert('Diagnostics check failed');
    }
  };

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
        <button className="kitt-button" onClick={onRefresh}>
          REFRESH
        </button>
        <button className="kitt-button orange" onClick={handleDiagnostics}>
          DIAGNOSTICS
        </button>
        <button className="kitt-button yellow" onClick={handleTestAll} disabled={testing}>
          {testing ? 'TESTING...' : 'TEST ALL'}
        </button>
        <button className="kitt-button" onClick={onBack}>
          BACK
        </button>
      </div>
    </div>
  );
};
