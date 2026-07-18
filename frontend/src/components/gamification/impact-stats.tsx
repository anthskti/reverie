import type { GamificationProfile } from "@/lib/gamification";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
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
    <Card className="overflow-hidden border-primary/20 bg-gradient-to-br from-accent/40 to-background">
      <CardHeader>
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-sm text-muted-foreground">Upcycler profile</p>
            <CardTitle className="text-2xl">
              {displayName ? `${displayName}` : "Your journey"}
            </CardTitle>
          </div>
          <div className="rounded-full bg-primary px-4 py-2 text-center text-primary-foreground">
            <div className="text-xs uppercase tracking-wide opacity-80">Level</div>
            <div className="text-2xl font-bold">{profile.level}</div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <div className="mb-2 flex justify-between text-sm">
            <span>{profile.xp} XP</span>
            <span className="text-muted-foreground">
              {Math.round(profile.progressToNextLevel)}% to level {profile.level + 1}
            </span>
          </div>
          <Progress value={profile.progressToNextLevel} />
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
    { label: "Water saved", value: `${water.toFixed(1)} L`, icon: "💧" },
    { label: "CO₂ offset", value: `${co2.toFixed(1)} kg`, icon: "🌿" },
    { label: "Landfill diverted", value: `${landfill.toFixed(1)} kg`, icon: "♻️" },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-3">
      {stats.map((stat) => (
        <Card key={stat.label}>
          <CardContent className="flex items-center gap-3 p-4">
            <span className="text-2xl">{stat.icon}</span>
            <div>
              <p className="text-sm text-muted-foreground">{stat.label}</p>
              <p className="text-xl font-semibold">{stat.value}</p>
            </div>
          </CardContent>
        </Card>
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
          className={badge.earned ? "border-primary/30 bg-accent/20" : "opacity-60"}
        >
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Award className={badge.earned ? "text-primary" : "text-muted-foreground"} />
              <span className="font-medium">{badge.name}</span>
            </div>
            <p className="mt-1 text-sm text-muted-foreground">{badge.description}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
