import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import './ConfigScreen.css';

interface Pump {
  id: number;
  pin: number;
  liquid: string | null;
  ml_per_second: number;
  is_active: boolean;
}

interface ConfigScreenProps {
  onBack: () => void;
}

export const ConfigScreen: React.FC<ConfigScreenProps> = ({ onBack }) => {
  const [pumps, setPumps] = useState<Pump[]>([]);
  const [liquids, setLiquids] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [calibrating, setCalibrating] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      setLoading(true);
      // Load pumps
      const pumpsRes = await fetch(`${API_BASE_URL}/api/v1/pumps`);
      const pumpsData = await pumpsRes.json();
      setPumps(pumpsData);

      // Load available liquids
      const liquidsRes = await fetch(`${API_BASE_URL}/api/v1/liquids`);
      const liquidsData = await liquidsRes.json();
      setLiquids(liquidsData);

      setError(null);
    } catch (err) {
      setError('Failed to load configuration');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleLiquidChange = async (pumpId: number, liquid: string) => {
    try {
      setSaving(true);
      const response = await fetch(`${API_BASE_URL}/api/v1/pumps/${pumpId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ liquid: liquid || null }),
      });

      if (!response.ok) throw new Error('Failed to update pump');

      setPumps(pumps.map(p =>
        p.id === pumpId ? { ...p, liquid: liquid || null } : p
      ));
    } catch (err) {
      setError('Failed to update pump');
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const handleFlowRateChange = (pumpId: number, value: string) => {
    const flowRate = parseFloat(value);
    if (!isNaN(flowRate) && flowRate > 0) {
      setPumps(pumps.map(p =>
        p.id === pumpId ? { ...p, ml_per_second: flowRate } : p
      ));
    }
  };

  const saveFlowRate = async (pumpId: number) => {
    const pump = pumps.find(p => p.id === pumpId);
    if (!pump) return;

    try {
      setSaving(true);
      const response = await fetch(`${API_BASE_URL}/api/v1/pumps/${pumpId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ml_per_second: pump.ml_per_second }),
      });

      if (!response.ok) throw new Error('Failed to update flow rate');
      setError(null);
    } catch (err) {
      setError('Failed to save flow rate');
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const startCalibration = async (pumpId: number, duration: number = 10) => {
    try {
      setCalibrating(pumpId);
      setError(null);

      // Start pump for calibration
      const response = await fetch(`${API_BASE_URL}/api/v1/pumps/${pumpId}/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ duration_seconds: duration }),
      });

      if (!response.ok) throw new Error('Failed to start calibration');

      // Auto-stop after duration
      setTimeout(() => {
        setCalibrating(null);
      }, duration * 1000);
    } catch (err) {
      setError('Failed to calibrate pump');
      console.error(err);
      setCalibrating(null);
    }
  };

  const stopCalibration = async () => {
    try {
      await fetch(`${API_BASE_URL}/api/v1/status/stop`, { method: 'POST' });
      setCalibrating(null);
    } catch (err) {
      console.error('Failed to stop calibration:', err);
    }
  };

  if (loading) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="config-screen"
      >
        <div className="loading-message">LOADING CONFIGURATION...</div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -50 }}
      transition={{ duration: 0.3 }}
      className="config-screen"
    >
      <div className="config-header">
        <h2 className="config-title">SYSTEM CONFIGURATION</h2>
        {error && <div className="config-error">{error}</div>}
      </div>

      <div className="pumps-config">
        {pumps.map((pump) => (
          <motion.div
            key={pump.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: pump.id * 0.05 }}
            className={`pump-config-card ${calibrating === pump.id ? 'calibrating' : ''}`}
          >
            <div className="pump-config-header">
              <span className="pump-config-id">PUMP {pump.id}</span>
              <span className="pump-config-pin">PIN {pump.pin}</span>
            </div>

            <div className="pump-config-row">
              <label className="config-label">LIQUID:</label>
              <select
                className="config-select"
                value={pump.liquid || ''}
                onChange={(e) => handleLiquidChange(pump.id, e.target.value)}
                disabled={saving || calibrating === pump.id}
              >
                <option value="">-- EMPTY --</option>
                {liquids.map((liquid) => (
                  <option key={liquid} value={liquid}>
                    {liquid}
                  </option>
                ))}
              </select>
            </div>

            <div className="pump-config-row">
              <label className="config-label">FLOW RATE:</label>
              <div className="flow-rate-input-group">
                <input
                  type="number"
                  className="config-input"
                  value={pump.ml_per_second}
                  onChange={(e) => handleFlowRateChange(pump.id, e.target.value)}
                  onBlur={() => saveFlowRate(pump.id)}
                  min="0.1"
                  step="0.1"
                  disabled={saving || calibrating === pump.id}
                />
                <span className="unit-label">ml/sec</span>
              </div>
            </div>

            <div className="pump-config-actions">
              {calibrating === pump.id ? (
                <>
                  <div className="calibrating-indicator">PUMPING...</div>
                  <button
                    className="kitt-button secondary small"
                    onClick={stopCalibration}
                  >
                    STOP
                  </button>
                </>
              ) : (
                <>
                  <button
                    className="kitt-button secondary small"
                    onClick={() => startCalibration(pump.id, 5)}
                    disabled={saving || calibrating !== null}
                  >
                    TEST 5s
                  </button>
                  <button
                    className="kitt-button secondary small"
                    onClick={() => startCalibration(pump.id, 10)}
                    disabled={saving || calibrating !== null}
                  >
                    TEST 10s
                  </button>
                </>
              )}
            </div>
          </motion.div>
        ))}
      </div>

      <div className="config-actions">
        <button
          className="kitt-button secondary"
          onClick={onBack}
          disabled={saving || calibrating !== null}
        >
          BACK
        </button>
        <button
          className="kitt-button"
          onClick={loadConfig}
          disabled={saving || calibrating !== null}
        >
          RELOAD CONFIG
        </button>
      </div>
    </motion.div>
  );
};
