import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"

interface ResultCardProps {
  title: string
  items?: string[]
  loading?: boolean
  type?: "list" | "grid"
}

export function ResultCard({
  title,
  items = [],
  loading = true,
  type = "list",
}: ResultCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
          </div>
        ) : items.length === 0 ? (
          <p className="text-sm text-gray-500">No recommendations available.</p>
        ) : type === "grid" ? (
          <div className="grid gap-2 sm:grid-cols-2">
            {items.map((item, index) => (
              <div
                key={index}
                className="rounded-lg bg-gray-50 px-3 py-2 text-sm text-gray-700"
              >
                {item}
              </div>
            ))}
          </div>
        ) : (
          <ul className="space-y-2">
            {items.map((item, index) => (
              <li key={index} className="flex items-start gap-2 text-sm">
                <span className="text-gray-400">-</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  )
}
