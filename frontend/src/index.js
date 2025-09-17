// src/index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// React 애플리케이션 진입점
const root = ReactDOM.createRoot(document.getElementById('root'));

// 개발 모드에서의 성능 최적화를 위해 StrictMode 사용
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
