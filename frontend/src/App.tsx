import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './App.css';

import DashboardPage from './pages/DashboardPage';
import HistoryPage from './pages/HistoryPage';
import ModelDetailsPage from './pages/ModelDetailsPage'


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/models/:modelId" element={<ModelDetailsPage/>} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;