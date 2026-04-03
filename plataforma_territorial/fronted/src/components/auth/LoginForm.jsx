import React, { useState } from 'react';
import { api } from '../../services/api';
import './auth.css';

export default function LoginForm({ onLoggedIn, onGoRegister }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await api.login(username, password);
      onLoggedIn();
    } catch (err) {
      setError(err.message || 'No se pudo iniciar sesión');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-wrap">
      <div className="auth-card">
        <h1>Iniciar sesión</h1>
        <p className="sub">Accede para cargar datasets y ver zonas.</p>

        {error && (
          <div className="auth-error" role="alert">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="auth-field">
            <label htmlFor="login-user">Usuario</label>
            <input
              id="login-user"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              required
            />
          </div>
          <div className="auth-field">
            <label htmlFor="login-pass">Contraseña</label>
            <input
              id="login-pass"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
            />
          </div>
          <div className="auth-actions">
            <button type="submit" className="auth-primary" disabled={loading}>
              {loading ? 'Entrando…' : 'Entrar'}
            </button>
            {onGoRegister && (
              <button
                type="button"
                className="auth-secondary"
                onClick={onGoRegister}
              >
                Crear cuenta
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
