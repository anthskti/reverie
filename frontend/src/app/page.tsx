import Link from "next/link";
import { getGlobalStats } from "@/lib/api/analytics";
import { browseListings } from "@/lib/api/marketplace";
import { ListingGrid } from "@/components/marketplace/listing-card";
import { ImpactStats } from "@/components/gamification/impact-stats";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ArrowRight, Recycle, Sparkles, Store, Upload } from "lucide-react";

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
    <div>
      <section className="border-b bg-gradient-to-b from-accent/30 to-background">
        <div className="mx-auto max-w-6xl px-4 py-20 text-center md:py-28">
          <p className="mb-4 text-sm font-medium uppercase tracking-widest text-primary">
            Gamified upcycling
          </p>
          <h1 className="mx-auto max-w-3xl text-4xl font-bold tracking-tight md:text-6xl">
            Turn old clothes into your next favorite piece
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground">
            Reverie combines AI design, sewing guides, environmental impact
            tracking, and a marketplace — so every stitch counts toward a
            circular wardrobe.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-4">
            <Button asChild size="lg">
              <Link href="/upcycle">
                Start Upcycling
                <ArrowRight className="ml-1" />
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href="/marketplace">Browse Marketplace</Link>
            </Button>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-16">
        <h2 className="mb-6 text-center text-2xl font-semibold">
          Community impact
        </h2>
        {error && (
          <p className="mb-4 text-center text-sm text-amber-700">{error}</p>
        )}
        <ImpactStats
          water={stats.total_water_saved_l}
          co2={stats.total_co2_offset_kg}
          landfill={stats.total_landfill_diverted_kg}
        />
      </section>

      <section className="bg-muted/30 py-16">
        <div className="mx-auto max-w-6xl px-4">
          <h2 className="mb-10 text-center text-2xl font-semibold">
            How it works
          </h2>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {steps.map((step, index) => (
              <Card key={step.title}>
                <CardContent className="p-6">
                  <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-full bg-primary text-primary-foreground">
                    <step.icon className="h-5 w-5" />
                  </div>
                  <p className="text-xs font-medium text-muted-foreground">
                    Step {index + 1}
                  </p>
                  <h3 className="mt-1 font-semibold">{step.title}</h3>
                  <p className="mt-2 text-sm text-muted-foreground">
                    {step.description}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-16">
        <div className="mb-8 flex items-end justify-between gap-4">
          <div>
            <h2 className="text-2xl font-semibold">Featured listings</h2>
            <p className="text-muted-foreground">
              One-of-a-kind upcycled pieces from the community
            </p>
          </div>
          <Button asChild variant="ghost">
            <Link href="/marketplace">View all</Link>
          </Button>
        </div>
        <ListingGrid listings={listings} />
      </section>
    </div>
  );
}
