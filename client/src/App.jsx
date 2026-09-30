import { Routes, Route, Link } from "react-router-dom";

import Login from "./pages/Login";
import PublicQueue from "./pages/PublicQueue";
import Dashboard from "./pages/Dashboard";
import ProtectedRoute from "./components/ProtectedRoute";
import { useAuth } from "./context/AuthContext";

export default function App() {
  const { user } = useAuth();

  return (
    <div className="app">
      <nav>
        <Link to="/">Queue</Link>
        {user ? <Link to="/dashboard">Dashboard</Link> : <Link to="/login">Staff Login</Link>}
      </nav>
      <Routes>
        <Route path="/" element={<PublicQueue />} />
        <Route path="/login" element={<Login />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
      </Routes>
    </div>
  );
}