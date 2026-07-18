import Link from "next/link";
import Image from "next/image";
import type { Listing } from "@/lib/types";
import { formatUsdc, resolveMediaUrl } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";

const categoryLabels: Record<string, string> = {
  upcycled_clothing: "Upcycled",
  material: "Material",
  tool: "Tool",
};

export function ListingCard({ listing }: { listing: Listing }) {
  const imageUrl = resolveMediaUrl(listing.item_image_url);

  return (
    <Link href={`/marketplace/${listing.listing_id}`}>
      <Card className="overflow-hidden transition-shadow hover:shadow-md">
        <div className="relative aspect-[4/3] bg-muted">
          {imageUrl ? (
            <Image
              src={imageUrl}
              alt={listing.title}
              fill
              className="object-cover"
              unoptimized
            />
          ) : (
            <div className="flex h-full items-center justify-center text-muted-foreground">
              {listing.title.charAt(0)}
            </div>
          )}
        </div>
        <CardContent className="space-y-2 p-4">
          <div className="flex items-start justify-between gap-2">
            <h3 className="font-medium line-clamp-2">{listing.title}</h3>
            <Badge variant="outline" className="shrink-0 capitalize">
              {categoryLabels[listing.category] ?? listing.category}
            </Badge>
          </div>
          <p className="text-lg font-semibold text-primary">
            {formatUsdc(listing.price_usdc)}
          </p>
        </CardContent>
      </Card>
    </Link>
  );
}

export function ListingGrid({ listings }: { listings: Listing[] }) {
  if (listings.length === 0) {
    return (
      <div className="rounded-xl border border-dashed p-12 text-center text-muted-foreground">
        No listings found.
      </div>
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {listings.map((listing) => (
        <ListingCard key={listing.listing_id} listing={listing} />
      ))}
    </div>
  );
}
