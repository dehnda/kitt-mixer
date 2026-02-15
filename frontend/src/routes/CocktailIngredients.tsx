import { useNavigate, useParams } from 'react-router';
import useCocktail from '../api/useCocktail';

export default function CocktailIngredients() {
  const { name } = useParams<{ name: string }>();
  const navigate = useNavigate();
  const cocktail = useCocktail(name!);

  if (cocktail.isPending) {
    return <div>Loading...</div>;
  }
  if (cocktail.isError || !cocktail.data) {
    return <div>Error loading cocktail</div>;
  }

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
      <button className="kitt-button" onClick={() => navigate('/cocktails')}>
        CLOSE
      </button>
    </div>
  );
}
