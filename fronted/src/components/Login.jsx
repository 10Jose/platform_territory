<<<<<<< HEAD
=======
/** Formulario de acceso; usa `authService.login` y navega al dashboard. */
>>>>>>> origin/Miguel
import React, { useState } from 'react';
import { useAuth } from './AuthContext';
import { useNavigate } from 'react-router-dom'; // ✅ IMPORTANTE
import '../styles/auth.css';

const Login = ({ onSwitchToRegister }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const { login, error } = useAuth();
  const navigate = useNavigate(); // ✅ NUEVO

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await login(username, password);

      // ✅ CAMBIO CLAVE (ANTES ROMPÍA TODO)
      navigate('/dashboard');

    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-[440px]">
      <header className="flex flex-col items-center mb-12">
        <div className="text-center">
          <h2 className="font-headline font-bold text-3xl text-on-surface tracking-tight mb-2">
            Iniciar Sesión
          </h2>
          <p className="text-on-surface-variant font-medium">
            Accede y explora la mejor opción para tu negocio
          </p>
        </div>
      </header>

      <div className="card">
        <form onSubmit={handleSubmit}>
          
          {/* Username */}
          <div className="form-group">
            <label className="form-label">Username</label>
            <div className="input-wrapper">
              <span className="material-symbols-outlined input-icon">person</span>
              <input
                type="text"
                className="input-field"
                placeholder="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
          </div>

          {/* Password */}
          <div className="form-group">
            <label className="form-label">Password</label>
            <div className="input-wrapper">
              <span className="material-symbols-outlined input-icon">lock</span>
              <input
                type={showPassword ? 'text' : 'password'}
                className="input-field"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
              >
                <span className="material-symbols-outlined">
                  {showPassword ? 'visibility_off' : 'visibility'}
                </span>
              </button>
            </div>
          </div>

          {/* Error */}
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {/* Botón */}
          <div className="pt-2">
            <button type="submit" className="btn-primary" disabled={isLoading}>
              {isLoading && <div className="spinner"></div>}
              Login
              <span className="material-symbols-outlined text-lg">arrow_forward</span>
            </button>
          </div>

        </form>

        {/* Registro */}
        <div className="divider">
          <p className="text-sm text-on-surface-variant font-medium">
            No tienes una cuenta todavia?
          </p>
          <button onClick={onSwitchToRegister} className="btn-outline">
            Crear una cuenta
          </button>
        </div>
      </div>
    </div>
  );
};

export default Login;