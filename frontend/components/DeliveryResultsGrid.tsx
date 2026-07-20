"use client";

import { useEffect, useMemo, useState } from "react";
import { ResultCard } from "@/components/ResultCard";
import {
  getDeliveryEstimates,
  type DeliveryEstimateItem,
  type SearchResult,
} from "@/lib/api";
import { currentDeliveryZip, subscribeToDeliveryZip } from "@/lib/ephemeralDelivery";

type DeliveryStatus = "idle" | "loading" | "done" | "error";

type Props = {
  results: SearchResult[];
  query: string;
  category: string;
  productId?: string;
  ariaLabel: string;
  deliveryEnabled?: boolean;
};

export function DeliveryResultsGrid({
  results,
  query,
  category,
  productId,
  ariaLabel,
  deliveryEnabled = false,
}: Props) {
  const itemIds = useMemo(
    () => results
      .filter((result) => result.provider.toLowerCase() === "ebay" && result.marketplace_item_id)
      .map((result) => result.marketplace_item_id as string)
      .slice(0, 3),
    [results],
  );
  const itemIdsKey = itemIds.join("|");
  const [postalCode, setPostalCode] = useState("");
  const [status, setStatus] = useState<DeliveryStatus>("idle");
  const [estimates, setEstimates] = useState<DeliveryEstimateItem[]>([]);

  useEffect(() => {
    setPostalCode(currentDeliveryZip());
    return subscribeToDeliveryZip(setPostalCode);
  }, []);

  useEffect(() => {
    let cancelled = false;
    if (!deliveryEnabled || !postalCode || !itemIds.length) {
      setStatus("idle");
      setEstimates([]);
      return () => {
        cancelled = true;
      };
    }

    setStatus("loading");
    setEstimates([]);
    getDeliveryEstimates(postalCode, itemIds)
      .then((response) => {
        if (cancelled) return;
        setEstimates(response.items);
        setStatus("done");
      })
      .catch(() => {
        if (cancelled) return;
        setEstimates([]);
        setStatus("error");
      });

    return () => {
      cancelled = true;
    };
  }, [deliveryEnabled, itemIdsKey, postalCode]);

  const estimatesById = useMemo(
    () => new Map(estimates.map((estimate) => [estimate.item_id, estimate])),
    [estimates],
  );

  return (
    <section className="mt-8 grid gap-5 xl:grid-cols-3" aria-label={ariaLabel}>
      {results.map((result, index) => {
        const itemId = result.marketplace_item_id || "";
        const hasDeliveryLookup = result.provider.toLowerCase() === "ebay" && Boolean(itemId);
        return (
          <ResultCard
            key={`${category}-${result.provider}-${itemId || result.url}-${index}`}
            result={result}
            query={query}
            category={category}
            productId={productId}
            variant="buy_now"
            deliveryStatus={hasDeliveryLookup ? status : "idle"}
            deliveryEstimate={hasDeliveryLookup ? estimatesById.get(itemId) || null : null}
          />
        );
      })}
    </section>
  );
}
