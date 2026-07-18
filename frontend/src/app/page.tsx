import Link from "next/link";
import { getGlobalStats } from "@/lib/api/analytics";
import { browseListings } from "@/lib/api/marketplace";
import { ListingGrid } from "@/components/marketplace/listing-card";
import { ImpactStats } from "@/components/gamification/impact-stats";
import { Reveal } from "@/components/motion/reveal";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ArrowRight, Recycle, ShoppingBag, Sparkles, Store, Upload } from "lucide-react";

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

  const steps = [
    {
      icon: Upload,
      title: "Upload",
      description: "Snap a photo of a garment you want to transform.",
    },
    {
      icon: Sparkles,
      title: "AI concepts",
      description: "Get three realistic upcycle ideas with mockups.",
    },
    {
      icon: Recycle,
      title: "Sew & verify",
      description: "Follow your guide, then verify craftsmanship with AI.",
    },
    {
      icon: Store,
      title: "Sell",
      description: "List your creation on the Reverie marketplace.",
    },
  ];

  return (
    <div className="overflow-x-hidden">
      {/* Hero */}
      <section className="relative overflow-hidden bg-primary py-24 text-primary-foreground md:py-32">
        <div className="absolute inset-0 bg-gradient-to-b from-primary via-primary/95 to-background" />
        <span className="absolute left-8 top-16 text-4xl opacity-40 md:left-16">🍃</span>
        <span className="absolute right-12 top-32 text-3xl opacity-30 md:right-24">🌿</span>
        <span className="absolute bottom-16 left-1/4 text-2xl opacity-20">🍀</span>

        <div className="relative mx-auto max-w-3xl px-4 text-center">
          <Reveal>
            <span className="inline-flex items-center gap-2 rounded-full border border-accent/40 bg-accent/15 px-4 py-2 text-sm font-bold text-accent-foreground/90 backdrop-blur-sm">
              <Sparkles className="h-3.5 w-3.5 text-accent" />
              Gamified upcycling
            </span>
          </Reveal>
          <Reveal delay={0.1}>
            <h1 className="mt-6 text-4xl font-black leading-[1.05] tracking-tight md:text-6xl">
              Turn old clothes into your{" "}
              <span
                className="bg-clip-text text-transparent"
                style={{
                  backgroundImage:
                    "linear-gradient(90deg, #74C69D 0%, #B7E4C7 60%, #52B788 100%)",
                }}
              >
                next favorite piece
              </span>
            </h1>
          </Reveal>
          <Reveal delay={0.18}>
            <p className="mx-auto mt-6 max-w-2xl text-lg text-primary-foreground/85">
              Reverie combines AI design, sewing guides, environmental impact
              tracking, and a marketplace — so every stitch counts toward a
              circular wardrobe.
            </p>
          </Reveal>
          <Reveal delay={0.26}>
            <div className="mt-9 flex flex-wrap justify-center gap-4">
              <Button asChild size="lg">
                <Link href="/upcycle">
                  Start Upcycling
                  <ArrowRight className="ml-1 h-4 w-4" />
                </Link>
              </Button>
              <Button
                asChild
                size="lg"
                variant="outline"
                className="border-primary-foreground/25 bg-primary-foreground/10 text-primary-foreground hover:bg-primary-foreground/20"
              >
                <Link href="/marketplace">
                  <ShoppingBag className="h-4 w-4" />
                  Browse Marketplace
                </Link>
              </Button>
            </div>
          </Reveal>
        </div>
      </section>

      {/* Community impact */}
      <section className="mx-auto max-w-6xl px-4 py-16">
        <Reveal>
          <h2 className="mb-6 text-center text-2xl font-black text-primary md:text-3xl">
            Community impact
          </h2>
        </Reveal>
        {error && (
          <p className="mb-4 text-center text-sm text-amber-700">{error}</p>
        )}
        <Reveal delay={0.1}>
          <ImpactStats
            water={stats.total_water_saved_l}
            co2={stats.total_co2_offset_kg}
            landfill={stats.total_landfill_diverted_kg}
          />
        </Reveal>
      </section>

      {/* How it works */}
      <section className="bg-secondary/50 py-16">
        <div className="mx-auto max-w-6xl px-4">
          <Reveal>
            <h2 className="mb-10 text-center text-2xl font-black text-primary md:text-3xl">
              How it works
            </h2>
          </Reveal>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {steps.map((step, index) => (
              <Reveal key={step.title} delay={index * 0.08}>
                <Card className="h-full border-border hover:border-primary/25 hover:shadow-lg">
                  <CardContent className="p-6">
                    <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-md shadow-primary/20">
                      <step.icon className="h-5 w-5" />
                    </div>
                    <p className="text-xs font-bold uppercase tracking-wide text-muted-foreground">
                      Step {index + 1}
                    </p>
                    <h3 className="mt-1 font-bold text-primary">{step.title}</h3>
                    <p className="mt-2 text-sm text-muted-foreground">
                      {step.description}
                    </p>
                  </CardContent>
                </Card>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* Featured listings */}
      <section className="mx-auto max-w-6xl px-4 py-16">
        <Reveal>
          <div className="mb-8 flex items-end justify-between gap-4">
            <div>
              <h2 className="text-2xl font-black text-primary md:text-3xl">
                Featured listings
              </h2>
              <p className="text-muted-foreground">
                One-of-a-kind upcycled pieces from the community
              </p>
            </div>
            <Button asChild variant="ghost">
              <Link href="/marketplace">View all</Link>
            </Button>
          </div>
        </Reveal>
        <Reveal delay={0.1}>
          <ListingGrid listings={listings} />
        </Reveal>
      </section>
    </div>
  );
}
