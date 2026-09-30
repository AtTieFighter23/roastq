import { useEffect, useState } from "react";
import { api } from "../api/client";

const POLL_INTERVAL_MS = 8000;

export default function PublicQueue() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let isMounted = true;

    async function fetchQueue() {
      try {
        const result = await api.get("/queue");
        if (isMounted) setData(result);
      } catch (err) {
        if (isMounted) setError(err.message);
      }
    }

    fetchQueue();
    const interval = setInterval(fetchQueue, POLL_INTERVAL_MS);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  if (error) return <p className="error">{error}</p>;
  if (!data) return <p>Loading queue...</p>;

  return (
    <div className="queue-page">
      <h1>Order Queue</h1>
      <p>
        Line status: <strong>{data.throughput_mode}</strong>
      </p>
      {/* Browser Notification API wiring (opt-in "notify me when ready") is a
          build-phase feature -- this scaffold only renders the live board. */}
      <div className="queue-board">
        {data.queue.length === 0 && <p>No orders currently in the queue.</p>}
        {data.queue.map((item) => (
          <div key={item.sack_id} className="queue-block">
            <div className="queue-number">#{item.order_display_number}</div>
            <div className="queue-detail">
              {item.size} &mdash; {item.service} &mdash; {item.variety_1}
              {item.variety_2 ? ` / ${item.variety_2}` : ""}
            </div>
            <div className="queue-eta">
              {item.estimated_minutes_remaining === null
                ? "On hold"
                : `~${item.estimated_minutes_remaining} min`}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
