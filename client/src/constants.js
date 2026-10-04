// Ticket colors are tied to variety (heat level), not to color_stage
// (ripeness). Each variety has one fixed, real-world ticket color used on
// the physical paper tickets -- this mirrors that on the digital board.
// NOTE: these keys are the exact values the backend accepts
// (VALID_VARIETIES in models/sack_item.py), NOT display-friendly names --
// "NM64" and "BigJim", not "NM-64" or "Big Jim".
export const TICKET_COLORS = {
  NM64: { color: "#3f8f3f", heat: "Mild", label: "NM-64" },
  BigJim: { color: "#d9a520", heat: "Medium", label: "Big Jim" },
  Sandia: { color: "#d2691e", heat: "Hot", label: "Sandia" },
  DoubleCross: { color: "#2c5f7c", heat: "Hot", label: "DoubleCross" },
  Lumbre: { color: "#b5342a", heat: "Extra Hot", label: "Lumbre" },
};

export function ticketColorFor(variety) {
  return TICKET_COLORS[variety]?.color || "#999999";
}

export const VARIETY_OPTIONS = Object.entries(TICKET_COLORS).map(([value, meta]) => ({
  value,
  label: `${meta.label} (${meta.heat})`,
}));

export const SIZE_OPTIONS = [
  { value: "sack", label: "Full sack" },
  { value: "half_sack", label: "Half sack" },
];

export const SERVICE_OPTIONS = [
  { value: "fresh", label: "Fresh (unroasted)" },
  { value: "roast_only", label: "Roast only" },
  { value: "cooled", label: "Roast + cooled" },
];

export const COLOR_STAGE_OPTIONS = [
  { value: "green", label: "Green" },
  { value: "red", label: "Red" },
];