"use client"

import { Button } from "@/components/ui/button"
import { ResultCard } from "@/components/cards/result-card"
import Link from "next/link"

export default function ResultsPage() {
  return (
    <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="mb-12">
        <h1 className="text-4xl font-bold text-black">Your Analysis Results</h1>
        <p className="mt-2 text-gray-600">
          Based on your photo and measurements, here are our personalized recommendations.
        </p>
      </div>

      <div className="grid gap-8 md:grid-cols-2">
        {/* Body Analysis */}
        <ResultCard
          title="Body Analysis"
          items={["Loading analysis..."]}
          loading={true}
        />

        {/* Recommended Colors */}
        <ResultCard
          title="Recommended Colors"
          items={["Loading colors..."]}
          loading={true}
          type="grid"
        />

        {/* Recommended Fits */}
        <ResultCard
          title="Recommended Fits"
          items={["Loading fits..."]}
          loading={true}
        />

        {/* Recommended Shirts */}
        <ResultCard
          title="Recommended Shirts"
          items={["Loading recommendations..."]}
          loading={true}
        />

        {/* Reasons */}
        <div className="md:col-span-2">
          <ResultCard
            title="Why These Recommendations?"
            items={["Loading explanations..."]}
            loading={true}
          />
        </div>

        {/* Product Cards */}
        <div className="md:col-span-2">
          <h2 className="mb-4 text-2xl font-bold text-black">
            Suggested Products
          </h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div
                key={i}
                className="flex flex-col rounded-lg border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow"
              >
                <div className="h-48 bg-gray-200 animate-pulse" />
                <div className="p-4 space-y-3">
                  <div className="h-4 bg-gray-200 rounded animate-pulse" />
                  <div className="h-4 bg-gray-200 rounded animate-pulse w-2/3" />
                  <div className="h-8 bg-gray-200 rounded animate-pulse" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="mt-12 flex flex-col gap-4 sm:flex-row sm:justify-center">
        <Link href="/analyze">
          <Button size="lg">New Analysis</Button>
        </Link>
        <Link href="/">
          <Button size="lg" variant="outline">Back to Home</Button>
        </Link>
      </div>
    </div>
  )
}
