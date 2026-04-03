import React, { useState } from 'react';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';

export default function AuthScreen({ onAuthenticated }) {
  const [mode, setMode] = useState('login');

  if (mode === 'register') {
    return (
      <RegisterForm
        onRegistered={onAuthenticated}
        onGoLogin={() => setMode('login')}
      />
    );
  }

  return (
    <LoginForm
      onLoggedIn={onAuthenticated}
      onGoRegister={() => setMode('register')}
    />
  );
}
