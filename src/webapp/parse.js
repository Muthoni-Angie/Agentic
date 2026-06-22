// CSV parsing for LedgerLoop.
window.LedgerLoop = window.LedgerLoop || {};

window.LedgerLoop.parseCsv = function parseCsv(text) {
  const lines = String(text || "").trim().split(/\r?\n/).filter(Boolean);
  if (lines.length === 0) return [];
  const header = lines[0].split(",").map((h) => h.trim().toLowerCase());
  const idx = { id: header.indexOf("id"), amount: header.indexOf("amount"), date: header.indexOf("date") };
  const rows = [];
  for (let i = 1; i < lines.length; i++) {
    const cells = lines[i].split(",");
    const id = (cells[idx.id] || "").trim();
    if (!id) continue;
    rows.push({
      id,
      amount: parseInt((cells[idx.amount] || "0").trim(), 10) || 0,
      date: (cells[idx.date] || "").trim(),
    });
  }
  return rows;
};
