import { createBrowserRouter, Navigate } from 'react-router';
import { CocktailList } from './components/CocktailList';
import CocktailIngredients from './routes/CocktailIngredients';
import Layout from './Layout';
import NotFound from './components/NotFound';
import ShoppingGuide from './components/ShoppingGuide';
import { StatusScreen } from './components/StatusScreen';
import { ConfigScreen } from './components/ConfigScreen';
import { CalibrateScreen } from './components/CalibrateScreen';

const router = createBrowserRouter([
  {
    // redirect to cocktails
    path: '/',
    Component: Layout,
    children: [
      {
        index: true,
        Component: () => <Navigate to="/cocktails" />,
      },
      {
        path: '/cocktails',
        Component: CocktailList,
        children: [
          {
            path: ':name',
            Component: CocktailIngredients,
          },
        ],
      },
      {
        path: '/config',
        Component: ConfigScreen,
      },
      {
        path: '/status',
        Component: StatusScreen,
      },
      {
        path: '/shopping-guide',
        Component: ShoppingGuide,
      },
      {
        path: '/calibrate',
        Component: CalibrateScreen,
      },
      {
        path: '*',
        Component: NotFound,
      },
    ],
  },
]);

export default router;
