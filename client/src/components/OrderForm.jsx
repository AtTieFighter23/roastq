import { useState } from "react";
import { api } from "../api/client";
import {
  VARIETY_OPTIONS,
  SIZE_OPTIONS,
  SERVICE_OPTIONS,
  COLOR_STAGE_OPTIONS,
} from "../constants";

const emptySackDraft = {
  size: "sack",
  service: "fresh",
  color_stage: "green",
  variety_1: "Sandia",
  variety_2: "",
  addon_note: "",
};

export default function OrderForm({ onOrderCreated }) {
  const [customerName, setCustomerName] = useState("");
  const [contactInfo, setContactInfo] = useState("");
  const [sackItems, setSackItems] = useState([]);
  const [draft, setDraft] = useState(emptySackDraft);
  const [draftError, setDraftError] = useState("");
  const [submitError, setSubmitError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function updateDraft(field, value) {
    setDraft((prev) => ({ ...prev, [field]: value }));
    setDraftError("");
  }

  function addSackToOrder() {
    // Mirrors the server's authoritative mixing rule (schemas.py) so staff
    // get instant feedback -- the server still re-validates on submit, this
    // is a convenience check only, not the source of truth.
    if (draft.variety_2) {
      if (draft.size === "half_sack") {
        setDraftError("Half sacks cannot be mixed.");
        return;
      }
      if (draft.variety_2 === draft.variety_1) {
        setDraftError("The second variety must differ from the first.");
        return;
      }
    }

    setSackItems((prev) => [...prev, draft]);
    setDraft(emptySackDraft);
    setDraftError("");
  }

  function removeSackItem(index) {
    setSackItems((prev) => prev.filter((_, i) => i !== index));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitError("");
    setSuccessMessage("");

    if (sackItems.length === 0) {
      setSubmitError("Add at least one sack to the order before submitting.");
      return;
    }

    setSubmitting(true);
    try {
      const order = await api.post("/orders", {
        customer_name: customerName || null,
        contact_info: contactInfo || null,
        sack_items: sackItems.map((item) => ({
          ...item,
          variety_2: item.variety_2 || undefined,
          addon_note: item.addon_note || undefined,
        })),
      });
      setSuccessMessage(`Order #${order.display_number} created.`);
      setCustomerName("");
      setContactInfo("");
      setSackItems([]);
      if (onOrderCreated) onOrderCreated(order);
    } catch (err) {
      setSubmitError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="order-form">
      <h2>New Order</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Customer name (optional)
          <input value={customerName} onChange={(e) => setCustomerName(e.target.value)} />
        </label>
        <label>
          Contact info (optional)
          <input value={contactInfo} onChange={(e) => setContactInfo(e.target.value)} />
        </label>

        <fieldset className="sack-builder">
          <legend>Add a sack</legend>

          <label>
            Size
            <select value={draft.size} onChange={(e) => updateDraft("size", e.target.value)}>
              {SIZE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </label>

          <label>
            Service
            <select value={draft.service} onChange={(e) => updateDraft("service", e.target.value)}>
              {SERVICE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </label>

          <label>
            Color stage
            <select value={draft.color_stage} onChange={(e) => updateDraft("color_stage", e.target.value)}>
              {COLOR_STAGE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </label>

          <label>
            Variety
            <select value={draft.variety_1} onChange={(e) => updateDraft("variety_1", e.target.value)}>
              {VARIETY_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </label>

          <label>
            Mix with a second variety (full sacks only, optional)
            <select value={draft.variety_2} onChange={(e) => updateDraft("variety_2", e.target.value)}>
              <option value="">-- none --</option>
              {VARIETY_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </label>

          <label>
            Add-on note (optional)
            <input
              value={draft.addon_note}
              onChange={(e) => updateDraft("addon_note", e.target.value)}
              placeholder="e.g. extra jalapenos"
            />
          </label>

          {draftError && <p className="error">{draftError}</p>}
          <button type="button" onClick={addSackToOrder}>Add Sack to Order</button>
        </fieldset>

        {sackItems.length > 0 && (
          <ul className="sack-list">
            {sackItems.map((item, index) => (
              <li key={index}>
                {item.size === "half_sack" ? "Half sack" : "Full sack"} &mdash; {item.service} &mdash;{" "}
                {item.variety_1}
                {item.variety_2 ? ` / ${item.variety_2}` : ""}
                <button type="button" onClick={() => removeSackItem(index)}>Remove</button>
              </li>
            ))}
          </ul>
        )}

        {submitError && <p className="error">{submitError}</p>}
        {successMessage && <p className="success">{successMessage}</p>}

        <button type="submit" disabled={submitting}>
          {submitting ? "Submitting..." : "Create Order"}
        </button>
      </form>
    </div>
  );
}