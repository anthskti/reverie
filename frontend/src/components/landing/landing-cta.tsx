"use client";

import Link from "next/link";
import { Reveal } from "@/components/motion/reveal";
import { Button } from "@/components/ui/button";
import { ArrowRight, Leaf, Sparkles } from "lucide-react";
import { TreeSilhouette } from "./tree-scenery";

export function LandingCta() {
  return (
    <section className="relative mx-4 mb-16 overflow-hidden rounded-[2rem] md:mx-auto md:max-w-6xl">
      <div className="relative bg-gradient-to-br from-primary via-[#2d6a4f] to-accent px-6 py-16 text-primary-foreground md:px-16 md:py-20">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(255,255,255,0.12),transparent_50%)]" />

        <TreeSilhouette className="pointer-events-none absolute bottom-0 left-6 h-28 w-28 text-white/10 md:left-12 md:h-36 md:w-36" />
        <TreeSilhouette className="pointer-events-none absolute bottom-0 right-8 h-20 w-20 text-white/10 md:right-16 md:h-32 md:w-32" />
        <TreeSilhouette className="pointer-events-none absolute bottom-0 left-1/3 h-16 w-16 text-white/[0.07]" />

        <Reveal>
          <div className="relative mx-auto max-w-2xl text-center">
            <span className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-1.5 text-sm font-bold backdrop-blur-sm">
              <Leaf className="h-4 w-4 text-accent" />
              Join the circular fashion movement
            </span>
            <h2 className="mt-5 text-3xl font-black md:text-4xl">
              Ready to grow a wardrobe that&apos;s kind to the planet?
            </h2>
            <p className="mt-4 text-lg text-primary-foreground/85">
              Start your first upcycle in minutes — or discover something
              unique from a fellow maker.
            </p>
            <div className="mt-9 flex flex-wrap justify-center gap-4">
              <Button
                asChild
                size="lg"
                className="bg-white text-primary shadow-lg shadow-black/10 hover:bg-white/90 hover:scale-[1.03]"
              >
                <Link href="/upcycle">
                  <Sparkles className="h-4 w-4" />
                  Start Creating Free
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </Button>
              <Button
                asChild
                size="lg"
                variant="outline"
                className="border-white/30 bg-white/10 text-primary-foreground hover:bg-white/20 hover:scale-[1.03]"
              >
                <Link href="/marketplace">Browse Marketplace</Link>
              </Button>
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
