"use client";

import Link from "next/link";
import { Reveal } from "@/components/motion/reveal";
import { Button } from "@/components/ui/button";
import { ArrowRight, ShoppingBag, Sparkles, Shirt, Wand2 } from "lucide-react";

const features = [
  {
    icon: ShoppingBag,
    accent: "from-emerald-600 to-teal-500",
    badge: "Marketplace",
    title: "Shop one-of-a-kind upcycles",
    description:
      "Browse verified, handmade pieces from real upcyclers. Every listing tells a story and keeps textiles out of the trash.",
    highlights: ["Community sellers", "Verified craftsmanship", "Unique finds"],
    href: "/marketplace",
    cta: "Explore Marketplace",
  },
  {
    icon: Sparkles,
    accent: "from-green-700 to-lime-500",
    badge: "AI Wardrobe",
    title: "Reimagine what you already own",
    description:
      "Snap a photo, get AI-powered upcycle concepts, sewing guides, and a digital wardrobe that grows with every project.",
    highlights: ["AI design mockups", "Step-by-step guides", "Digital inventory"],
    href: "/upcycle",
    cta: "Open AI Wardrobe",
  },
];

export function FeaturesSection() {
  return (
    <section className="py-20 md:py-28">
      <div className="mx-auto max-w-6xl px-4">
        <Reveal>
          <div className="mx-auto max-w-2xl text-center">
            <span className="inline-block rounded-full bg-accent/20 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-primary">
              What you can do
            </span>
            <h2 className="mt-4 text-3xl font-black text-primary md:text-4xl">
              Two paths to a greener wardrobe
            </h2>
            <p className="mt-3 text-lg text-muted-foreground">
              Create with AI, sell what you make, or discover pieces from
              makers who share your values.
            </p>
          </div>
        </Reveal>

        <div className="mt-14 grid gap-8 lg:grid-cols-2">
          {features.map((feature, index) => (
            <Reveal key={feature.badge} delay={index * 0.1}>
              <article className="group relative flex h-full flex-col overflow-hidden rounded-[2rem] border border-primary/10 bg-card shadow-md transition-all hover:border-accent/30 hover:shadow-xl hover:shadow-primary/10">
                <div
                  className={`relative bg-gradient-to-br ${feature.accent} px-8 py-10 text-primary-foreground`}
                >
                  <div className="absolute -right-6 -top-6 h-32 w-32 rounded-full bg-white/10 blur-2xl" />
                  <div className="absolute bottom-4 right-8 opacity-20">
                    {feature.badge === "AI Wardrobe" ? (
                      <Shirt className="h-24 w-24" strokeWidth={1} />
                    ) : (
                      <ShoppingBag className="h-24 w-24" strokeWidth={1} />
                    )}
                  </div>
                  <span className="relative inline-flex items-center gap-1.5 rounded-full bg-white/20 px-3 py-1 text-xs font-bold uppercase tracking-wide backdrop-blur-sm">
                    <Wand2 className="h-3 w-3" />
                    {feature.badge}
                  </span>
                  <h3 className="relative mt-4 text-2xl font-black md:text-3xl">
                    {feature.title}
                  </h3>
                </div>

                <div className="flex flex-1 flex-col p-8">
                  <p className="text-muted-foreground">{feature.description}</p>
                  <ul className="mt-6 flex flex-wrap gap-2">
                    {feature.highlights.map((item) => (
                      <li
                        key={item}
                        className="rounded-full bg-secondary px-3 py-1 text-xs font-semibold text-secondary-foreground"
                      >
                        {item}
                      </li>
                    ))}
                  </ul>
                  <div className="mt-auto pt-8">
                    <Button asChild size="lg" className="w-full sm:w-auto">
                      <Link href={feature.href}>
                        <feature.icon className="h-4 w-4" />
                        {feature.cta}
                        <ArrowRight className="h-4 w-4" />
                      </Link>
                    </Button>
                  </div>
                </div>
              </article>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
