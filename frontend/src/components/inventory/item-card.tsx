import Link from "next/link";
import Image from "next/image";
import type { Item } from "@/lib/types";
import { resolveMediaUrl } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";

export function ItemCard({ item }: { item: Item }) {
  const imageUrl = resolveMediaUrl(item.original_image_url);

  return (
    <Link href={`/inventory/${item.id}`}>
      <Card className="overflow-hidden border-border transition-all hover:border-primary/25 hover:shadow-lg">
        <div className="relative aspect-square bg-muted">
          {imageUrl ? (
            <Image
              src={imageUrl}
              alt={item.style ?? "Garment"}
              fill
              className="object-cover"
              unoptimized
            />
          ) : (
            <div className="flex h-full items-center justify-center text-muted-foreground">
              No image
            </div>
          )}
        </div>
        <CardContent className="space-y-2 p-4">
          <div className="flex items-start justify-between gap-2">
            <h3 className="font-bold line-clamp-1">
              {item.style ?? "Untitled garment"}
            </h3>
            {item.is_market_eligible && (
              <Badge variant="success" className="shrink-0">
                Verified
              </Badge>
            )}
          </div>
          <p className="text-sm text-muted-foreground capitalize">
            {item.difficulty ?? "unknown"} · {item.fabric_type ?? "fabric n/a"}
          </p>
        </CardContent>
      </Card>
    </Link>
  );
}

export function InventoryGrid({ items }: { items: Item[] }) {
  if (items.length === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-border p-12 text-center">
        <p className="text-muted-foreground">No items in your wardrobe yet.</p>
        <Link href="/upcycle" className="mt-4 inline-block font-semibold text-primary hover:underline">
          Start your first upcycle →
        </Link>
      </div>
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {items.map((item) => (
        <ItemCard key={item.id} item={item} />
      ))}
    </div>
  );
}
