import React, { useState, createContext, useContext } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './components/AuthContext';
import Login from './components/Login';
import Register from './components/Register';
import ProtectedRoute from './components/ProtectedRoute';
import FileUploadModern from './components/FileUploadModern';
import './styles/auth.css';

// Contexto global de errores
const ErrorContext = createContext();

export const useError = () => {
  const context = useContext(ErrorContext);
  if (!context) {
    throw new Error('useError debe usarse dentro de ErrorProvider');
  }
  return context;
};

const ErrorProvider = ({ children }) => {
  const [error, setError] = useState(null);

  const showError = (message, details = null) => {
    setError({ message, details, timestamp: Date.now() });
    setTimeout(() => setError(null), 5000);
  };

  const clearError = () => setError(null);

  return (
    <ErrorContext.Provider value={{ error, showError, clearError }}>
      {children}
      {error && (
        <div style={{
          position: 'fixed',
          top: '20px',
          right: '20px',
          backgroundColor: '#ef4444',
          color: 'white',
          padding: '1rem 1.5rem',
          borderRadius: '0.5rem',
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
          maxWidth: '400px',
          zIndex: 9999,
          animation: 'slideIn 0.3s ease-out'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
            <div>
              <div style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>Error</div>
              <div style={{ fontSize: '0.875rem' }}>{error.message}</div>
              {error.details && (
                <div style={{ fontSize: '0.75rem', marginTop: '0.5rem', opacity: 0.9 }}>
                  {error.details}
                </div>
              )}
            </div>
            <button
              onClick={clearError}
              style={{
                background: 'none',
                border: 'none',
                color: 'white',
                cursor: 'pointer',
                fontSize: '1.25rem',
                marginLeft: '1rem'
              }}
            >
              ×
            </button>
          </div>
        </div>
      )}
    </ErrorContext.Provider>
  );
};

// Componente que muestra Login/Registro
const AuthContainer = () => {
  const [isLogin, setIsLogin] = useState(true);

  return (
    <div className="min-h-screen auth-bg">
      <header className="header">
        <div className="header-content">
          <div className="flex items-center gap-3">
            <div className="logo-icon">
              <span className="material-symbols-outlined">landscape</span>
            </div>
            <h1 className="logo-text">Analytical Sanctuary</h1>
          </div>
        </div>
      </header>

      <main className="flex-grow flex items-center justify-center p-6 md:p-10">
        {isLogin ? (
          <Login onSwitchToRegister={() => setIsLogin(false)} />
        ) : (
          <Register onSwitchToLogin={() => setIsLogin(true)} />
        )}
      </main>

      <footer className="footer">
        <div className="footer-content">
          <div className="copyright">© 2024 Territorial Analytics. All rights reserved.</div>
          <div className="footer-links">
            <a href="#" className="footer-link">Privacy Policy</a>
            <a href="#" className="footer-link">Terms of Service</a>
            <a href="#" className="footer-link">Help Center</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

// Dashboard protegido (solo después de login)
const Dashboard = () => {
  const { user, logout } = useAuth();

  return (
    <div>
      {/* Barra superior */}
      <div style={{
        backgroundColor: '#0d9488',
        color: 'white',
        padding: '1rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <h1>Analytical Sanctuary</h1>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <span>Welcome, {user?.full_name || user?.username}</span>
          <button
            onClick={logout}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: 'rgba(255,255,255,0.2)',
              border: 'none',
              borderRadius: '0.5rem',
              cursor: 'pointer',
              color: 'white'
            }}
          >
            Logout
          </button>
        </div>
      </div>

      {/* Componente de carga de CSV */}
      <div style={{ padding: '1.5rem' }}>
        <FileUploadModern />
      </div>
    </div>
  );
};

// Componente principal
function App() {
  return (
    <ErrorProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<AuthContainer />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ErrorProvider>
  );
}

export default App;