import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';

import UserCreatePage from './pages/UserCreatePage';
import ContextInputPage from './pages/ContextInputPage';
import CardRecommendationPage from './pages/CardRecommendationPage';
import CardInterpretationPage from './pages/CardInterpretationPage';
import FeedbackPage from './pages/FeedbackPage';

function App() {
  return (
    <div className="App">
      <Router>
        <header className="App-header">
          <h1>AAC 해석 시스템</h1>
        </header>

        <main className="App-main">
          <Routes>
            <Route path="/" element={<Navigate to="/user/create" replace />} />
            <Route path="/user/create" element={<UserCreatePage />} />
            <Route path="/context/input" element={<ContextInputPage />} />
            <Route path="/cards/recommendation" element={<CardRecommendationPage />} />
            <Route path="/cards/interpretation" element={<CardInterpretationPage />} />
            <Route path="/feedback" element={<FeedbackPage />} />
          </Routes>
        </main>
      </Router>
    </div>
  );
}

export default App;
