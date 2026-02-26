import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export function NavBar() {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <nav className="nav">
      <Link to="/">Home</Link>
      {isAuthenticated ? <Link to="/dashboard">Dashboard</Link> : <Link to="/login">Login</Link>}
      {user?.role === 'admin' ? <Link to="/admin">Admin</Link> : null}
      {isAuthenticated ? (
        <button
          data-testid="logout"
          onClick={async () => {
            await logout();
            navigate('/login');
          }}
        >
          Logout
        </button>
      ) : null}
    </nav>
  );
}
