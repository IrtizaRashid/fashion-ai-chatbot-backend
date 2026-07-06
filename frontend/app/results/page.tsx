"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { ResultCard } from "@/components/cards/result-card"

interface AnalysisResult {
  body_type?: string
  body_build?: string
  shoulders?: string
  torso?: string
  legs?: string
  neck?: string
  posture?: string
  recommended_fit?: string[]
  recommended_shirts?: string[]
  recommended_trousers?: string[]
  recommended_colors?: string[]
  recommended_patterns?: string[]
  avoid?: string[]
  summary?: string
  disclaimer?: string
}

interface StoredAnalysis {
  result: AnalysisResult
  imageName?: string
  analyzedAt?: string
}

export default function ResultsPage() {
  const stored =
    typeof window !== "undefined"
      ? sessionStorage.getItem("fashion-analysis-result")
      : null
  let result: AnalysisResult | null = null
  let imageName: string | undefined
  let analyzedAt: string | undefined

  if (stored) {
    try {
      const parsed = JSON.parse(stored) as StoredAnalysis
      result = parsed.result
      imageName = parsed.imageName
      analyzedAt = parsed.analyzedAt
    } catch {
      result = null
    }
  }

  const bodyItems = result
    ? ([
        result.body_type && `Body type: ${result.body_type}`,
        result.body_build,
        result.shoulders && `Shoulders: ${result.shoulders}`,
        result.torso && `Torso: ${result.torso}`,
        result.legs && `Legs: ${result.legs}`,
        result.neck && `Neck: ${result.neck}`,
        result.posture && `Posture: ${result.posture}`,
      ].filter(Boolean) as string[])
    : []

  const clothingItems = [
    ...(result?.recommended_shirts ?? []),
    ...(result?.recommended_trousers ?? []),
  ]

  const explanationItems = result
    ? ([
        result.summary,
        result.recommended_patterns?.length
          ? `Patterns: ${result.recommended_patterns.join(" ")}`
          : undefined,
        result.avoid?.length ? `Avoid: ${result.avoid.join(" ")}` : undefined,
        result.disclaimer,
      ].filter(Boolean) as string[])
    : []

  return (
    <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="mb-12">
        <h1 className="text-4xl font-bold text-black">Your Analysis Results</h1>
        <p className="mt-2 text-gray-600">
          Based on your photo and measurements, here are our personalized recommendations.
        </p>
        {result && (
          <p className="mt-3 text-sm text-gray-500">
            Analyzed {imageName ?? "uploaded photo"}
            {analyzedAt ? ` at ${new Date(analyzedAt).toLocaleTimeString()}` : ""}
          </p>
        )}
      </div>

      {!result && (
        <div className="mb-8 rounded-lg border border-yellow-200 bg-yellow-50 p-4 text-sm text-yellow-900">
          No analysis result found yet. Start a new analysis and upload a photo.
        </div>
      )}

      <div className="grid gap-8 md:grid-cols-2">
        <ResultCard title="Body Analysis" items={bodyItems} loading={!result} />

        <ResultCard
          title="Recommended Colors"
          items={result?.recommended_colors ?? []}
          loading={!result}
          type="grid"
        />

        <ResultCard
          title="Recommended Fits"
          items={result?.recommended_fit ?? []}
          loading={!result}
        />

        <ResultCard
          title="Recommended Clothing"
          items={clothingItems}
          loading={!result}
        />

        <div className="md:col-span-2">
          <ResultCard
            title="Why These Recommendations?"
            items={explanationItems}
            loading={!result}
          />
        </div>
      </div>

      <div className="mt-12 flex flex-col gap-4 sm:flex-row sm:justify-center">
        <Link href="/analyze">
          <Button size="lg">New Analysis</Button>
        </Link>
        <Link href="/">
          <Button size="lg" variant="outline">
            Back to Home
          </Button>
        </Link>
      </div>
    </div>
  )
}
