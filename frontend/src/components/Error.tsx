import { useNavigate } from 'react-router';

type Props = { message: string };

export default function ErrorScreen({ message }: Props) {
  const navigate = useNavigate();
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        flex: 1,
        gap: '12px',
      }}
    >
      <div style={{ color: '#ff0000', fontSize: '14px', fontWeight: 'bold' }}>
        {message}
      </div>
      <button className="kitt-button" onClick={() => navigate(0)}>
        RETRY
      </button>
    </div>
  );
}
