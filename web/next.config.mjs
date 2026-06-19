import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

/** @type {import('next').NextConfig} */
const nextConfig = {
  // The UI reads pipeline artifacts straight off the filesystem in API routes.
  // Pin the tracing root to this app to avoid multi-lockfile inference.
  outputFileTracingRoot: __dirname,
};

export default nextConfig;
