import { useState } from "react";
import { api } from "../api/client";

const MODE_OPTIONS = ["normal", "degraded", "halted"];

export default function ManagerControls({ orders, onChange }) {
  const [mode, setMode] = useState("normal");
  const [modeError, setModeError] = useState("");
  const [modeMessage, setModeMessage] = useState("");
  const [movingOrderId, setMovingOrderId] = useState("");
  const [afterOrderId, setAfterOrderId] = useState("");
  const [reorderError, setReorderError] = useState("");
  const [reorderMessage, setReorderMessage] = useState("");

  const activeOrders = orders.filter((o) => o.status !== "done");

  async function handleModeSubmit(e) {
    e.preventDefault();
    setModeError("");
    setModeMessage("");
    try {
      const result = await api.post("/queue/mode", { mode });
      setModeMessage(result.message);
      onChange();
    } catch (err) {
      setModeError(err.message);
    }
  }

  async function handleReorderSubmit(e) {
    e.preventDefault();
    setReorderError("");
    setReorderMessage("");
    if (!movingOrderId) {
      setReorderError("Pick an order to move.");
      return;
    }
    try {
      const result = await api.post("/queue/reorder", {
        moving_order_id: Number(movingOrderId),
        after_order_id: afterOrderId ? Number(afterOrderId) : null,
      });
      setReorderMessage(result.message);
      setMovingOrderId("");
      setAfterOrderId("");
      onChange();
    } catch (err) {
      setReorderError(err.message);
    }
  }

  return (
    <div className="manager-controls">
      <h2>Manager Tools</h2>
      <form onSubmit={handleModeSubmit} className="inline-form">
        <label>
          Throughput mode
          <select value={mode} onChange={(e) => setMode(e.target.value)}>
            {MODE_OPTIONS.map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </label>
        <button type="submit">Set Mode</button>
        {modeError && <p className="error">{modeError}</p>}
        {modeMessage && <p className="success">{modeMessage}</p>}
      </form>
      <form onSubmit={handleReorderSubmit} className="inline-form">
        <label>
          Move order
          <select value={movingOrderId} onChange={(e) => setMovingOrderId(e.target.value)}>
            <option value="">-- select --</option>
            {activeOrders.map((o) => (
              <option key={o.id} value={o.id}>#{o.display_number} ({o.customer_name || "Walk-in"})</option>
            ))}
          </select>
        </label>
        <label>
          Place after
          <select value={afterOrderId} onChange={(e) => setAfterOrderId(e.target.value)}>
            <option value="">-- front of line --</option>
            {activeOrders.map((o) => (
              <option key={o.id} value={o.id}>#{o.display_number} ({o.customer_name || "Walk-in"})</option>
            ))}
          </select>
        </label>
        <button type="submit">Reorder</button>
        {reorderError && <p className="error">{reorderError}</p>}
        {reorderMessage && <p className="success">{reorderMessage}</p>}
      </form>
    </div>
  );
}
