// AI Slob
import { useState, useMemo } from 'react';
import type { Cocktail } from '../types';
import './ShoppingGuide.css';
import useCocktails from '../api/useCocktails';
import { useNavigate } from 'react-router';

const MAX_PUMPS = 8;

export default function ShoppingGuide() {
  const cocktails = useCocktails();
  const navigate = useNavigate();

  const [selected, setSelected] = useState<Set<string>>(new Set());

  // All unique ingredient names across every cocktail
  const allIngredients = useMemo(() => {
    if (cocktails.isPending || cocktails.isError) {
      return [];
    }

    const names = new Set<string>();
    cocktails.data.forEach((c) =>
      c.ingredients.forEach((i) => names.add(i.ingredient))
    );
    return Array.from(names).sort((a, b) => a.localeCompare(b));
  }, [cocktails]);

  // Cocktails that can be made using *only* the selected ingredients
  const makeable = useMemo(() => {
    if (cocktails.isPending || cocktails.isError) {
      return [];
    }
    if (selected.size === 0) {
      return [] as Cocktail[];
    }
    return cocktails.data.filter((c) =>
      c.ingredients.every((i) => selected.has(i.ingredient))
    );
  }, [cocktails, selected]);

  // For every ingredient NOT yet selected, count how many *new* cocktails
  // would become makeable if we added it (respecting the pump limit).
  const unlockMap = useMemo(() => {
    if (cocktails.isPending || cocktails.isError) {
      return new Map<string, number>();
    }

    const map = new Map<string, number>();
    const atLimit = selected.size >= MAX_PUMPS;

    allIngredients.forEach((ing) => {
      if (selected.has(ing)) {
        map.set(ing, 0);
        return;
      }
      if (atLimit) {
        map.set(ing, 0);
        return;
      }
      const hypothetical = new Set(selected);
      hypothetical.add(ing);
      const newCocktails = cocktails.data.filter(
        (c) =>
          c.ingredients.every((i) => hypothetical.has(i.ingredient)) &&
          !makeable.includes(c)
      );
      map.set(ing, newCocktails.length);
    });
    return map;
  }, [allIngredients, cocktails, selected, makeable]);

  // Count how many cocktails each ingredient appears in
  const usedInMap = useMemo(() => {
    if (cocktails.isPending || cocktails.isError) {
      return new Map<string, number>();
    }

    const map = new Map<string, number>();

    allIngredients.forEach((ing) => {
      const count = cocktails.data.filter((c) =>
        c.ingredients.some((i) => i.ingredient === ing)
      ).length;
      map.set(ing, count);
    });
    return map;
  }, [allIngredients, cocktails]);

  // Sort ingredients: selected first, then by unlock count desc
  const sortedIngredients = useMemo(() => {
    return [...allIngredients].sort((a, b) => {
      const aSelected = selected.has(a) ? 0 : 1;
      const bSelected = selected.has(b) ? 0 : 1;
      if (aSelected !== bSelected) return aSelected - bSelected;
      return (unlockMap.get(b) ?? 0) - (unlockMap.get(a) ?? 0);
    });
  }, [allIngredients, selected, unlockMap]);

  const toggle = (ing: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(ing)) {
        next.delete(ing);
      } else if (next.size < MAX_PUMPS) {
        next.add(ing);
      }
      return next;
    });
  };

  return (
    <div className="shopping-guide">
      <div className="display-screen">
        <div className="display-title">SHOPPING GUIDE</div>

        {/* Makeable cocktails banner */}
        <div className="sg-makeable-section">
          <div className="sg-makeable-label">
            COCKTAILS ({makeable.length}) — PUMPS {selected.size}/{MAX_PUMPS}
          </div>
          <div className="sg-makeable-list">
            {makeable.length > 0
              ? makeable.map((c) => c.name.toUpperCase()).join(', ')
              : 'SELECT INGREDIENTS BELOW'}
          </div>
        </div>

        {/* Ingredient list */}
        <div className="sg-ingredient-header">
          <span>INGREDIENT</span>
          <span className="sg-header-right">
            <span>USED IN</span>
            <span>UNLOCKS</span>
          </span>
        </div>

        <div className="sg-ingredient-list">
          {sortedIngredients.map((ing) => {
            const isSelected = selected.has(ing);
            const unlocks = unlockMap.get(ing) ?? 0;
            const disabled = !isSelected && selected.size >= MAX_PUMPS;

            return (
              <div
                key={ing}
                className={`sg-ingredient-row ${
                  isSelected ? 'selected' : ''
                } ${disabled ? 'disabled' : ''}`}
                onClick={() => !disabled && toggle(ing)}
              >
                <span className="sg-ing-name">
                  {isSelected ? '✓ ' : ''}
                  {ing.toUpperCase()}
                </span>
                <span className="sg-ing-right">
                  <span className="sg-ing-used-in">
                    {usedInMap.get(ing) ?? 0}
                  </span>
                  <span className="sg-ing-unlocks">
                    {isSelected ? 'ADDED' : unlocks > 0 ? `+${unlocks}` : '—'}
                  </span>
                </span>
              </div>
            );
          })}
        </div>
      </div>

      <button className="kitt-button" onClick={() => navigate(-1)}>
        ← BACK
      </button>
    </div>
  );
}
