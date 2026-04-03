import React, { useState, useCallback } from 'react';
import FileUploadModern from './components/FileUploadModern';
import AuthScreen from './components/auth/AuthScreen';
import { api } from './services/api';

function App() {
  const [hasSession, setHasSession] = useState(
    () => !!localStorage.getItem('token')
  );

  const handleLogout = useCallback(() => {
    api.logout();
    setHasSession(false);
  }, []);

  if (!hasSession) {
    return <AuthScreen onAuthenticated={() => setHasSession(true)} />;
  }

  return <FileUploadModern onLogout={handleLogout} />;
}

export default App;
