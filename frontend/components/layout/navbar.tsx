"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { ExternalLink } from "lucide-react"

export function Navbar() {
  return (
    <nav className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center gap-2">
          <span className="text-2xl font-bold">✨</span>
          <span className="hidden text-xl font-semibold sm:inline">
            AI Fashion Stylist
          </span>
          <span className="text-xl font-semibold sm:hidden">AFS</span>
        </Link>

        <div className="flex items-center gap-6">
          <Link
            href="/"
            className="text-sm font-medium text-gray-600 hover:text-black"
          >
            Home
          </Link>
          <Link
            href="/analyze"
            className="text-sm font-medium text-gray-600 hover:text-black"
          >
            Analyze
          </Link>
          <Button
            variant="ghost"
            size="icon"
            className="hover:bg-gray-100"
            onClick={() => window.open("https://github.com", "_blank")}
          >
            <ExternalLink className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </nav>
  )
}
