import { useNavigate } from 'react-router';

export default function NotFound() {
  const navigate = useNavigate();
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        flex: 1,
        gap: '24px',
        padding: '20px',
      }}
    >
      <div style={{ fontSize: '72px', fontWeight: 'bold', color: '#ff0000' }}>
        404
      </div>
      <div
        style={{ fontSize: '18px', fontWeight: 'bold', textAlign: 'center' }}
      >
        LOCATION NOT FOUND
      </div>
      <div
        style={{
          fontSize: '14px',
          color: '#888',
          textAlign: 'center',
          maxWidth: '400px',
        }}
      >
        I'm afraid this destination does not exist in my database, Michael. I
        suggest we return to the main interface.
      </div>
      <button className="kitt-button" onClick={() => navigate('/cocktails')}>
        RETURN TO BASE
      </button>
    </div>
  );
}
