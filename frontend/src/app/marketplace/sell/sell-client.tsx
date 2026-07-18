"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useApiClient } from "@/lib/auth/use-api-client";
import { getMyItems } from "@/lib/api/inventory";
import { createListing } from "@/lib/api/marketplace";
import type { ApiError, Item, ListingCategory } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";

export default function SellPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const preselectedItemId = searchParams.get("itemId");
  const { getToken, isAuthenticated } = useApiClient();

  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");
  const [category, setCategory] = useState<ListingCategory>("upcycled_clothing");
  const [itemId, setItemId] = useState(preselectedItemId ?? "");

  useEffect(() => {
    if (!isAuthenticated) return;
    async function load() {
      try {
        const token = await getToken();
        const data = await getMyItems(token);
        setItems(data);
        if (preselectedItemId) {
          const item = data.find((i) => i.id === preselectedItemId);
          if (item) setTitle(item.style ?? "Upcycled piece");
        }
      } catch (error) {
        toast.error((error as ApiError).message ?? "Failed to load inventory");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [getToken, isAuthenticated, preselectedItemId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const priceNum = parseFloat(price);
    if (!title || !priceNum || priceNum <= 0) {
      toast.error("Enter a title and valid price");
      return;
    }
    if (category === "upcycled_clothing" && !itemId) {
      toast.error("Select an inventory item for upcycled clothing listings");
      return;
    }

    setSubmitting(true);
    try {
      const token = await getToken();
      const result = await createListing(token, {
        title,
        description: description || undefined,
        price_usdc: priceNum,
        category,
        item_id: category === "upcycled_clothing" ? itemId : undefined,
      });
      sessionStorage.setItem("reverie_has_listed", "1");
      toast.success("Listing created!");
      router.push(`/marketplace/${result.listing_id}`);
    } catch (error) {
      toast.error((error as ApiError).message ?? "Failed to create listing");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="mx-auto max-w-xl space-y-4 px-4 py-8">
        <Skeleton className="h-10 w-48" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-xl px-4 py-8">
      <Button asChild variant="ghost" size="sm">
        <Link href="/marketplace">← Marketplace</Link>
      </Button>
      <h1 className="mt-4 text-3xl font-black text-primary">Sell on Reverie</h1>
      <p className="mt-2 text-muted-foreground">
        List upcycled clothing, materials, or tools for USDC.
      </p>

      <Card className="mt-8">
        <CardHeader>
          <CardTitle>New listing</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label>Category</Label>
              <Select
                value={category}
                onValueChange={(v) => setCategory(v as ListingCategory)}
              >
                <SelectTrigger className="mt-2">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="upcycled_clothing">Upcycled clothing</SelectItem>
                  <SelectItem value="material">Material</SelectItem>
                  <SelectItem value="tool">Tool</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {category === "upcycled_clothing" && (
              <div>
                <Label>Inventory item</Label>
                <Select value={itemId} onValueChange={setItemId}>
                  <SelectTrigger className="mt-2">
                    <SelectValue placeholder="Select item" />
                  </SelectTrigger>
                  <SelectContent>
                    {items.map((item) => (
                      <SelectItem key={item.id} value={item.id}>
                        {item.style ?? item.id.slice(0, 8)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}

            <div>
              <Label htmlFor="title">Title</Label>
              <Input
                id="title"
                className="mt-2"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
            </div>

            <div>
              <Label htmlFor="description">Description</Label>
              <Input
                id="description"
                className="mt-2"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            <div>
              <Label htmlFor="price">Price (USDC)</Label>
              <Input
                id="price"
                type="number"
                step="0.01"
                min="0.01"
                className="mt-2"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                required
              />
            </div>

            <Button type="submit" disabled={submitting} className="w-full">
              {submitting && <Loader2 className="animate-spin" />}
              Create listing
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
