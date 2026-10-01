import { useEffect, useState } from "react";
import { api } from "../api/client";
import { ticketColorFor } from "../constants";

const POLL_INTERVAL_MS = 8000;

const STATUS_LABELS = {
  queued: "Queued",
  roasting: "Roasting",
  peeling: "Peeling",
  done: "Done",
};

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

  const halted = data.throughput_mode === "halted";

  return (
    <div className="queue-page">
      <h1>Order Queue</h1>
      <p className="line-status">
        Line status: <strong>{data.throughput_mode}</strong>
      </p>
      {halted && (
        <div className="halted-banner">
          The roasting line is temporarily paused. Orders already placed are safe
          &mdash; we'll resume shortly.
        </div>
      )}
      {/* Browser Notification API wiring (opt-in "notify me when ready") is a
          build-phase feature -- this scaffold only renders the live board. */}
      <div className="queue-board">
        {data.queue.length === 0 && <p>No orders currently in the queue.</p>}
        {data.queue.map((item) => (
          <div
            key={item.sack_id}
            className="queue-block"
            style={{ borderTopColor: ticketColorFor(item.variety_1) }}
          >
            <div className="queue-number">#{item.order_display_number}</div>

            <div className="ticket-tags">
              <span className="ticket-tag" style={{ background: ticketColorFor(item.variety_1) }}>
                {item.variety_1}
              </span>
              {item.variety_2 && (
                <span className="ticket-tag" style={{ background: ticketColorFor(item.variety_2) }}>
                  {item.variety_2}
                </span>
              )}
            </div>

            <div className="queue-detail">
              {item.size === "half_sack" ? "Half sack" : "Full sack"} &mdash; {item.service}
              {item.color_stage ? ` \u2014 ${item.color_stage}` : ""}
            </div>

            <div className="queue-status">{STATUS_LABELS[item.status] || item.status}</div>

            <div className="queue-eta">
              {item.estimated_minutes_remaining === null
                ? "On hold"
                : `~${item.estimated_minutes_remaining} min`}
            </div>

            {item.note && <div className="queue-note">{item.note}</div>}
          </div>
        ))}
      </div>
    </div>
  );
}