import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  async function onSubmit(e) {
    e.preventDefault();
    try {
      const payload = await login(email, password);
      setError('');
      if (payload.user.role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/dashboard');
      }
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <main className="layout small">
      <h1>Login</h1>
      <form onSubmit={onSubmit}>
        <input data-testid="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
        <input data-testid="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" />
        <button data-testid="login-submit" type="submit">Login</button>
      </form>
      {error ? <p className="error">{error}</p> : null}
    </main>
  );
}
