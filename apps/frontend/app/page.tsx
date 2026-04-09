import Link from "next/link";

import { StatusBadge } from "@/components/status-badge";
import { teamRunbook } from "@/lib/runbook";

const telemetryEvents = [
  "Run started",
  "Role stage started",
  "Role stage completed",
  "Frontend delivery generated",
  "Run completed or failed"
] as const;

export default function HomePage() {
  return (
    <main className="min-h-screen px-6 py-8 text-ink sm:px-10">
      <div className="mx-auto max-w-6xl">
        <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="rounded-[36px] bg-slate-950 px-8 py-10 text-white shadow-soft">
            <StatusBadge label="CrewAI command center" tone="accent" />
            <h1 className="mt-5 max-w-3xl text-4xl font-semibold leading-tight sm:text-6xl">
              IT department orchestration with production frontend delivery.
            </h1>
            <p className="mt-6 max-w-2xl text-base leading-7 text-slate-200">
              This workspace couples a CrewAI manager flow, role-specific Ollama models, a Telegram
              notifier, and a Next.js production target that the frontend stage can update directly.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                href="/generated"
                className="rounded-full bg-amber-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-amber-200"
              >
                Open generated delivery
              </Link>
              <a
                href="https://github.com/joaomdmoura/crewai"
                className="rounded-full border border-white/20 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/10"
              >
                CrewAI reference
              </a>
            </div>
          </div>

          <div className="grid gap-6">
            <section className="rounded-[32px] border border-black/10 bg-white/80 p-6 backdrop-blur">
              <p className="text-sm font-semibold uppercase tracking-[0.16em] text-slate-500">
                Progress telemetry
              </p>
              <div className="mt-5 grid gap-3">
                {telemetryEvents.map((event) => (
                  <div key={event} className="rounded-2xl bg-slate-100 px-4 py-4 text-sm text-slate-700">
                    {event}
                  </div>
                ))}
              </div>
            </section>

            <section className="rounded-[32px] border border-black/10 bg-white p-6">
              <p className="text-sm font-semibold uppercase tracking-[0.16em] text-slate-500">
                Delivery policy
              </p>
              <p className="mt-4 text-sm leading-7 text-slate-700">
                Keep generated production pages under <code>app/generated</code> or extract shared
                components under <code>components/</code> once stable.
              </p>
            </section>
          </div>
        </section>

        <section className="mt-8 rounded-[36px] border border-black/10 bg-white p-8 shadow-soft">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.16em] text-slate-500">
                Role ownership
              </p>
              <h2 className="mt-2 text-3xl font-semibold text-slate-950">Team runbook</h2>
            </div>
            <StatusBadge label="Monorepo scaffold" />
          </div>
          <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-5">
            {teamRunbook.map((item) => (
              <article key={item.role} className="rounded-[28px] bg-slate-50 p-5">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
                  {item.role}
                </p>
                <p className="mt-3 text-sm leading-7 text-slate-700">{item.responsibility}</p>
              </article>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
