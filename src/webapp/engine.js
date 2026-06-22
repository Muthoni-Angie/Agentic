// Matching engine for LedgerLoop (mirrors the Python core).
window.LedgerLoop = window.LedgerLoop || {};

window.LedgerLoop.reconcile = function reconcile(left, right) {
  const matched = [];
  const unmatchedLeft = [];
  const remaining = right.slice();
  for (const tx of left) {
    const j = remaining.findIndex((r) => r.amount === tx.amount && r.date === tx.date);
    if (j >= 0) {
      matched.push([tx.id, remaining[j].id]);
      remaining.splice(j, 1);
    } else {
      unmatchedLeft.push(tx.id);
    }
  }
  return { matched, unmatchedLeft, unmatchedRight: remaining.map((r) => r.id) };
};
