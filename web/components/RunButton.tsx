"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Play, Loader2, Check, AlertCircle } from "lucide-react";

type State = "idle" | "loading" | "done" | "error";

export function RunButton() {
  const router = useRouter();
  const [state, setState] = useState<State>("idle");
  const [msg, setMsg] = useState("");

  async function trigger() {
    setState("loading");
    setMsg("");
    try {
      const res = await fetch("/api/run", { method: "POST" });
      const data = await res.json();
      if (res.ok && data.ok) {
        setState("done");
        setMsg(data.message ?? "Run triggered.");
        // Refresh the runs list shortly after; the PR/run appears async.
        setTimeout(() => router.refresh(), 4000);
      } else {
        setState("error");
        setMsg(String(data.error ?? "Failed to trigger run.").slice(0, 160));
      }
    } catch {
      setState("error");
      setMsg("Network error — could not reach the server.");
    }
    if (state !== "error") {
      setTimeout(() => setState((s) => (s === "loading" ? s : "idle")), 6000);
    }
  }

  const icon = {
    idle: <Play size={15} />,
    loading: <Loader2 size={15} className="animate-spin" />,
    done: <Check size={15} />,
    error: <AlertCircle size={15} />,
  }[state];

  return (
    <div className="flex flex-col items-start gap-1.5 sm:items-end">
      <button
        onClick={trigger}
        disabled={state === "loading"}
        className="inline-flex items-center gap-2 rounded-xl bg-[var(--color-brand)] px-4 py-2 text-sm font-semibold text-white shadow-sm transition-all hover:brightness-110 disabled:opacity-60"
      >
        {icon}
        {state === "loading" ? "Triggering…" : "Run pipeline"}
      </button>
      {msg && (
        <p
          className="max-w-xs text-right text-xs"
          style={{
            color:
              state === "error" ? "var(--color-danger)" : "var(--color-muted)",
          }}
        >
          {msg}
        </p>
      )}
    </div>
  );
}
