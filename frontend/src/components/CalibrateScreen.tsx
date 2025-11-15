import React, { useState, useEffect } from 'react';
import './CalibrateScreen.css';

interface Pump {
  id: number;
  pin: number;
  liquid: string | null;
  ml_per_second: number;
  is_active: boolean;
}

interface CalibrateScreenProps {
  onBack: () => void;
}

export const CalibrateScreen: React.FC<CalibrateScreenProps> = ({ onBack }) => {
  const [pumps, setPumps] = useState<Pump[]>([]);
  const [selectedPump, setSelectedPump] = useState<Pump | null>(null);
  const [testDuration, setTestDuration] = useState<number>(10);
  const [measuredVolume, setMeasuredVolume] = useState<number>(0);
  const [calculatedRate, setCalculatedRate] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [testing, setTesting] = useState(false);
  const [saving, setSaving] = useState(false);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  useEffect(() => {
    loadPumps();
  }, []);

  const loadPumps = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/v1/pumps`);
      const data = await response.json();
      setPumps(data);
      if (data.length > 0) {
        setSelectedPump(data[0]);
        setCalculatedRate(data[0].ml_per_second);
      }
    } catch (err) {
      console.error('Failed to load pumps:', err);
    } finally {
      setLoading(false);
    }
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

  const runTest = async () => {
    if (!selectedPump) return;

    try {
      setTesting(true);
      const response = await fetch(`${API_BASE_URL}/api/v1/pumps/${selectedPump.id}/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ duration_seconds: testDuration }),
      });

      if (!response.ok) throw new Error('Failed to start test');

      setTimeout(() => {
        setTesting(false);
      }, testDuration * 1000);
    } catch (err) {
      console.error('Failed to run test:', err);
      setTesting(false);
    }
  };

  const saveRate = async () => {
    if (!selectedPump || calculatedRate === 0) return;

    try {
      setSaving(true);
      const response = await fetch(`${API_BASE_URL}/api/v1/pumps/${selectedPump.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ml_per_second: calculatedRate }),
      });

      if (!response.ok) throw new Error('Failed to save flow rate');

      setPumps(pumps.map(p =>
        p.id === selectedPump.id ? { ...p, ml_per_second: calculatedRate } : p
      ));

      // Reset for next pump
      setMeasuredVolume(0);
    } catch (err) {
      console.error('Failed to save rate:', err);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="calibrate-screen">
        <div className="loading-message">LOADING...</div>
      </div>
    );
  }

  return (
    <div className="calibrate-screen">
      <div className="display-screen">
        <div className="display-title">PUMP CALIBRATION</div>

        <div className="calibrate-section">
          <div className="section-header">SELECT PUMP</div>
          <div className="pump-selector-grid">
            {pumps.map((pump) => (
              <button
                key={pump.id}
                className={`pump-selector-btn ${selectedPump?.id === pump.id ? 'selected' : ''} ${pump.liquid ? 'active' : ''}`}
                onClick={() => {
                  setSelectedPump(pump);
                  setCalculatedRate(pump.ml_per_second);
                  setMeasuredVolume(0);
                }}
              >
                PUMP {pump.id}
              </button>
            ))}
          </div>
        </div>

        {selectedPump && (
          <>
            <div className="calibrate-info">
              <div className="calibrate-pump-name">
                PUMP {selectedPump.id} - {selectedPump.liquid?.toUpperCase() || 'EMPTY'}
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
          </>
        )}
      </div>

      <div className="calibrate-control-buttons">
        <button
          className="kitt-button yellow"
          onClick={runTest}
          disabled={!selectedPump || testing}
        >
          {testing ? 'RUNNING...' : 'RUN TEST'}
        </button>
        <button
          className="kitt-button"
          onClick={calculateFlowRate}
          disabled={measuredVolume === 0}
        >
          CALCULATE
        </button>
        <button
          className="kitt-button green"
          onClick={saveRate}
          disabled={calculatedRate === 0 || saving}
        >
          SAVE RATE
        </button>
        <button className="kitt-button" onClick={onBack}>
          BACK
        </button>
      </div>
    </div>
  );
};
