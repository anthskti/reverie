import Link from "next/link";
import { getGlobalStats } from "@/lib/api/analytics";
import { browseListings } from "@/lib/api/marketplace";
import { ListingGrid } from "@/components/marketplace/listing-card";
import { ImpactStats } from "@/components/gamification/impact-stats";
import { FeaturesSection } from "@/components/landing/features-section";
import { LandingCta } from "@/components/landing/landing-cta";
import {
  FloatingLeaf,
  TreeLine,
  TreeSilhouette,
} from "@/components/landing/tree-scenery";
import { WhyReverieSection } from "@/components/landing/why-reverie-section";
import { Reveal } from "@/components/motion/reveal";
import { Button } from "@/components/ui/button";
import {
  ArrowRight,
  Leaf,
  ShoppingBag,
  Sparkles,
  TreePine,
} from "lucide-react";

async function getLandingData() {
  try {
    const [stats, listings] = await Promise.all([
      getGlobalStats(),
      browseListings({ category: "upcycled_clothing" }),
    ]);
    return { stats, listings: listings.slice(0, 6), error: null };
  } catch {
    return {
      stats: {
        total_water_saved_l: 0,
        total_co2_offset_kg: 0,
        total_landfill_diverted_kg: 0,
      },
      listings: [],
      error: "Could not reach the backend. Start the API server to see live data.",
    };
  }
}

export default async function HomePage() {
  const { stats, listings, error } = await getLandingData();

  return (
    <div className="overflow-x-hidden">
      {/* Hero */}
      <section className="relative overflow-hidden bg-gradient-to-br from-[#1b4332] via-[#2d6a4f] to-[#40916c] text-primary-foreground">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_70%_20%,rgba(116,198,157,0.25),transparent_55%)]" />
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_20%_80%,rgba(183,228,199,0.15),transparent_50%)]" />

        <FloatingLeaf className="pointer-events-none absolute left-[8%] top-[18%] h-8 w-8 rotate-12 text-accent/40 animate-[pulse_4s_ease-in-out_infinite]" />
        <FloatingLeaf className="pointer-events-none absolute right-[12%] top-[28%] h-6 w-6 -rotate-45 text-accent/30 animate-[pulse_5s_ease-in-out_infinite_1s]" />
        <FloatingLeaf className="pointer-events-none absolute left-[22%] top-[55%] h-5 w-5 rotate-[30deg] text-white/20 animate-[pulse_6s_ease-in-out_infinite_0.5s]" />

        <TreeSilhouette className="pointer-events-none absolute bottom-24 left-[5%] hidden h-32 w-32 text-white/[0.08] md:block" />
        <TreeSilhouette className="pointer-events-none absolute bottom-20 right-[8%] hidden h-40 w-40 text-white/[0.06] md:block" />
        <TreePine className="pointer-events-none absolute bottom-28 right-[22%] hidden h-16 w-16 text-accent/20 lg:block" strokeWidth={1.5} />

        <div className="relative mx-auto max-w-4xl px-4 pb-32 pt-24 text-center md:pb-40 md:pt-32">
          <Reveal>
            <span className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-2 text-sm font-bold backdrop-blur-sm">
              <Leaf className="h-4 w-4 text-accent" />
              Eco-friendly upcycling, made fun
            </span>
          </Reveal>

          <Reveal delay={0.1}>
            <h1 className="mt-6 text-4xl font-black leading-[1.08] tracking-tight md:text-6xl lg:text-7xl">
              Dream up a{" "}
              <span
                className="bg-clip-text text-transparent"
                style={{
                  backgroundImage:
                    "linear-gradient(90deg, #B7E4C7 0%, #74C69D 50%, #D8F3DC 100%)",
                }}
              >
                greener wardrobe
              </span>
            </h1>
          </Reveal>

          <Reveal delay={0.18}>
            <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-primary-foreground/90 md:text-xl">
              <strong className="font-bold text-white">Our mission:</strong>{" "}
              Reverie helps you transform old clothes into something you love —
              with AI design, sewing guides, impact tracking, and a marketplace
              built for circular fashion.
            </p>
          </Reveal>

          <Reveal delay={0.26}>
            <div className="mt-10 flex flex-wrap justify-center gap-4">
              <Button
                asChild
                size="lg"
                className="bg-white text-primary shadow-lg shadow-black/15 hover:scale-[1.03] hover:bg-white/90"
              >
                <Link href="/upcycle">
                  <Sparkles className="h-4 w-4" />
                  Start Upcycling
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </Button>
              <Button
                asChild
                size="lg"
                variant="outline"
                className="border-white/30 bg-white/10 text-primary-foreground hover:scale-[1.03] hover:bg-white/20"
              >
                <Link href="/marketplace">
                  <ShoppingBag className="h-4 w-4" />
                  Browse Marketplace
                </Link>
              </Button>
            </div>
          </Reveal>

          <Reveal delay={0.34}>
            <p className="mt-6 text-sm font-semibold text-primary-foreground/60">
              Free to start · No new fabric required · Real environmental impact
            </p>
          </Reveal>
        </div>

        <TreeLine className="pointer-events-none absolute bottom-0 left-0 right-0 h-24 w-full text-background md:h-32" />
      </section>

      <WhyReverieSection />

      <FeaturesSection />

      {/* Community impact */}
      <section className="mx-auto max-w-6xl px-4 py-16 md:py-20">
        <Reveal>
          <div className="mx-auto max-w-2xl text-center">
            <span className="inline-block rounded-full bg-primary/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-primary">
              Real impact
            </span>
            <h2 className="mt-4 text-3xl font-black text-primary md:text-4xl">
              What our community has saved
            </h2>
            <p className="mt-3 text-muted-foreground">
              Every upcycle adds up — water, carbon, and landfill diverted.
            </p>
          </div>
        </Reveal>
        {error && (
          <p className="mb-4 mt-6 text-center text-sm text-amber-700">{error}</p>
        )}
        <Reveal delay={0.1}>
          <div className="mt-10">
            <ImpactStats
              water={stats.total_water_saved_l}
              co2={stats.total_co2_offset_kg}
              landfill={stats.total_landfill_diverted_kg}
            />
          </div>
        </Reveal>
      </section>

      {/* Featured listings */}
      {listings.length > 0 && (
        <section className="bg-secondary/30 py-16 md:py-20">
          <div className="mx-auto max-w-6xl px-4">
            <Reveal>
              <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
                <div>
                  <h2 className="text-3xl font-black text-primary md:text-4xl">
                    Fresh from the marketplace
                  </h2>
                  <p className="mt-2 text-muted-foreground">
                    One-of-a-kind upcycled pieces from the community
                  </p>
                </div>
                <Button asChild size="lg">
                  <Link href="/marketplace">
                    View all listings
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                </Button>
              </div>
            </Reveal>
            <Reveal delay={0.1}>
              <ListingGrid listings={listings} />
            </Reveal>
          </div>
        </section>
      )}

      <LandingCta />
    </div>
  );
}
