import React, { useState } from 'react';
import { Cocktail } from '../types';
import './CocktailList.css';

interface CocktailListProps {
  cocktails: Cocktail[];
  onSelect: (cocktail: Cocktail) => void;
  onConfigOpen: () => void;
  onStatusOpen: () => void;
}

export const CocktailList: React.FC<CocktailListProps> = ({ cocktails, onSelect, onConfigOpen, onStatusOpen }) => {
  const [filter, setFilter] = useState<'all' | 'available'>('all');
  const [selectedCocktail, setSelectedCocktail] = useState<Cocktail | null>(null);
  const [showIngredients, setShowIngredients] = useState(false);

  const filteredCocktails = filter === 'available'
    ? cocktails.filter(c => c.can_make)
    : cocktails;

  const hasAvailableCocktails = cocktails.some(c => c.can_make);

  const handleSelect = (cocktail: Cocktail) => {
    if (selectedCocktail?.name === cocktail.name) {
      // Toggle off if clicking the same cocktail
      setShowIngredients(!showIngredients);
    } else {
      // Select new cocktail and show ingredients
      setSelectedCocktail(cocktail);
      setShowIngredients(true);
    }
    if (selectedCocktail?.name !== cocktail.name) {
      setSelectedCocktail(cocktail);
    }
  };

  const handleEngage = () => {
    if (selectedCocktail && selectedCocktail.can_make) {
      onSelect(selectedCocktail);
    }
  };

  return (
    <div className="cocktail-list-page">
      <div className="display-screen">
        <div className="display-title">K.I.T.T</div>

        <div className={`cocktail-content ${showIngredients ? 'with-details' : ''}`}>
          <div className="cocktail-grid">
            {filteredCocktails.map((cocktail) => (
              <div
                key={cocktail.name}
                className={`cocktail-item ${selectedCocktail?.name === cocktail.name ? 'selected' : ''} ${!cocktail.can_make ? 'unavailable' : ''}`}
                onClick={() => handleSelect(cocktail)}
              >
                {cocktail.name.toUpperCase()}
              </div>
            ))}
          </div>

          {selectedCocktail && showIngredients && (
            <div className="ingredients-panel">
              <div className="panel-title">{selectedCocktail.name.toUpperCase()}</div>
              <div className="panel-subtitle">INGREDIENTS</div>
              <div className="ingredient-list">
                {selectedCocktail.ingredients.map((ing, index) => (
                  <div key={index} className="ingredient-line">
                    <span className="ing-name">{ing.ingredient.toUpperCase()}</span>
                    <span className="ing-amount">{ing.amount} {ing.unit.toUpperCase()}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      <button
        className={`kitt-button large ${selectedCocktail?.can_make ? 'green' : 'gray'}`}
        onClick={handleEngage}
        disabled={!selectedCocktail?.can_make}
      >
        ▶ ENGAGE
      </button>

      <div className="control-buttons">
        <button
          className={`kitt-button small wide ${filter === 'all' ? '' : 'gray'}`}
          onClick={() => setFilter('all')}
        >
          ALL
        </button>
        <button
          className={`kitt-button small narrow ${
            filter === 'available'
              ? (hasAvailableCocktails ? 'green' : 'red')
              : (hasAvailableCocktails ? 'green' : 'red')
          }`}
          onClick={() => setFilter('available')}
        >
          AVAILABLE
        </button>
        <button
          className="kitt-button small wide orange"
          onClick={onConfigOpen}
        >
          CONFIG
        </button>
        <button className="kitt-button green small wide" onClick={onStatusOpen}>
          ● STATUS
        </button>
      </div>
    </div>
  );
};
