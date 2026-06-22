import Link from "next/link";
import { ChevronLeft, Check, Hammer, Circle, Package } from "lucide-react";

import { getProductState } from "@/lib/product";
import { CodeBlock } from "@/components/CodeBlock";

export const dynamic = "force-dynamic";

export default async function ProductPage() {
  const product = await getProductState();
  const pct = Math.round((product.doneCount / product.total) * 100);

  return (
    <div className="flex flex-col gap-6">
      <Link
        href="/"
        className="inline-flex w-fit items-center gap-1 text-sm text-[var(--color-muted)] transition-colors hover:text-[var(--color-text)]"
      >
        <ChevronLeft size={15} />
        Dashboard
      </Link>

      {/* Header */}
      <section className="flex flex-col gap-3">
        <div className="flex items-center gap-2.5">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-[var(--color-coder)]/15 text-[var(--color-coder)]">
            <Package size={18} />
          </span>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">
              {product.name}
            </h1>
            <p className="text-xs text-[var(--color-faint)]">
              the product the agents are building
            </p>
          </div>
        </div>
        <p className="max-w-2xl text-sm leading-relaxed text-[var(--color-muted)]">
          {product.pitch}
        </p>

        <a
          href="https://ledgerloop-seven.vercel.app"
          target="_blank"
          rel="noreferrer"
          className="inline-flex w-fit items-center gap-2 rounded-xl bg-[var(--color-coder)] px-4 py-2 text-sm font-semibold text-[#06281d] transition-all hover:brightness-110"
        >
          Open the live app ↗
        </a>
        {product.doneCount < product.total && (
          <span className="text-xs text-[var(--color-faint)]">
            The live app updates as the agents ship the remaining features.
          </span>
        )}

        {/* Progress */}
        <div className="mt-1 flex flex-col gap-1.5">
          <div className="flex items-center justify-between text-xs">
            <span className="font-medium text-[var(--color-muted)]">
              {product.doneCount} of {product.total} features shipped
            </span>
            <span className="text-[var(--color-faint)]">{pct}%</span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-[var(--color-surface-2)]">
            <div
              className="h-full rounded-full bg-gradient-to-r from-[var(--color-coder)] to-[var(--color-brand)] transition-all"
              style={{ width: `${pct}%` }}
            />
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="flex flex-col gap-4">
        {product.features.map((f) => {
          const state = f.done ? "done" : f.building ? "building" : "todo";
          const color =
            state === "done"
              ? "var(--color-ok)"
              : state === "building"
                ? "var(--color-tester)"
                : "var(--color-faint)";
          return (
            <div
              key={f.id}
              className="rounded-[var(--radius)] border border-[var(--color-border)] bg-[var(--color-surface)] p-4 sm:p-5"
              style={state === "building" ? { borderColor: color } : undefined}
            >
              <div className="flex items-start gap-3">
                <span style={{ color }} className="mt-0.5">
                  {state === "done" ? (
                    <Check size={18} />
                  ) : state === "building" ? (
                    <Hammer size={18} />
                  ) : (
                    <Circle size={18} />
                  )}
                </span>
                <div className="flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-mono text-xs text-[var(--color-faint)]">
                      {f.id}
                    </span>
                    <h2 className="text-sm font-semibold">{f.title}</h2>
                    <span
                      className="rounded-full px-2 py-0.5 text-[10px] font-medium"
                      style={{ backgroundColor: `${color}22`, color }}
                    >
                      {state === "done"
                        ? "shipped"
                        : state === "building"
                          ? "up next"
                          : "planned"}
                    </span>
                  </div>
                  <p className="mt-0.5 text-xs text-[var(--color-muted)]">
                    {f.summary}
                  </p>
                </div>
              </div>

              {/* Built source for shipped features */}
              {f.sources.length > 0 && (
                <div className="mt-4 flex flex-col gap-3">
                  {f.sources.map((s) => (
                    <CodeBlock key={s.path} path={s.path} content={s.content} />
                  ))}
                </div>
              )}
              {f.sources.length === 0 && !f.done && (
                <p className="mt-3 pl-7 text-xs italic text-[var(--color-faint)]">
                  Not built yet — run the pipeline to ship this feature.
                </p>
              )}
            </div>
          );
        })}
      </section>
    </div>
  );
}
