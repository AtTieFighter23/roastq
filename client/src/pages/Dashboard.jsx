import { useAuth } from "../context/AuthContext";

export default function Dashboard() {
  const { user, logout } = useAuth();

  return (
    <div className="dashboard">
      <h1>
        Welcome, {user.username} ({user.role})
      </h1>
      <p>
        Scaffold placeholder &mdash; order entry, queue controls, and
        {user.role === "manager" ? " manager tools (reorder, throughput mode, inventory/history)" : " status controls"}{" "}
        get built out here next.
      </p>
      <button onClick={logout}>Log Out</button>
    </div>
  );
}
