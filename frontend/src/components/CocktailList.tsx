import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Cocktail } from '../types';
import './CocktailList.css';

interface CocktailListProps {
  cocktails: Cocktail[];
  onSelect: (cocktail: Cocktail) => void;
  onConfigOpen: () => void;
}

export const CocktailList: React.FC<CocktailListProps> = ({ cocktails, onSelect, onConfigOpen }) => {
  const [filter, setFilter] = useState<'all' | 'available'>('all');

  const filteredCocktails = filter === 'available'
    ? cocktails.filter(c => c.can_make)
    : cocktails;

  return (
    <motion.div
      initial={{ opacity: 0, x: -50 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 50 }}
      transition={{ duration: 0.3 }}
      className="cocktail-list"
    >
      <div className="list-header">
        <div className="filter-buttons">
          <button
            className={`kitt-button ${filter === 'all' ? '' : 'secondary'}`}
            onClick={() => setFilter('all')}
          >
            ALL ({cocktails.length})
          </button>
          <button
            className={`kitt-button ${filter === 'available' ? '' : 'secondary'}`}
            onClick={() => setFilter('available')}
          >
            AVAILABLE ({cocktails.filter(c => c.can_make).length})
          </button>
        </div>
        <button
          className="kitt-button config-button"
          onClick={onConfigOpen}
          title="Configure Pumps"
        >
          ⚙
        </button>
      </div>

      <div className="cocktail-grid">
        {filteredCocktails.map((cocktail, index) => (
          <motion.div
            key={cocktail.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className={`cocktail-card ${cocktail.can_make ? 'available' : 'unavailable'}`}
            onClick={() => onSelect(cocktail)}
          >
            <div className="cocktail-name">{cocktail.name}</div>
            <div className="cocktail-meta">
              {cocktail.taste && <span className="tag">{cocktail.taste}</span>}
              {cocktail.timing && <span className="tag">{cocktail.timing}</span>}
            </div>
            {!cocktail.can_make && (
              <div className="unavailable-badge">UNAVAILABLE</div>
            )}
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
};

