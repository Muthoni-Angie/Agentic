// Wire the UI: parse -> reconcile -> render summary + tables + export.
(function () {
  const LL = window.LedgerLoop;
  const $ = (id) => document.getElementById(id);
  let lastRec = null;

  function table(title, rows, headers) {
    const head = headers.map((h) => "<th>" + h + "</th>").join("");
    const body = rows.length
      ? rows.map((r) => "<tr>" + r.map((c) => "<td>" + c + "</td>").join("") + "</tr>").join("")
      : '<tr><td colspan="' + headers.length + '" style="color:var(--faint)">none</td></tr>';
    return (
      '<div class="result-block"><h3>' + title + " (" + rows.length + ")</h3>" +
      "<table><thead><tr>" + head + "</tr></thead><tbody>" + body + "</tbody></table></div>"
    );
  }

  function render(rec) {
    const s = LL.summarize(rec);
    $("summary").innerHTML = [
      ['<div class="card"><div class="value">' + s.matched + '</div><div class="label">Matched</div></div>'],
      ['<div class="card"><div class="value">' + s.unmatchedLeft + '</div><div class="label">Unmatched A</div></div>'],
      ['<div class="card"><div class="value">' + s.unmatchedRight + '</div><div class="label">Unmatched B</div></div>'],
      ['<div class="card"><div class="value">' + s.rate + '%</div><div class="label">Match rate</div></div>'],
    ].join("");
    $("results").innerHTML =
      table("Matched pairs", rec.matched.map((m) => [m[0], m[1]]), ["Source A", "Source B"]) +
      table("Unmatched in A", rec.unmatchedLeft.map((x) => [x]), ["id"]) +
      table("Unmatched in B", rec.unmatchedRight.map((x) => [x]), ["id"]);
    $("summary").hidden = false;
    $("results").hidden = false;
    $("empty").hidden = true;
    $("export").hidden = false;
  }

  function run() {
    $("error").hidden = true;
    try {
      const a = LL.parseCsv($("source-a").value);
      const b = LL.parseCsv($("source-b").value);
      if (a.length === 0 && b.length === 0) {
        $("error").textContent = "Please enter CSV data in at least one source.";
        $("error").hidden = false;
        return;
      }
      lastRec = LL.reconcile(a, b);
      render(lastRec);
    } catch (e) {
      $("error").textContent = "Could not reconcile: " + e.message;
      $("error").hidden = false;
    }
  }

  $("reconcile").addEventListener("click", run);
  $("load-sample").addEventListener("click", function () {
    $("source-a").value = LL.SAMPLE_A;
    $("source-b").value = LL.SAMPLE_B;
    run();
  });
  $("clear").addEventListener("click", function () {
    $("source-a").value = "";
    $("source-b").value = "";
    $("summary").hidden = true;
    $("results").hidden = true;
    $("export").hidden = true;
    $("empty").hidden = false;
  });
  $("export").addEventListener("click", function () {
    if (!lastRec) return;
    const blob = new Blob([LL.toMarkdown(lastRec)], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "reconciliation-report.md";
    a.click();
    URL.revokeObjectURL(url);
  });
})();
