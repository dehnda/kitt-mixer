import React, { useMemo, useState } from 'react';
import type { Cocktail } from '../types';
import './CocktailList.css';
import useCocktails from '../api/useCocktails';
import { Outlet, useNavigate, useParams } from 'react-router';
import useCocktail from '../api/useCocktail';
import Loading from './Loading';
import ErrorScreen from './Error';
import useMakeCocktail from '../api/useMakeCocktail';

export const CocktailList: React.FC = () => {
  const params = useParams<{ name: string }>();
  const selectedCocktail = useCocktail(params.name);
  const cocktails = useCocktails();
  const makeCocktail = useMakeCocktail();
  const navigate = useNavigate();

  const [filter, setFilter] = useState<'all' | 'available'>('available');

  const filteredCocktails = useMemo(() => {
    if (cocktails.isPending || cocktails.isError) {
      return [];
    }

    return filter === 'available'
      ? cocktails.data.filter((c) => c.can_make)
      : cocktails.data;
  }, [cocktails, filter]);

  const handleSelect = (cocktail: Cocktail) => {
    if (selectedCocktail?.data?.name === cocktail.name) {
      // Toggle off if clicking the same cocktail
      navigate('/cocktails');
    } else if (selectedCocktail?.data?.name !== cocktail.name) {
      navigate(`/cocktails/${cocktail.name}`);
    }
  };

  const handleEngage = () => {
    if (selectedCocktail && selectedCocktail.data?.can_make) {
      makeCocktail.mutate({
        name: selectedCocktail.data.name,
        sizeMl: 200, // TODO - allow user to select size
      });
    }
  };

  if (cocktails.isPending) {
    return <Loading />;
  }
  if (cocktails.isError) {
    return (
      <ErrorScreen message="Failed to load cocktails. Please try again." />
    );
  }

  console.log({ selectedCocktail: selectedCocktail.data });

  return (
    <div className="cocktail-list-page">
      <div className="display-screen">
        <div className="display-title">K.I.T.T</div>

        <div
          className={`cocktail-content ${selectedCocktail.isEnabled ? 'with-details' : ''}`}
        >
          <div className="cocktail-grid">
            {filteredCocktails.map((cocktail) => (
              <div
                key={cocktail.name}
                className={`cocktail-item ${selectedCocktail?.data?.name === cocktail.name ? 'selected' : ''} ${!cocktail.can_make ? 'unavailable' : ''}`}
                onClick={() => handleSelect(cocktail)}
              >
                {cocktail.name.toUpperCase()}
              </div>
            ))}
          </div>

          <Outlet />
        </div>
      </div>

      <button
        className={`kitt-button large ${selectedCocktail?.data?.can_make ? 'green' : 'gray'}`}
        onClick={handleEngage}
        disabled={!selectedCocktail?.data?.can_make}
      >
        ▶ ENGAGE
      </button>

      <div className="control-buttons">
        <button
          className={`kitt-button small wide green`}
          onClick={() => setFilter(filter === 'all' ? 'available' : 'all')}
        >
          {filter === 'all'
            ? `ALL (${cocktails.data.length})`
            : `AVAILABLE (${cocktails.data.filter((c) => c.can_make).length})`}
        </button>
        <button
          className="kitt-button small wide orange"
          onClick={() => navigate('/config')}
        >
          CONFIG
        </button>
        <button
          className="kitt-button green small wide"
          onClick={() => navigate('/status')}
        >
          ● STATUS
        </button>
        <button
          className="kitt-button yellow small wide"
          onClick={() => navigate('/shopping-guide')}
        >
          SHOPPING GUIDE
        </button>
      </div>
    </div>
  );
};
