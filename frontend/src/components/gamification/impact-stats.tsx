"use client";

import type { GamificationProfile } from "@/lib/gamification";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useCounter } from "@/components/motion/use-counter";
import { Award } from "lucide-react";

export function GamificationHeader({
  profile,
  displayName,
}: {
  profile: GamificationProfile;
  displayName?: string;
}) {
  const earnedBadges = profile.badges.filter((b) => b.earned);

  return (
    <Card className="overflow-hidden border-primary/20 bg-gradient-to-br from-primary to-primary/85 text-primary-foreground shadow-lg shadow-primary/20">
      <CardHeader>
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-bold uppercase tracking-widest text-primary-foreground/70">
              Upcycler profile
            </p>
            <CardTitle className="text-2xl text-primary-foreground">
              {displayName ? `${displayName}` : "Your journey"}
            </CardTitle>
          </div>
          <div className="rounded-full bg-accent px-4 py-2 text-center text-accent-foreground">
            <div className="text-xs font-bold uppercase tracking-wide opacity-80">Level</div>
            <div className="text-2xl font-black">{profile.level}</div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <div className="mb-2 flex justify-between text-sm font-semibold">
            <span>{profile.xp} XP</span>
            <span className="text-primary-foreground/70">
              {Math.round(profile.progressToNextLevel)}% to level {profile.level + 1}
            </span>
          </div>
          <Progress value={profile.progressToNextLevel} className="bg-primary-foreground/15" />
        </div>
        {earnedBadges.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {earnedBadges.map((badge) => (
              <Badge key={badge.id} variant="success" className="gap-1">
                <Award className="h-3 w-3" />
                {badge.name}
              </Badge>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function AnimatedStatValue({
  value,
  decimals = 1,
}: {
  value: number;
  decimals?: number;
}) {
  const { count, ref } = useCounter(value);
  return (
    <div ref={ref} className="text-3xl font-black text-primary-foreground md:text-4xl">
      {count.toFixed(decimals)}
    </div>
  );
}

export function ImpactStats({
  water,
  co2,
  landfill,
}: {
  water: number;
  co2: number;
  landfill: number;
}) {
  const stats = [
    { label: "Water saved", value: water, unit: "L", icon: "💧" },
    { label: "CO₂ offset", value: co2, unit: "kg", icon: "🌿" },
    { label: "Landfill diverted", value: landfill, unit: "kg", icon: "♻️" },
  ];

  return (
    <div className="grid gap-4 rounded-3xl bg-primary p-6 shadow-lg shadow-primary/20 sm:grid-cols-3 sm:p-8">
      {stats.map((stat) => (
        <div key={stat.label} className="flex flex-col items-center gap-1.5 text-center">
          <span className="text-2xl">{stat.icon}</span>
          <div className="flex items-baseline gap-1">
            <AnimatedStatValue value={stat.value} />
            <span className="text-lg font-bold text-accent">{stat.unit}</span>
          </div>
          <p className="text-sm font-semibold text-primary-foreground/75">{stat.label}</p>
        </div>
      ))}
    </div>
  );
}

export function BadgeGrid({ badges }: { badges: GamificationProfile["badges"] }) {
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {badges.map((badge) => (
        <Card
          key={badge.id}
          className={badge.earned ? "border-primary/25 bg-accent/10" : "opacity-60"}
        >
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Award className={badge.earned ? "text-primary" : "text-muted-foreground"} />
              <span className="font-bold">{badge.name}</span>
            </div>
            <p className="mt-1 text-sm text-muted-foreground">{badge.description}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
