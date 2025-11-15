import React from 'react';
import './MixingProgress.css';

interface MixingProgressProps {
  cocktailName: string;
  progress: number;
  onCancel: () => void;
}

export const MixingProgress: React.FC<MixingProgressProps> = ({
  cocktailName,
  progress,
  onCancel
}) => {
  return (
    <div className="mixing-overlay">
      <div className="mixing-modal">
        <div className="mixing-title">PREPARING COCKTAIL</div>

        <div className="cocktail-name">{cocktailName.toUpperCase()}</div>

        <div className="progress-section">
          <div className="progress-bar-container">
            <div
              className="progress-bar-fill"
              style={{ width: `${progress}%` }}
            >
              <div className="progress-scanner"></div>
            </div>
          </div>
          <div className="progress-text">{Math.round(progress)}%</div>
        </div>

        <div className="mixing-status">
          {progress < 100 ? (
            <>
              <div className="status-indicator"></div>
              <span>DISPENSING...</span>
            </>
          ) : (
            <span className="complete">COMPLETE</span>
          )}
        </div>

        <button
          className="kitt-button red large"
          onClick={onCancel}
          disabled={progress >= 100}
        >
          {progress < 100 ? '⚠ EMERGENCY STOP' : 'CLOSE'}
        </button>
      </div>
    </div>
  );
};
