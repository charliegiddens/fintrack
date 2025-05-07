import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';

import HomePage from './pages/HomePage';
import DashboardPage from './pages/DashboardPage';

import LoginButton from './components/LoginButton';
import LogoutButton from './components/LogoutButton';
import ProtectedRoute from './components/ProtectedRoute';

import './App.css'; 

function App() {
  const { isAuthenticated, isLoading, error } = useAuth0();

  if (isLoading) {
    return <div className="app-loading">Loading Application...</div>;
  }

  if (error) {
    return <div className="app-error">Oops... {error.message}</div>;
  }

  return (
    <Router>
      <div className="app-container">
        <nav className="app-nav">
          <Link to="/" className="nav-link">Home</Link>
          {isAuthenticated && (
            <Link to="/dashboard" className="nav-link">Dashboard</Link>
          )}
          {/* Example for later:
          {isAuthenticated && (
            <Link to="/expenses" className="nav-link">Expenses</Link>
          )}
          */}
          <div className="auth-buttons">
            {!isAuthenticated ? <LoginButton /> : <LogoutButton />}
          </div>
        </nav>

        <main className="app-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route
              path="/dashboard"
              element={<ProtectedRoute component={DashboardPage} />}
            />
            {/* Example for later:
            <Route
              path="/expenses"
              element={<ProtectedRoute component={ExpensesPage} />}
            />
            */}
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;