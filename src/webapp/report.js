// Summary + Markdown report for a reconciliation result.
window.LedgerLoop = window.LedgerLoop || {};

window.LedgerLoop.summarize = function summarize(rec) {
  const matched = rec.matched.length;
  const ul = rec.unmatchedLeft.length;
  const ur = rec.unmatchedRight.length;
  const total = matched + ul + ur;
  const rate = total === 0 ? 0 : Math.round((matched / total) * 100);
  return { matched, unmatchedLeft: ul, unmatchedRight: ur, rate };
};

window.LedgerLoop.toMarkdown = function toMarkdown(rec) {
  const s = window.LedgerLoop.summarize(rec);
  return [
    "# LedgerLoop Reconciliation Report",
    "",
    "- Matched: " + s.matched,
    "- Unmatched (A): " + s.unmatchedLeft,
    "- Unmatched (B): " + s.unmatchedRight,
    "- Match rate: " + s.rate + "%",
  ].join("\n");
};
