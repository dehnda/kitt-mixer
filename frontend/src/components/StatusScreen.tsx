import React from 'react';
import { motion } from 'framer-motion';
import { SystemStatus } from '../types';
import './StatusScreen.css';

interface StatusScreenProps {
  status: SystemStatus;
  onBack: () => void;
}

export const StatusScreen: React.FC<StatusScreenProps> = ({ status, onBack }) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={{ duration: 0.3 }}
      className="status-screen"
    >
      <div className="status-header">
        <h2 className="status-title">SYSTEM STATUS</h2>
      </div>

      {status.is_mixing && status.current_cocktail && (
        <div className="mixing-info">
          <div className="mixing-title">MIXING: {status.current_cocktail}</div>
          <div className="progress-bar">
            <motion.div
              className="progress-fill"
              initial={{ width: 0 }}
              animate={{ width: `${status.progress}%` }}
              transition={{ duration: 0.5 }}
            />
            <div className="progress-text">{Math.round(status.progress)}%</div>
          </div>
          <div className="mixing-animation">
            {[...Array(8)].map((_, i) => (
              <motion.div
                key={i}
                className="mixing-bar"
                animate={{
                  scaleY: [1, 1.5, 1],
                  opacity: [0.3, 1, 0.3],
                }}
                transition={{
                  duration: 1,
                  repeat: Infinity,
                  delay: i * 0.1,
                }}
              />
            ))}
          </div>
        </div>
      )}

      {!status.is_mixing && (
        <div className="idle-message">
          <div className="idle-text">SYSTEM READY</div>
          <div className="idle-subtext">AWAITING INSTRUCTIONS</div>
        </div>
      )}

      <div className="pumps-section">
        <h3 className="section-title">PUMP STATUS</h3>
        <div className="pumps-grid">
          {status.pumps.map((pump) => (
            <div
              key={pump.id}
              className={`pump-card ${pump.is_active ? 'active' : ''} ${pump.liquid ? 'loaded' : 'empty'}`}
            >
              <div className="pump-header">
                <span className="pump-id">PUMP {pump.id}</span>
                {pump.is_active && <span className="pump-active">ACTIVE</span>}
              </div>
              <div className="pump-liquid">
                {pump.liquid || 'EMPTY'}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="status-actions">
        <button
          className="kitt-button secondary"
          onClick={onBack}
          disabled={status.is_mixing}
        >
          BACK
        </button>
      </div>
    </motion.div>
  );
};
