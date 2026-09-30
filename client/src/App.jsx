import { Routes, Route, Link } from "react-router-dom";

import Login from "./pages/Login";
import PublicQueue from "./pages/PublicQueue";
import Dashboard from "./pages/Dashboard";
import ProtectedRoute from "./components/ProtectedRoute";

export default function App() {
  return (
    <div className="app">
      <nav>
        <Link to="/">Queue</Link>
        <Link to="/login">Staff Login</Link>
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
