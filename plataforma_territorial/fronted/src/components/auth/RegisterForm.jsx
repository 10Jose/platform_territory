import React, { useState } from 'react';
import { api } from '../../services/api';
import './auth.css';

export default function RegisterForm({ onRegistered, onGoLogin }) {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await api.register({
        username,
        email,
        password,
        full_name: fullName.trim() || null,
      });
      await api.login(username, password);
      onRegistered();
    } catch (err) {
      setError(err.message || 'No se pudo registrar');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-wrap">
      <div className="auth-card">
        <h1>Crear cuenta</h1>
        <p className="sub">Regístrate para usar la plataforma.</p>

        {error && (
          <div className="auth-error" role="alert">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="auth-field">
            <label htmlFor="reg-user">Usuario</label>
            <input
              id="reg-user"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              required
            />
          </div>
          <div className="auth-field">
            <label htmlFor="reg-email">Correo</label>
            <input
              id="reg-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              required
            />
          </div>
          <div className="auth-field">
            <label htmlFor="reg-name">Nombre completo (opcional)</label>
            <input
              id="reg-name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              autoComplete="name"
            />
          </div>
          <div className="auth-field">
            <label htmlFor="reg-pass">Contraseña</label>
            <input
              id="reg-pass"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="new-password"
              required
            />
          </div>
          <div className="auth-actions">
            <button type="submit" className="auth-primary" disabled={loading}>
              {loading ? 'Creando…' : 'Registrarme'}
            </button>
            {onGoLogin && (
              <button
                type="button"
                className="auth-secondary"
                onClick={onGoLogin}
              >
                Ya tengo cuenta
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
