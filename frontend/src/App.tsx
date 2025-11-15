import React, { useState, useEffect } from 'react';
import './App.css';
import { CocktailList } from './components/CocktailList';
import { ConfigScreen } from './components/ConfigScreen';
import { api } from './services/api';
import { Cocktail } from './types';

type Screen = 'list' | 'config';

function App() {
  const [screen, setScreen] = useState<Screen>('list');
  const [cocktails, setCocktails] = useState<Cocktail[]>([]);
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
      await api.getStatus();
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
            />
          )}
          {screen === 'config' && (
            <ConfigScreen onBack={() => setScreen('list')} />
          )}
        </>
      )}
    </div>
  );
}

export default App;
