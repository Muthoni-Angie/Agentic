import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

/** @type {import('next').NextConfig} */
const nextConfig = {
  // The UI reads pipeline artifacts straight off the filesystem in API routes.
  // Pin the tracing root to this app to avoid multi-lockfile inference.
  outputFileTracingRoot: __dirname,
  // Bundle the snapshotted pipeline runs into the server functions / pages that
  // read them, so the deployed site can serve runs (they live outside the
  // default trace otherwise).
  outputFileTracingIncludes: {
    "/": ["./.pipeline/**"],
    "/runs/[runId]": ["./.pipeline/**"],
    "/api/runs": ["./.pipeline/**"],
    "/api/runs/[runId]": ["./.pipeline/**"],
  },
};

export default nextConfig;
