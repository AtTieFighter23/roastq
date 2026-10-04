import { useState } from "react";
import { api } from "../api/client";

export default function QueueControls({ onChange }) {
  const [delayMinutes, setDelayMinutes] = useState("");
  const [delayError, setDelayError] = useState("");
  const [delayMessage, setDelayMessage] = useState("");
  const [note, setNote] = useState("");
  const [noteError, setNoteError] = useState("");
  const [noteMessage, setNoteMessage] = useState("");

  async function handleDelaySubmit(e) {
    e.preventDefault();
    setDelayError("");
    setDelayMessage("");
    try {
      const result = await api.post("/queue/delay", { minutes: Number(delayMinutes) });
      setDelayMessage(result.message);
      setDelayMinutes("");
      onChange();
    } catch (err) {
      setDelayError(err.message);
    }
  }

  async function handleNoteSubmit(e) {
    e.preventDefault();
    setNoteError("");
    setNoteMessage("");
    try {
      const result = await api.post("/queue/note", { note });
      setNoteMessage(result.message);
      onChange();
    } catch (err) {
      setNoteError(err.message);
    }
  }

  return (
    <div className="queue-controls">
      <h2>Queue Adjustments</h2>
      <form onSubmit={handleDelaySubmit} className="inline-form">
        <label>
          Delay (minutes)
          <input type="number" value={delayMinutes} onChange={(e) => setDelayMinutes(e.target.value)} />
        </label>
        <button type="submit">Set Delay</button>
        {delayError && <p className="error">{delayError}</p>}
        {delayMessage && <p className="success">{delayMessage}</p>}
      </form>
      <form onSubmit={handleNoteSubmit} className="inline-form">
        <label>
          Customer-visible note
          <input type="text" value={note} onChange={(e) => setNote(e.target.value)} />
        </label>
        <button type="submit">Set Note</button>
        {noteError && <p className="error">{noteError}</p>}
        {noteMessage && <p className="success">{noteMessage}</p>}
      </form>
    </div>
  );
}
