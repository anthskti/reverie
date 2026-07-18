import type { UserStats } from "@/lib/types";

export interface Badge {
  id: string;
  name: string;
  description: string;
  earned: boolean;
}

export interface GamificationProfile {
  xp: number;
  level: number;
  xpForCurrentLevel: number;
  xpForNextLevel: number;
  progressToNextLevel: number;
  badges: Badge[];
}

export function computeXp(
  stats: Pick<UserStats, "water_saved_l" | "co2_offset_kg" | "landfill_diverted_kg">,
  projectsCount: number,
): number {
  return (
    stats.water_saved_l * 1 +
    stats.co2_offset_kg * 10 +
    stats.landfill_diverted_kg * 5 +
    projectsCount * 50
  );
}

export function computeLevel(xp: number): number {
  return Math.floor(Math.sqrt(xp / 100)) + 1;
}

function xpForLevel(level: number): number {
  return (level - 1) ** 2 * 100;
}

export function buildGamificationProfile(
  stats: UserStats,
  projectsCount: number,
  options?: { hasListed?: boolean; bestVerificationScore?: number },
): GamificationProfile {
  const xp = computeXp(stats, projectsCount);
  const level = computeLevel(xp);
  const xpForCurrentLevel = xpForLevel(level);
  const xpForNextLevel = xpForLevel(level + 1);
  const range = xpForNextLevel - xpForCurrentLevel;
  const progressToNextLevel =
    range > 0 ? Math.min(100, ((xp - xpForCurrentLevel) / range) * 100) : 100;

  const badges: Badge[] = [
    {
      id: "first-thread",
      name: "First Thread",
      description: "Complete your first upcycle project",
      earned: projectsCount >= 1,
    },
    {
      id: "water-warrior",
      name: "Water Warrior",
      description: "Save 100L of water through upcycling",
      earned: stats.water_saved_l >= 100,
    },
    {
      id: "carbon-cut",
      name: "Carbon Cut",
      description: "Offset 10kg of CO₂",
      earned: stats.co2_offset_kg >= 10,
    },
    {
      id: "market-maker",
      name: "Market Maker",
      description: "List an item on the marketplace",
      earned: options?.hasListed ?? false,
    },
    {
      id: "quality-craft",
      name: "Quality Craft",
      description: "Score 85+ on garment verification",
      earned: (options?.bestVerificationScore ?? 0) >= 85,
    },
  ];

  return {
    xp,
    level,
    xpForCurrentLevel,
    xpForNextLevel,
    progressToNextLevel,
    badges,
  };
}
