import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import './ConfigScreen.css';
import { Liquid } from '../types';

interface Pump {
  id: number;
  pin: number;
  liquid: string | null;
  liquid_id?: number | null;
  ml_per_second: number;
  is_active: boolean;
}

interface ConfigScreenProps {
  onBack: () => void;
  onCalibrate: () => void;
}

export const ConfigScreen: React.FC<ConfigScreenProps> = ({ onBack, onCalibrate }) => {
  const [pumps, setPumps] = useState<Pump[]>([]);
  const [liquids, setLiquids] = useState<Liquid[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [calibrating, setCalibrating] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [editingPump, setEditingPump] = useState<Pump | null>(null);
  const [editLiquidId, setEditLiquidId] = useState<number | null>(null);
  const [editFlowRate, setEditFlowRate] = useState<number>(0);
  const [calibratingPump, setCalibratingPump] = useState<Pump | null>(null);
  const [testDuration, setTestDuration] = useState<number>(10);
  const [measuredVolume, setMeasuredVolume] = useState<number>(0);
  const [calculatedRate, setCalculatedRate] = useState<number>(0);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  useEffect(() => {
    loadConfig();
    // eslint-disable-next-line react-hooks/exhaustive-deps
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

  const handleLiquidChange = async (pumpId: number, liquidId: number | null) => {
    try {
      setSaving(true);
      const response = await fetch(`${API_BASE_URL}/api/v1/pumps/${pumpId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ liquid_id: liquidId }),
      });

      if (!response.ok) throw new Error('Failed to update pump');

      // Reload pumps to get updated liquid name
      await loadConfig();
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

  const openEditModal = (pump: Pump) => {
    setEditingPump(pump);
    setEditLiquidId(pump.liquid_id || null);
    setEditFlowRate(pump.ml_per_second);
  };

  const closeEditModal = () => {
    setEditingPump(null);
    setEditLiquidId(null);
    setEditFlowRate(0);
  };

  const adjustFlowRate = (delta: number) => {
    setEditFlowRate(Math.max(0.1, Math.round((editFlowRate + delta) * 10) / 10));
  };

  const saveEditedPump = async () => {
    if (!editingPump) return;

    try {
      setSaving(true);
      const response = await fetch(`${API_BASE_URL}/api/v1/pumps/${editingPump.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          liquid_id: editLiquidId,
          ml_per_second: editFlowRate
        }),
      });

      if (!response.ok) throw new Error('Failed to update pump');

      // Reload pumps to get updated liquid name
      await loadConfig();

      closeEditModal();
      setError(null);
    } catch (err) {
      setError('Failed to save pump configuration');
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const openCalibrateMode = (pump: Pump) => {
    setCalibratingPump(pump);
    setTestDuration(10);
    setMeasuredVolume(0);
    setCalculatedRate(pump.ml_per_second);
  };

  const closeCalibrateMode = () => {
    setCalibratingPump(null);
    setTestDuration(10);
    setMeasuredVolume(0);
    setCalculatedRate(0);
  };

  const adjustTestDuration = (delta: number) => {
    setTestDuration(Math.max(1, testDuration + delta));
  };

  const adjustMeasuredVolume = (delta: number) => {
    setMeasuredVolume(Math.max(0, Math.round((measuredVolume + delta) * 100) / 100));
  };

  const calculateFlowRate = () => {
    if (testDuration > 0 && measuredVolume > 0) {
      const rate = Math.round((measuredVolume / testDuration) * 10) / 10;
      setCalculatedRate(rate);
    }
  };

  const runCalibrationTest = async () => {
    if (!calibratingPump) return;

    try {
      setCalibrating(calibratingPump.id);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/api/v1/pumps/${calibratingPump.id}/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ duration_seconds: testDuration }),
      });

      if (!response.ok) throw new Error('Failed to start test');

      setTimeout(() => {
        setCalibrating(null);
      }, testDuration * 1000);
    } catch (err) {
      setError('Failed to run test');
      console.error(err);
      setCalibrating(null);
    }
  };

  const saveCalibrationRate = async () => {
    if (!calibratingPump || calculatedRate === 0) return;

    try {
      setSaving(true);
      const response = await fetch(`${API_BASE_URL}/api/v1/pumps/${calibratingPump.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ml_per_second: calculatedRate }),
      });

      if (!response.ok) throw new Error('Failed to save flow rate');

      setPumps(pumps.map(p =>
        p.id === calibratingPump.id ? { ...p, ml_per_second: calculatedRate } : p
      ));

      closeCalibrateMode();
      setError(null);
    } catch (err) {
      setError('Failed to save calibration');
      console.error(err);
    } finally {
      setSaving(false);
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
    <div className="config-screen">
      <div className="display-screen">
        <div className="display-title">PUMP CONFIGURATION</div>

        <div className="pump-grid">
          {pumps.map((pump) => (
            <div
              key={pump.id}
              className={`pump-card ${pump.liquid ? 'active' : ''} ${calibrating === pump.id ? 'calibrating' : ''}`}
              onClick={() => openEditModal(pump)}
              style={{ cursor: 'pointer' }}
            >
              <div className="pump-number">PUMP {pump.id}</div>
              <div className="pump-liquid">{pump.liquid ? pump.liquid.toUpperCase() : 'EMPTY'}</div>
              <div className="pump-flow">{pump.ml_per_second.toFixed(1)} ML/SEC</div>
              <div className="pump-action">
                {calibrating === pump.id ? (
                  <button
                    className="pump-test-btn calibrating"
                    onClick={stopCalibration}
                  >
                    STOP
                  </button>
                ) : (
                  <button
                    className="pump-test-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      startCalibration(pump.id, 5);
                    }}
                    disabled={calibrating !== null}
                  >
                    TEST
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="config-instruction">
          SELECT PUMP TO CONFIGURE LIQUID AND FLOW RATE
        </div>
      </div>

      <div className="config-control-buttons">
        <button className="kitt-button green" onClick={loadConfig}>
          SAVE CONFIG
        </button>
        <button className="kitt-button" onClick={onCalibrate}>
          CALIBRATE
        </button>
        <button className="kitt-button" onClick={() => {}}>
          PURGE ALL
        </button>
        <button className="kitt-button" onClick={onBack}>
          BACK
        </button>
      </div>

      {editingPump && (
        <div className="modal-overlay" onClick={closeEditModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-title">CONFIGURE PUMP {editingPump.id}</div>

            <div className="modal-section">
              <div className="modal-label">LIQUID:</div>
              <div className="liquid-selector">
                <button
                  className={`liquid-option ${editLiquidId === null ? 'selected' : ''}`}
                  onClick={() => setEditLiquidId(null)}
                >
                  EMPTY
                </button>
                {liquids.map((liquid) => (
                  <button
                    key={liquid.id}
                    className={`liquid-option ${editLiquidId === liquid.id ? 'selected' : ''}`}
                    onClick={() => setEditLiquidId(liquid.id)}
                  >
                    {liquid.name.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>

            <div className="modal-section">
              <div className="modal-label">FLOW RATE:</div>
              <div className="flow-rate-control">
                <button
                  className="flow-btn"
                  onClick={() => adjustFlowRate(-1)}
                >
                  -1.0
                </button>
                <button
                  className="flow-btn"
                  onClick={() => adjustFlowRate(-0.1)}
                >
                  -0.1
                </button>
                <div className="flow-value">
                  {editFlowRate.toFixed(1)} ML/SEC
                </div>
                <button
                  className="flow-btn"
                  onClick={() => adjustFlowRate(0.1)}
                >
                  +0.1
                </button>
                <button
                  className="flow-btn"
                  onClick={() => adjustFlowRate(1)}
                >
                  +1.0
                </button>
              </div>
            </div>

            <div className="modal-actions">
              <button
                className="kitt-button green large"
                onClick={saveEditedPump}
                disabled={saving}
              >
                SAVE
              </button>
              <button
                className="kitt-button large"
                onClick={() => {
                  closeEditModal();
                  if (editingPump) openCalibrateMode(editingPump);
                }}
              >
                CALIBRATE
              </button>
              <button
                className="kitt-button red large"
                onClick={closeEditModal}
              >
                CANCEL
              </button>
            </div>
          </div>
        </div>
      )}

      {calibratingPump && (
        <div className="modal-overlay" onClick={closeCalibrateMode}>
          <div className="modal-content calibrate-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-title">PUMP CALIBRATION</div>

            <div className="calibrate-section">
              <div className="section-header">SELECT PUMP</div>
              <div className="pump-selector-grid">
                {pumps.map((pump) => (
                  <button
                    key={pump.id}
                    className={`pump-selector-btn ${calibratingPump.id === pump.id ? 'selected' : ''} ${pump.liquid ? 'active' : ''}`}
                    onClick={() => setCalibratingPump(pump)}
                  >
                    PUMP {pump.id}
                  </button>
                ))}
              </div>
            </div>

            <div className="calibrate-info">
              <div className="calibrate-pump-name">
                PUMP {calibratingPump.id} - {calibratingPump.liquid?.toUpperCase() || 'EMPTY'}
              </div>
            </div>

            <div className="calibrate-controls">
              <div className="calibrate-row">
                <span className="calibrate-label">TEST DURATION</span>
                <div className="calibrate-adjuster">
                  <button className="adj-btn" onClick={() => adjustTestDuration(-1)}>-</button>
                  <div className="adj-value">{testDuration}</div>
                  <button className="adj-btn" onClick={() => adjustTestDuration(1)}>+</button>
                  <span className="adj-unit">SEC</span>
                </div>
              </div>

              <div className="calibrate-row">
                <span className="calibrate-label">MEASURED VOLUME</span>
                <div className="calibrate-adjuster">
                  <button className="adj-btn" onClick={() => adjustMeasuredVolume(-1)}>-</button>
                  <div className="adj-value">{measuredVolume.toFixed(2)}</div>
                  <button className="adj-btn" onClick={() => adjustMeasuredVolume(1)}>+</button>
                  <span className="adj-unit">ML</span>
                </div>
              </div>

              <div className="calibrate-row">
                <span className="calibrate-label">CALCULATED RATE</span>
                <div className="calibrate-result">
                  {calculatedRate.toFixed(1)} ML/SEC
                </div>
              </div>
            </div>

            <div className="calibrate-instruction">
              RUN TEST → MEASURE OUTPUT → ENTER VOLUME → SAVE
            </div>

            <div className="modal-actions calibrate-actions">
              <button
                className="kitt-button green"
                onClick={runCalibrationTest}
                disabled={calibrating !== null}
              >
                {calibrating === calibratingPump.id ? 'RUNNING...' : 'RUN TEST'}
              </button>
              <button
                className="kitt-button"
                onClick={calculateFlowRate}
                disabled={measuredVolume === 0}
              >
                CALCULATE
              </button>
              <button
                className="kitt-button"
                onClick={saveCalibrationRate}
                disabled={calculatedRate === 0 || saving}
              >
                SAVE RATE
              </button>
              <button
                className="kitt-button red"
                onClick={closeCalibrateMode}
              >
                BACK
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
