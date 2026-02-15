import useStatus from './api/useStatus';
import './App.css';
import { Outlet } from 'react-router';
import Loading from './components/Loading';
import ErrorScreen from './components/Error';
import { MixingProgress } from './components/MixingProgress';

function Layout() {
  const status = useStatus();

  if (status.isPending) {
    return <Loading />;
  }
  if (status.isError) {
    return (
      <ErrorScreen message="Failed to load system status. Please try again." />
    );
  }

  return (
    <div className="App">
      <div className="scanner"></div>

      <Outlet />

      {status?.data.is_mixing && status.data.current_cocktail && (
        <MixingProgress
          cocktailName={status.data.current_cocktail}
          progress={status.data.progress || 0}
        />
      )}
    </div>
  );
}

export default Layout;
