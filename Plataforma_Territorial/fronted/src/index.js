import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import ErrorBoundary from './components/ErrorBoundary';

const root = ReactDOM.createRoot(document.getElementById('root'));
// Global error overlay to show runtime errors directly in the page
function showOverlay(message) {
  let overlay = document.getElementById('error-overlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.id = 'error-overlay';
    Object.assign(overlay.style, {
      position: 'fixed',
      top: '0',
      left: '0',
      right: '0',
      bottom: '0',
      background: 'rgba(0,0,0,0.85)',
      color: '#fff',
      padding: '20px',
      zIndex: 99999,
      overflow: 'auto',
      fontFamily: 'monospace',
      fontSize: '13px',
      lineHeight: '1.4'
    });
    document.body.appendChild(overlay);
  }
  overlay.textContent = message;
}

window.addEventListener('error', (e) => {
  console.error(e.error || e.message || e);
  try { showOverlay(String(e.error?.stack || e.message || e)); } catch (err) { /* ignore */ }
});

window.addEventListener('unhandledrejection', (e) => {
  console.error('Unhandled Rejection', e.reason);
  try { showOverlay('Unhandled Rejection: ' + (e.reason?.stack || e.reason?.message || String(e.reason))); } catch (err) { /* ignore */ }
});
root.render(
  <React.StrictMode>
  <ErrorBoundary>
    <App />
    </ErrorBoundary>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
