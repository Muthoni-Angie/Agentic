import type { Metadata } from "next";
import Link from "next/link";

import "./globals.css";

export const metadata: Metadata = {
  title: "Agentic — Autonomous Engineering Pipeline",
  description:
    "A GitHub-native autonomous software engineering framework where specialized agents collaborate through filesystem artifacts.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen">
          <header className="sticky top-0 z-30 border-b border-[var(--color-border)] bg-[var(--color-bg)]/80 backdrop-blur-md">
            <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:px-6">
              <Link href="/" className="flex items-center gap-2.5">
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-[var(--color-brand)] to-[var(--color-reviewer)] text-sm font-bold text-white">
                  A
                </span>
                <div className="leading-tight">
                  <div className="text-sm font-semibold tracking-tight">
                    Agentic
                  </div>
                  <div className="text-[11px] text-[var(--color-faint)]">
                    autonomous engineering pipeline
                  </div>
                </div>
              </Link>
              <nav className="flex items-center gap-1 text-sm">
                <Link
                  href="/"
                  className="rounded-md px-3 py-1.5 text-[var(--color-muted)] transition-colors hover:bg-[var(--color-surface)] hover:text-[var(--color-text)]"
                >
                  Runs
                </Link>
                <a
                  href="https://github.com"
                  className="rounded-md px-3 py-1.5 text-[var(--color-muted)] transition-colors hover:bg-[var(--color-surface)] hover:text-[var(--color-text)]"
                >
                  Docs
                </a>
              </nav>
            </div>
          </header>
          <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6">{children}</main>
        </div>
      </body>
    </html>
  );
}
