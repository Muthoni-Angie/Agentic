import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center gap-4 py-24 text-center">
      <h1 className="text-3xl font-bold">Run not found</h1>
      <p className="text-sm text-[var(--color-muted)]">
        That pipeline run does not exist in <code>.pipeline/</code>.
      </p>
      <Link
        href="/"
        className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] px-4 py-2 text-sm transition-colors hover:bg-[var(--color-surface-2)]"
      >
        ← Back to runs
      </Link>
    </div>
  );
}
