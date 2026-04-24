import React, { useState, createContext, useContext } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './components/AuthContext';
import Login from './components/Login';
import Register from './components/Register';
import ProtectedRoute from './components/ProtectedRoute';
import RankingTable from './components/RankingTable';
import ConfigPanel from './components/ConfigPanel';
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
          zIndex: 9999
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <div>
              <strong>Error</strong>
              <div>{error.message}</div>
            </div>
            <button onClick={clearError} style={{ background: 'none', border: 'none', color: 'white' }}>
              ×
            </button>
          </div>
        </div>
      )}
    </ErrorContext.Provider>
  );
};

// Login / Register
const AuthContainer = () => {
  const [isLogin, setIsLogin] = useState(true);

  return (
    <div className="min-h-screen auth-bg">
      <header className="header">
        <h1>Plataforma Analítica Territorial</h1>
      </header>

      <main>
        {isLogin ? (
          <Login onSwitchToRegister={() => setIsLogin(false)} />
        ) : (
          <Register onSwitchToLogin={() => setIsLogin(true)} />
        )}
      </main>
    </div>
  );
};

// Dashboard
const Dashboard = () => {
  const { user, logout } = useAuth();

  return (
    <div>
      {/* HEADER */}
      <div style={{
        backgroundColor: '#0d9488',
        color: 'white',
        padding: '1rem',
        display: 'flex',
        justifyContent: 'space-between'
      }}>
        <h1>Dashboard</h1>
        <div>
          <span>{user?.username}</span>
          <button onClick={logout}>Logout</button>
        </div>
      </div>

      {/* CONTENIDO */}
      <div style={{ padding: '20px' }}>
        <RankingTable />
        <hr style={{ margin: '2rem 0' }} />
        <ConfigPanel />
      </div>
    </div>
  );
};

// App principal
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