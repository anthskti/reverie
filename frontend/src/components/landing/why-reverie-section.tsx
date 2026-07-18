"use client";

import type { ReactNode } from "react";
import { useCounter } from "@/components/motion/use-counter";
import { Reveal } from "@/components/motion/reveal";
import { cn } from "@/lib/utils";

type Reason = {
  value: number;
  suffix?: string;
  prefix?: string;
  decimals?: number;
  title: string;
  description: string | ReactNode;
};

const reasons: Reason[] = [
  {
    value: 92,
    suffix: "M",
    title: <a
        href="https://earth.org/how-repairing-clothes-slows-down-climate-change/"
        target="_blank"
        rel="noreferrer"
        className="text-primary underline"
      >"Tons of textile waste every year"</a>,
    description: (

        "Fashion churns out mountains of discarded clothes. Reverie gives garments a second life instead of a landfill trip."
    ),
  },
  {
    value: 2700,
    suffix: "L",
    title:<a
        href="https://www.europarl.europa.eu/topics/en/article/20201208STO93327/fast-fashion-eu-laws-for-sustainable-textile-consumption"
        target="_blank"
        rel="noreferrer"
        className="text-primary underline"
      >Of water for one cotton tee</a>,
    description:
      "Every new piece costs the planet. Upcycling what you already own saves water, energy, and raw materials.",
  },
  {
    value: 60,
    suffix: "%",
    title: <a
        href="https://www.europarl.europa.eu/topics/en/article/20201208STO93327/fast-fashion-eu-laws-for-sustainable-textile-consumption"
        target="_blank"
        rel="noreferrer"
        className="text-primary underline"
      >Of clothes end up in landfills</a>,
    description:
      "Most wardrobes are full of untapped potential. We built Reverie so creativity beats consumption.",
  },
  {
    value: 1,
    title: "Planet to share",
    description:
      "Small stitches add up. Track your impact, join a community, and make circular fashion actually fun.",
  },
];

function CountingStat({
  value,
  prefix,
  suffix,
  decimals = 0,
}: Pick<Reason, "value" | "prefix" | "suffix" | "decimals">) {
  const { count, ref } = useCounter(value);

  return (
    <div
      ref={ref}
      className="flex items-baseline gap-0.5 font-black tabular-nums text-primary"
    >
      {prefix && <span className="text-3xl md:text-4xl">{prefix}</span>}
      <span className="text-4xl md:text-5xl">{count.toFixed(decimals)}</span>
      {suffix && (
        <span className="text-2xl text-accent md:text-3xl">{suffix}</span>
      )}
    </div>
  );
}

export function WhyReverieSection() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-background via-secondary/40 to-background py-20 md:py-28">
      <div className="pointer-events-none absolute -left-20 top-10 h-64 w-64 rounded-full bg-accent/20 blur-3xl" />
      <div className="pointer-events-none absolute -right-16 bottom-10 h-72 w-72 rounded-full bg-primary/10 blur-3xl" />

      <div className="relative mx-auto max-w-6xl px-4">
        <Reveal>
          <div className="mx-auto max-w-2xl text-center">
            <span className="inline-block rounded-full bg-primary/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-primary">
              Why Reverie exists
            </span>
            <h2 className="mt-4 text-3xl font-black text-primary md:text-4xl">
              The numbers that inspired us
            </h2>
            <p className="mt-3 text-lg text-muted-foreground">
              Fast fashion leaves a heavy footprint. We built Reverie to turn
              that problem into playful, planet-friendly creativity.
            </p>
          </div>
        </Reveal>

        <ol className="mt-14 grid gap-5 md:grid-cols-2">
          {reasons.map((reason, index) => (
            <Reveal key={reason.title} delay={index * 0.08}>
              <li
                className={cn(
                  "group relative flex gap-5 overflow-hidden rounded-3xl border border-primary/10 bg-card/80 p-6 shadow-sm backdrop-blur-sm transition-all hover:border-accent/40 hover:shadow-lg hover:shadow-primary/5 md:p-8",
                )}
              >
                <span className="absolute -right-3 -top-3 text-7xl font-black text-primary/[0.04]">
                  {String(index + 1).padStart(2, "0")}
                </span>
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-accent text-sm font-black text-primary-foreground shadow-md shadow-primary/20">
                  {String(index + 1).padStart(2, "0")}
                </div>
                <div className="relative min-w-0 flex-1">
                  <CountingStat
                    value={reason.value}
                    prefix={reason.prefix}
                    suffix={reason.suffix}
                    decimals={reason.decimals}
                  />
                  <h3 className="mt-2 text-lg font-bold text-primary">
                    {reason.title}
                  </h3>
                  <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                    {reason.description}
                  </p>
                </div>
              </li>
            </Reveal>
          ))}
        </ol>
      </div>
    </section>
  );
}
