import { useNavigate, useParams } from 'react-router';
import useCocktail from '../api/useCocktail';
import useMakeCocktail from '../api/useMakeCocktail';
import { useState } from 'react';
import Slider from '../components/Slider';

export default function CocktailIngredients() {
  const { name } = useParams<{ name: string }>();
  const navigate = useNavigate();
  const cocktail = useCocktail(name!);
  const makeCocktail = useMakeCocktail();
  const [sizeMultiplier, setSizeMultiplier] = useState(1);

  if (cocktail.isPending) {
    return <div>Loading...</div>;
  }
  if (cocktail.isError || !cocktail.data) {
    return <div>Error loading cocktail</div>;
  }

  const handleEngage = () => {
    if (cocktail.data?.can_make) {
      makeCocktail.mutate({
        name: cocktail.data.name,
        size_multiplier: sizeMultiplier,
      });
    }
  };

  return (
    <div className="ingredients-panel">
      <div className="panel-title">{cocktail.data.name.toUpperCase()}</div>
      <div className="panel-subtitle">INGREDIENTS</div>
      <div className="ingredient-list">
        {cocktail.data.ingredients.map((ing, index) => (
          <div key={index} className="ingredient-line">
            <span className="ing-name">{ing.ingredient.toUpperCase()}</span>
            <span className="ing-amount">
              {ing.amount} {ing.unit.toUpperCase()}
            </span>
          </div>
        ))}
      </div>

      <div style={{ padding: '10px' }}>
        <Slider onChange={setSizeMultiplier} value={sizeMultiplier} />
      </div>

      <button
        className={`kitt-button ${cocktail.data?.can_make ? 'green' : 'gray'}`}
        onClick={handleEngage}
        disabled={!cocktail.data?.can_make}
      >
        ▶ Engage (x{sizeMultiplier})
      </button>
      <button className="kitt-button" onClick={() => navigate('/cocktails')}>
        CLOSE
      </button>
    </div>
  );
}
