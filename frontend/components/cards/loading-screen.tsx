"use client"

import { useEffect, useState } from "react"

const MESSAGES = [
  "Analyzing your body shape...",
  "Understanding proportions...",
  "Finding suitable styles...",
  "Preparing recommendations...",
]

export function LoadingScreen() {
  const [currentMessage, setCurrentMessage] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentMessage((prev) => (prev + 1) % MESSAGES.length)
    }, 2000)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="flex min-h-screen items-center justify-center bg-white">
      <div className="flex flex-col items-center gap-8">
        <div className="flex gap-2">
          <div className="h-3 w-3 animate-bounce rounded-full bg-black [animation-delay:0ms]" />
          <div className="h-3 w-3 animate-bounce rounded-full bg-black [animation-delay:150ms]" />
          <div className="h-3 w-3 animate-bounce rounded-full bg-black [animation-delay:300ms]" />
        </div>

        <div className="h-8">
          <p className="animate-fade-in text-center text-lg text-gray-600">
            {MESSAGES[currentMessage]}
          </p>
        </div>
      </div>

      <style jsx>{`
        @keyframes fade-in {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        .animate-fade-in {
          animation: fade-in 0.5s ease-in-out;
        }
      `}</style>
    </div>
  )
}
