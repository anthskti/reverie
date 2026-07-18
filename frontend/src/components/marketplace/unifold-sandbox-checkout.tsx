"use client";

import { Loader2 } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import type { DepositSession } from "@/lib/types";
import { formatUsdc, truncateId } from "@/lib/utils";

type UnifoldSandboxCheckoutProps = {
  open: boolean;
  deposit: DepositSession | null;
  listingTitle: string;
  confirming: boolean;
  onConfirm: () => void;
  onCancel: () => void;
};

export function UnifoldSandboxCheckout({
  open,
  deposit,
  listingTitle,
  confirming,
  onConfirm,
  onCancel,
}: UnifoldSandboxCheckoutProps) {
  return (
    <Dialog open={open} onOpenChange={(next) => !next && !confirming && onCancel()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Unifold Sandbox</DialogTitle>
          <DialogDescription>
            Local demo checkout — no real crypto or card charge.
          </DialogDescription>
        </DialogHeader>

        {deposit && (
          <div className="space-y-4 text-sm">
            <div className="rounded-xl bg-muted/60 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                Paying for
              </p>
              <p className="mt-1 font-bold text-primary">{listingTitle}</p>
              <p className="mt-2 text-2xl font-black text-primary">
                {formatUsdc(deposit.amount_usdc)}
              </p>
            </div>

            <dl className="grid gap-2 text-muted-foreground">
              <div className="flex justify-between gap-4">
                <dt>Network</dt>
                <dd className="font-medium text-foreground">
                  Base ({deposit.destination_chain_id})
                </dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt>Token</dt>
                <dd className="font-medium text-foreground">
                  {deposit.destination_token_symbol}
                </dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt>Recipient</dt>
                <dd className="font-mono text-xs text-foreground">
                  {truncateId(deposit.recipient_address, 10)}
                </dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt>Session</dt>
                <dd className="font-mono text-xs text-foreground">
                  {truncateId(deposit.session_id, 18)}
                </dd>
              </div>
            </dl>
          </div>
        )}

        <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <Button variant="outline" onClick={onCancel} disabled={confirming}>
            Cancel
          </Button>
          <Button onClick={onConfirm} disabled={confirming || !deposit}>
            {confirming && <Loader2 className="animate-spin" />}
            Complete sandbox payment
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
