import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './App.css';
import { CocktailList } from './components/CocktailList';
import { CocktailDetail } from './components/CocktailDetail';
import { StatusScreen } from './components/StatusScreen';
import { ConfigScreen } from './components/ConfigScreen';
import { ScannerAnimation } from './components/ScannerAnimation';
import { api } from './services/api';
import { Cocktail, SystemStatus } from './types';

type Screen = 'list' | 'detail' | 'status' | 'config';

function App() {
  const [screen, setScreen] = useState<Screen>('list');
  const [cocktails, setCocktails] = useState<Cocktail[]>([]);
  const [selectedCocktail, setSelectedCocktail] = useState<Cocktail | null>(null);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadCocktails();
    loadStatus();

    // Poll status every 2 seconds
    const interval = setInterval(loadStatus, 2000);
    return () => clearInterval(interval);
  }, []);

  const loadCocktails = async () => {
    try {
      setLoading(true);
      const data = await api.getCocktails();
      setCocktails(data);
      setError(null);
    } catch (err) {
      setError('Failed to load cocktails');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadStatus = async () => {
    try {
      const status = await api.getStatus();
      setSystemStatus(status);
    } catch (err) {
      console.error('Failed to load status:', err);
    }
  };

  const handleCocktailSelect = (cocktail: Cocktail) => {
    setSelectedCocktail(cocktail);
    setScreen('detail');
  };

  const handleMakeCocktail = async (cocktailName: string, size: number) => {
    try {
      setScreen('status');
      await api.makeCocktail(cocktailName, size);
      // Status polling will handle updates
    } catch (err) {
      setError('Failed to make cocktail');
      console.error(err);
    }
  };

  const handleBack = () => {
    if (screen === 'detail') {
      setScreen('list');
    } else if (screen === 'status') {
      setScreen('list');
      loadCocktails();
    } else if (screen === 'config') {
      setScreen('list');
      loadCocktails();
    }
  };

  const handleConfigOpen = () => {
    setScreen('config');
  };

  return (
    <div className="App">
      <ScannerAnimation />

      <header className="App-header">
        <div className="logo-container">
          <div className="logo-pulse"></div>
          <h1 className="kitt-logo">K.I.T.T.</h1>
        </div>
        <div className="subtitle">Cocktail Intelligence Transfer Terminal</div>
      </header>

      <main className="App-main">
        <AnimatePresence mode="wait">
          {loading ? (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="loading-screen"
            >
              <div className="kitt-loading">INITIALIZING...</div>
            </motion.div>
          ) : error ? (
            <motion.div
              key="error"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="error-screen"
            >
              <div className="kitt-error">{error}</div>
              <button className="kitt-button" onClick={loadCocktails}>
                RETRY
              </button>
            </motion.div>
          ) : screen === 'list' ? (
            <CocktailList
              key="list"
              cocktails={cocktails}
              onSelect={handleCocktailSelect}
              onConfigOpen={handleConfigOpen}
            />
          ) : screen === 'detail' && selectedCocktail ? (
            <CocktailDetail
              key="detail"
              cocktail={selectedCocktail}
              onMake={handleMakeCocktail}
              onBack={handleBack}
            />
          ) : screen === 'status' && systemStatus ? (
            <StatusScreen
              key="status"
              status={systemStatus}
              onBack={handleBack}
            />
          ) : screen === 'config' ? (
            <ConfigScreen
              key="config"
              onBack={handleBack}
            />
          ) : null}
        </AnimatePresence>
      </main>

      <footer className="App-footer">
        <div className="status-bar">
          <div className="status-item">
            <span className={`status-indicator ${systemStatus?.arduino_connected ? 'active' : 'inactive'}`}></span>
            SYSTEM {systemStatus?.arduino_connected ? 'ONLINE' : 'OFFLINE'}
          </div>
          {systemStatus?.is_mixing && (
            <div className="status-item mixing">
              <span className="status-indicator active"></span>
              MIXING IN PROGRESS
            </div>
          )}
        </div>
      </footer>
    </div>
  );
}

export default App;
