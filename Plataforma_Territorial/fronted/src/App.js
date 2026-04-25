import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './components/AuthContext';
import Login from './components/Login';
import Register from './components/Register';
import ProtectedRoute from './components/ProtectedRoute';
import './styles/auth.css';
import Dashboard from "./pages/Dashboard";

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
            <h1 className="logo-text">Plataforma Analítica Territorial</h1>
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
                <div className="copyright">© 2026 Todos los derechos reservados.</div>
                <div className="footer-links">
                  <button
                    onClick={() => alert('Política de Privacidad - Próximamente')}
                    className="link-button"
                  >
                    Política de Privacidad
                  </button>
                  <button
                    onClick={() => alert('Términos de Servicio - Próximamente')}
                    className="link-button"
                  >
                    Términos de Servicio
                  </button>
                </div>
              </div>
            </footer>
    </div>
  );
};


function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<AuthContainer />} />
          <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;