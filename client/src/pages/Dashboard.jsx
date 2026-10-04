import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../api/client";
import OrderForm from "../components/OrderForm";
import QueueControls from "../components/QueueControls";
import ManagerControls from "../components/ManagerControls";

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [orders, setOrders] = useState([]);
  const [loadError, setLoadError] = useState("");

  async function loadOrders() {
    try {
      const result = await api.get("/orders");
      setOrders(result);
    } catch (err) {
      setLoadError(err.message);
    }
  }

  useEffect(() => {
    loadOrders();
  }, []);

  return (
    <div className="dashboard">
      <h1>
        Welcome, {user.username} ({user.role})
      </h1>
      <button onClick={logout}>Log Out</button>

      <OrderForm onOrderCreated={loadOrders} />

      <QueueControls orders={orders} onChange={loadOrders} />

      {user.role === "manager" && (
        <ManagerControls orders={orders} onChange={loadOrders} />
      )}

      <h2>Today's Orders</h2>
      {loadError && <p className="error">{loadError}</p>}
      {orders.length === 0 && <p>No orders yet today.</p>}
      <ul className="order-list">
        {orders.map((order) => (
          <li key={order.id}>
            #{order.display_number} &mdash; {order.customer_name || "Walk-in"} &mdash; {order.status}
            <ul>
              {order.sack_items.map((item) => (
                <li key={item.id}>
                  {item.size} / {item.service} / {item.variety_1}
                  {item.variety_2 ? ` + ${item.variety_2}` : ""} &mdash; {item.sack_status}
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
    </div>
  );
}