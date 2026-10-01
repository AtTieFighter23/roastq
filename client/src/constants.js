// Ticket colors are tied to variety (heat level), not to color_stage
// (ripeness). Each variety has one fixed, real-world ticket color used on
// the physical paper tickets -- this mirrors that on the digital board.
export const TICKET_COLORS = {
  "NM-64": { color: "#3f8f3f", heat: "Mild" },
  "Big Jim": { color: "#d9a520", heat: "Medium" },
  "Sandia": { color: "#d2691e", heat: "Hot" },
  "DoubleCross": { color: "#2c5f7c", heat: "Hot" },
  "Lumbre": { color: "#b5342a", heat: "Extra Hot" },
};

export function ticketColorFor(variety) {
  return TICKET_COLORS[variety]?.color || "#999999";
}

export function heatLabelFor(variety) {
  return TICKET_COLORS[variety]?.heat || "";
}