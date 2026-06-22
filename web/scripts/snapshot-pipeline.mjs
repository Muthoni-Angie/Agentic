// Build-time snapshot: copy artifacts from the repo root into web/ so the
// deployed functions can read them. On Vercel the project root is web/, so
// anything outside it is not bundled. We snapshot:
//   ../.pipeline   -> web/.pipeline        (agent runs)
//   ../src         -> web/product-src      (the product the agents build)
//   ../roadmap.json-> web/roadmap.json     (backlog progress)
import fs from "node:fs";
import path from "node:path";

function snapshotDir(rel, destName) {
  const src = path.join(process.cwd(), "..", rel);
  const dest = path.join(process.cwd(), destName);
  if (fs.existsSync(src)) {
    fs.rmSync(dest, { recursive: true, force: true });
    fs.cpSync(src, dest, { recursive: true });
    console.log(`[snapshot] ${rel} -> ${destName}`);
  } else {
    console.log(`[snapshot] no ${rel}; skipping`);
  }
}

function snapshotFile(rel, destName) {
  const src = path.join(process.cwd(), "..", rel);
  const dest = path.join(process.cwd(), destName);
  if (fs.existsSync(src)) {
    fs.copyFileSync(src, dest);
    console.log(`[snapshot] ${rel} -> ${destName}`);
  } else {
    console.log(`[snapshot] no ${rel}; skipping`);
  }
}

try {
  snapshotDir(".pipeline", ".pipeline");
  snapshotDir("src", "product-src");
  snapshotFile("roadmap.json", "roadmap.json");
} catch (err) {
  // Never fail the build over the snapshot.
  console.warn("[snapshot] skipped:", err?.message ?? err);
}
