import React, { useState, useEffect } from 'react';
import './App.css';
import { CocktailList } from './components/CocktailList';
import { ConfigScreen } from './components/ConfigScreen';
import { StatusScreen } from './components/StatusScreen';
import { CalibrateScreen } from './components/CalibrateScreen';
import { MixingProgress } from './components/MixingProgress';
import { api } from './services/api';
import { Cocktail, SystemStatus } from './types';
import ShoppingGuide from './components/ShoppingGuide';

type Screen = 'list' | 'config' | 'status' | 'calibrate' | 'shopping-guide';

function App() {
  const [screen, setScreen] = useState<Screen>('list');
  const [cocktails, setCocktails] = useState<Cocktail[]>([]);
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadCocktails();
    loadStatus();

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
      const data = await api.getStatus();
      setStatus(data);
    } catch (err) {
      console.error('Failed to load status:', err);
    }
  };

  const handleCocktailSelect = async (cocktail: Cocktail) => {
    try {
      await api.makeCocktail(cocktail.name, 200);
      loadStatus();
    } catch (err) {
      setError('Failed to make cocktail');
      console.error(err);
    }
  };

  const handleConfigOpen = () => {
    setScreen('config');
  };

  const handleConfigClose = () => {
    setScreen('list');
    loadCocktails(); // Reload cocktails to update can_make status
  };

  const handleStatusOpen = () => {
    setScreen('status');
  };

  const handleShoppingGuideOpen = () => {
    setScreen('shopping-guide');
  };

  const handleCancelMixing = async () => {
    try {
      await api.cancelMixing();
      loadStatus();
    } catch (err) {
      console.error('Failed to cancel mixing:', err);
    }
  };

  return (
    <div className="App">
      <div className="scanner"></div>

      {loading ? (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flex: 1,
          color: '#ff0000',
          fontSize: '16px',
          fontWeight: 'bold',
          letterSpacing: '2px'
        }}>
          INITIALIZING...
        </div>
      ) : error ? (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          flex: 1,
          gap: '12px'
        }}>
          <div style={{color: '#ff0000', fontSize: '14px', fontWeight: 'bold'}}>{error}</div>
          <button className="kitt-button" onClick={loadCocktails}>
            RETRY
          </button>
        </div>
      ) : (
        <>
          {screen === 'list' && (
            <CocktailList
              cocktails={cocktails}
              onSelect={handleCocktailSelect}
              onConfigOpen={handleConfigOpen}
              onStatusOpen={handleStatusOpen}
              onShoppingGuideOpen={handleShoppingGuideOpen}
            />
          )}
          {screen === 'config' && (
            <ConfigScreen
              onBack={handleConfigClose}
              onCalibrate={() => setScreen('calibrate')}
            />
          )}
          {screen === 'status' && status && (
            <StatusScreen
              status={status}
              onBack={() => setScreen('list')}
              onRefresh={loadCocktails}
            />
          )}
          {screen === 'calibrate' && (
            <CalibrateScreen onBack={() => setScreen('config')} />
          )}
          {screen === 'shopping-guide' && (
            <ShoppingGuide onBack={() => setScreen('list')} cocktails={cocktails} />
          )}
        </>
      )}

      {status?.is_mixing && status.current_cocktail && (
        <MixingProgress
          cocktailName={status.current_cocktail}
          progress={status.progress || 0}
          onCancel={handleCancelMixing}
        />
      )}
    </div>
  );
}

export default App;
