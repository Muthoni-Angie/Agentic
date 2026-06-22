import { FileCode } from "lucide-react";

export function CodeBlock({
  path,
  content,
}: {
  path: string;
  content: string;
}) {
  const lines = content.replace(/\n$/, "").split("\n");
  return (
    <div className="overflow-hidden rounded-xl border border-[var(--color-border)] bg-[#0c0e14]">
      <div className="flex items-center gap-2 border-b border-[var(--color-border)] bg-[var(--color-surface-2)] px-3 py-2">
        <FileCode size={13} className="text-[var(--color-faint)]" />
        <span className="font-mono text-xs text-[var(--color-muted)]">
          {path}
        </span>
      </div>
      <div className="overflow-x-auto">
        <pre className="min-w-full py-3 text-[12.5px] leading-relaxed">
          <code className="block font-mono">
            {lines.map((line, i) => (
              <span key={i} className="flex">
                <span className="w-10 shrink-0 select-none pr-3 text-right text-[var(--color-faint)]/60">
                  {i + 1}
                </span>
                <span className="whitespace-pre pr-4 text-[#c4cad8]">
                  {line || " "}
                </span>
              </span>
            ))}
          </code>
        </pre>
      </div>
    </div>
  );
}
