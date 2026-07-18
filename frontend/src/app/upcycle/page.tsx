"use client";

import { useCallback, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import ReactMarkdown from "react-markdown";
import { useApiClient } from "@/lib/auth/use-api-client";
import { ideate, execute, verifyItem } from "@/lib/api/upcycle";
import { useAuthModal } from "@/components/providers/auth-modal-provider";
import type {
  ApiError,
  ExecutionResponse,
  IdeationResponse,
  UpcycleOption,
  VerificationResponse,
} from "@/lib/types";
import { resolveMediaUrl } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";

const STEPS = [
  "Upload",
  "Choose concept",
  "Generate guide",
  "Sewing guide",
  "Verify",
  "Complete",
];

export default function UpcyclePage() {
  const router = useRouter();
  const { getToken, isAuthenticated } = useApiClient();
  const { openAuthModal } = useAuthModal();
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);

  const [image, setImage] = useState<File | null>(null);
  const [style, setStyle] = useState("casual");
  const [difficulty, setDifficulty] = useState("medium");
  const [fabricType, setFabricType] = useState("cotton");
  const [weightKg, setWeightKg] = useState("0.3");
  const [generateMockups, setGenerateMockups] = useState(true);

  const [ideation, setIdeation] = useState<IdeationResponse | null>(null);
  const [selectedConcept, setSelectedConcept] = useState<UpcycleOption | null>(
    null,
  );
  const [execution, setExecution] = useState<ExecutionResponse | null>(null);
  const [verification, setVerification] = useState<VerificationResponse | null>(
    null,
  );
  const [verifyImage, setVerifyImage] = useState<File | null>(null);

  const progress = ((step + 1) / STEPS.length) * 100;

  const handleError = useCallback((error: unknown) => {
    const apiError = error as ApiError;
    toast.error(apiError.message ?? "Something went wrong");
  }, []);

  const handleIdeate = async () => {
    if (!isAuthenticated) {
      openAuthModal();
      return;
    }
    if (!image) {
      toast.error("Please upload a garment photo");
      return;
    }
    setLoading(true);
    try {
      const token = await getToken();
      const result = await ideate(token, {
        image,
        style,
        difficulty,
        fabric_type: fabricType,
        weight_kg: parseFloat(weightKg) || 0.3,
        generate_mockups: generateMockups,
      });
      setIdeation(result);
      setStep(1);
    } catch (error) {
      handleError(error);
    } finally {
      setLoading(false);
    }
  };

  const handleExecute = async () => {
    if (!ideation || !selectedConcept) return;
    setLoading(true);
    setStep(2);
    try {
      const token = await getToken();
      const result = await execute(token, {
        item_id: ideation.item_id,
        selected_concept: selectedConcept,
        fabric_type: fabricType,
        weight_kg: parseFloat(weightKg) || 0.3,
      });
      setExecution(result);
      setStep(3);
    } catch (error) {
      handleError(error);
      setStep(1);
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async () => {
    if (!ideation || !verifyImage) {
      toast.error("Upload a photo of your finished garment");
      return;
    }
    setLoading(true);
    try {
      const token = await getToken();
      const result = await verifyItem(token, ideation.item_id, verifyImage);
      setVerification(result);
      if (result.score >= 85) {
        sessionStorage.setItem(
          "reverie_best_verification_score",
          String(result.score),
        );
      }
      setStep(5);
    } catch (error) {
      handleError(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-black text-primary">Upcycle quest</h1>
        <p className="mt-2 text-muted-foreground">
          Transform a garment with AI-guided design and sewing instructions.
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          {STEPS.map((label, index) => (
            <Badge
              key={label}
              variant={index === step ? "default" : index < step ? "success" : "outline"}
            >
              {index + 1}. {label}
            </Badge>
          ))}
        </div>
        <Progress value={progress} className="mt-4" />
      </div>

      {step === 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Upload your garment</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="image">Garment photo</Label>
              <Input
                id="image"
                type="file"
                accept="image/*"
                className="mt-2"
                onChange={(e) => setImage(e.target.files?.[0] ?? null)}
              />
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <Label>Style</Label>
                <Select value={style} onValueChange={setStyle}>
                  <SelectTrigger className="mt-2">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="casual">Casual</SelectItem>
                    <SelectItem value="streetwear">Streetwear</SelectItem>
                    <SelectItem value="bohemian">Bohemian</SelectItem>
                    <SelectItem value="minimalist">Minimalist</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Difficulty</Label>
                <Select value={difficulty} onValueChange={setDifficulty}>
                  <SelectTrigger className="mt-2">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="easy">Easy</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="hard">Hard</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Fabric type</Label>
                <Input
                  className="mt-2"
                  value={fabricType}
                  onChange={(e) => setFabricType(e.target.value)}
                />
              </div>
              <div>
                <Label>Weight (kg)</Label>
                <Input
                  className="mt-2"
                  type="number"
                  step="0.01"
                  value={weightKg}
                  onChange={(e) => setWeightKg(e.target.value)}
                />
              </div>
            </div>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={generateMockups}
                onChange={(e) => setGenerateMockups(e.target.checked)}
              />
              Generate mockup previews (recommended)
            </label>
            <Button onClick={handleIdeate} disabled={loading} className="w-full sm:w-auto">
              {loading && <Loader2 className="animate-spin" />}
              Generate concepts
            </Button>
          </CardContent>
        </Card>
      )}

      {step === 1 && ideation && (
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-primary">Choose your concept</h2>
          <div className="grid gap-4 md:grid-cols-3">
            {ideation.options.map((option, index) => {
              const mockupUrl =
                option.mockup_url ??
                ideation.mockup_urls[index] ??
                ideation.original_image_url;
              const resolved = resolveMediaUrl(mockupUrl);
              const isSelected = selectedConcept?.title === option.title;
              return (
                <Card
                  key={option.title}
                  className={`cursor-pointer overflow-hidden transition-all ${
                    isSelected ? "ring-2 ring-primary" : "hover:border-primary/25 hover:shadow-lg"
                  }`}
                  onClick={() => setSelectedConcept(option)}
                >
                  <div className="relative aspect-square bg-muted">
                    {resolved ? (
                      <Image
                        src={resolved}
                        alt={option.title}
                        fill
                        className="object-cover"
                        unoptimized
                      />
                    ) : null}
                  </div>
                  <CardContent className="space-y-2 p-4">
                    <h3 className="font-bold">{option.title}</h3>
                    <p className="text-sm text-muted-foreground line-clamp-3">
                      {option.description}
                    </p>
                    <Badge variant="outline" className="capitalize">
                      {option.difficulty}
                    </Badge>
                  </CardContent>
                </Card>
              );
            })}
          </div>
          <Button
            disabled={!selectedConcept || loading}
            onClick={handleExecute}
          >
            {loading && <Loader2 className="animate-spin" />}
            Start project
          </Button>
        </div>
      )}

      {step === 2 && (
        <Card>
          <CardContent className="flex flex-col items-center gap-4 py-16">
            <Loader2 className="h-10 w-10 animate-spin text-primary" />
            <p className="text-lg font-medium">Generating your sewing guide…</p>
            <p className="text-sm text-muted-foreground">
              Our AI agents are writing instructions and calculating environmental impact.
            </p>
          </CardContent>
        </Card>
      )}

      {step === 3 && execution && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Sewing guide</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-sm max-w-none dark:prose-invert">
              <ReactMarkdown>{execution.sewing_guide}</ReactMarkdown>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Environmental impact</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">{execution.environmental_impact}</p>
              {execution.environmental_data && (
                <div className="mt-4 grid gap-2 text-sm sm:grid-cols-3">
                  <div>💧 {execution.environmental_data.water_saved_liters?.toFixed(1)} L water saved</div>
                  <div>🌿 {execution.environmental_data.co2_offset_kg?.toFixed(1)} kg CO₂ offset</div>
                  <div>♻️ {execution.environmental_data.landfill_diverted_kg?.toFixed(1)} kg diverted</div>
                </div>
              )}
            </CardContent>
          </Card>
          <Button onClick={() => setStep(4)}>Continue to verification</Button>
        </div>
      )}

      {step === 4 && ideation && (
        <Card>
          <CardHeader>
            <CardTitle>Verify your finished garment</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Upload a photo of your completed piece. AI will compare it to your design mockup.
            </p>
            <Input
              type="file"
              accept="image/*"
              onChange={(e) => setVerifyImage(e.target.files?.[0] ?? null)}
            />
            <Button onClick={handleVerify} disabled={loading}>
              {loading && <Loader2 className="animate-spin" />}
              Submit verification
            </Button>
          </CardContent>
        </Card>
      )}

      {step === 5 && verification && ideation && (
        <Card>
          <CardHeader>
            <CardTitle>Quest complete!</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="text-4xl font-black text-primary">
                {verification.score}/100
              </div>
              <div>
                <p className="font-semibold">Quality score</p>
                {verification.is_eligible && (
                  <Badge variant="success">Marketplace eligible</Badge>
                )}
              </div>
            </div>
            <p className="text-muted-foreground">{verification.feedback}</p>
            <div className="flex flex-wrap gap-3">
              <Button asChild>
                <Link href={`/marketplace/sell?itemId=${ideation.item_id}`}>
                  List on marketplace
                </Link>
              </Button>
              <Button asChild variant="outline">
                <Link href={`/inventory/${ideation.item_id}`}>View item</Link>
              </Button>
              <Button variant="ghost" onClick={() => router.push("/profile")}>
                Back to profile
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
