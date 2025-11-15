import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Cocktail } from '../types';
import './CocktailDetail.css';

interface CocktailDetailProps {
  cocktail: Cocktail;
  onMake: (name: string, size: number) => void;
  onBack: () => void;
}

const SIZES = [
  { label: 'SMALL', ml: 150 },
  { label: 'MEDIUM', ml: 200 },
  { label: 'LARGE', ml: 250 },
];

export const CocktailDetail: React.FC<CocktailDetailProps> = ({ cocktail, onMake, onBack }) => {
  const [selectedSize, setSelectedSize] = useState(SIZES[1]);

  const handleMake = () => {
    onMake(cocktail.name, selectedSize.ml);
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -50 }}
      transition={{ duration: 0.3 }}
      className="cocktail-detail"
    >
      <div className="detail-header">
        <h2 className="detail-title">{cocktail.name}</h2>
        <div className="detail-meta">
          {cocktail.taste && <span className="tag">{cocktail.taste}</span>}
          {cocktail.timing && <span className="tag">{cocktail.timing}</span>}
          {cocktail.preparation && <span className="tag">{cocktail.preparation}</span>}
        </div>
      </div>

      <div className="ingredients-section">
        <h3 className="section-title">INGREDIENTS</h3>
        <div className="ingredients-list">
          {cocktail.ingredients.map((ing, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="ingredient-item"
            >
              <span className="ingredient-amount">
                {ing.amount} {ing.unit}
              </span>
              <span className="ingredient-name">{ing.ingredient}</span>
              {cocktail.missing_ingredients?.includes(ing.ingredient) && (
                <span className="missing-badge">MISSING</span>
              )}
            </motion.div>
          ))}
        </div>
      </div>

      {cocktail.can_make && (
        <div className="size-section">
          <h3 className="section-title">SIZE</h3>
          <div className="size-buttons">
            {SIZES.map((size) => (
              <button
                key={size.label}
                className={`kitt-button ${selectedSize.label === size.label ? '' : 'secondary'}`}
                onClick={() => setSelectedSize(size)}
              >
                {size.label}<br/>
                <span style={{fontSize: '10px'}}>{size.ml}ml</span>
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="action-buttons">
        <button className="kitt-button secondary" onClick={onBack}>
          BACK
        </button>
        {cocktail.can_make ? (
          <button className="kitt-button make-button" onClick={handleMake}>
            MAKE IT
          </button>
        ) : (
          <button className="kitt-button" disabled>
            UNAVAILABLE
          </button>
        )}
      </div>
    </motion.div>
  );
};
