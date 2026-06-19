// Build-time snapshot: copy the committed pipeline runs from the repo root
// (../.pipeline) into web/.pipeline so the deployed functions can read them.
// On Vercel the project root is web/, so anything outside it is not bundled.
import fs from "node:fs";
import path from "node:path";

const src = path.join(process.cwd(), "..", ".pipeline");
const dest = path.join(process.cwd(), ".pipeline");

try {
  if (fs.existsSync(src)) {
    fs.rmSync(dest, { recursive: true, force: true });
    fs.cpSync(src, dest, { recursive: true });
    const runs = fs
      .readdirSync(dest, { withFileTypes: true })
      .filter((d) => d.isDirectory()).length;
    console.log(`[snapshot] copied ${runs} pipeline run(s) -> ${dest}`);
  } else {
    console.log(`[snapshot] no ${src} found; deployed site will start empty`);
  }
} catch (err) {
  // Never fail the build over the snapshot.
  console.warn("[snapshot] skipped:", err?.message ?? err);
}
