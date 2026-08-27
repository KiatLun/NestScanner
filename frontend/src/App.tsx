import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './App.css';

import DashboardPage from './pages/DashboardPage';


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;