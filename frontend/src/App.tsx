import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './App.css';

import DashboardPage from './pages/DashboardPage';
import HistoryPage from './pages/HistoryPage';


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/history" element={<HistoryPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;