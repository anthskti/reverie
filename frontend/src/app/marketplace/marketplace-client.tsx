"use client";

import { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { browseListings } from "@/lib/api/marketplace";
import type { Listing } from "@/lib/types";
import { ListingGrid } from "@/components/marketplace/listing-card";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";

const categories = [
  { value: "all", label: "All" },
  { value: "upcycled_clothing", label: "Upcycled" },
  { value: "material", label: "Materials" },
  { value: "tool", label: "Tools" },
];

export default function MarketplacePage() {
  const searchParams = useSearchParams();
  const [listings, setListings] = useState<Listing[]>([]);
  const [category, setCategory] = useState(
    searchParams.get("category") ?? "all",
  );
  const [query, setQuery] = useState(searchParams.get("q") ?? "");
  const [loading, setLoading] = useState(true);

  const loadListings = useCallback(async () => {
    setLoading(true);
    try {
      const data = await browseListings({
        category: category === "all" ? undefined : category,
        q: query || undefined,
      });
      setListings(data);
    } catch {
      toast.error("Failed to load marketplace listings");
    } finally {
      setLoading(false);
    }
  }, [category, query]);

  useEffect(() => {
    const timer = setTimeout(loadListings, 300);
    return () => clearTimeout(timer);
  }, [loadListings]);

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <h1 className="text-3xl font-black text-primary">Marketplace</h1>
      <p className="mt-2 text-muted-foreground">
        Buy and sell upcycled clothing, materials, and tools.
      </p>

      <div className="mt-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <Tabs value={category} onValueChange={setCategory}>
          <TabsList>
            {categories.map((cat) => (
              <TabsTrigger key={cat.value} value={cat.value}>
                {cat.label}
              </TabsTrigger>
            ))}
          </TabsList>
        </Tabs>
        <Input
          placeholder="Search listings…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="max-w-sm"
        />
      </div>

      <div className="mt-8">
        {loading ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[...Array(6)].map((_, i) => (
              <Skeleton key={i} className="aspect-[4/3] w-full" />
            ))}
          </div>
        ) : (
          <ListingGrid listings={listings} />
        )}
      </div>
    </div>
  );
}
