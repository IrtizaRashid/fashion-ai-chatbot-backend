"use client"

import { motion } from "framer-motion"
import { Message as MessageType } from "@/lib/types"

interface MessageProps {
  message: MessageType
  isLatest?: boolean
}

export function Message({ message, isLatest }: MessageProps) {
  const isAssistant = message.role === "assistant"

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex gap-3 ${isAssistant ? "justify-start" : "justify-end"}`}
    >
      {isAssistant && (
        <div className="h-7 w-7 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center flex-shrink-0 text-white text-xs font-bold">
          AI
        </div>
      )}

      <div
        className={`max-w-[280px] px-4 py-3 rounded-lg ${
          isAssistant
            ? "bg-slate-800 text-gray-100 border border-purple-500/20"
            : "bg-purple-600/80 text-white"
        }`}
      >
        <div className="text-sm leading-relaxed">
          {message.content.split("\n").map((line, i) => (
            <div key={i}>
              {line.includes("•") ? (
                <p className="mb-1 ml-2">
                  {line.startsWith("•") ? line : line}
                </p>
              ) : line.includes("**") ? (
                <p className="mb-2 font-semibold">
                  {line
                    .replace(/\*\*/g, "")
                    .split(":")
                    .map((part, idx) =>
                      idx === 0 ? `${part}:` : part
                    )
                    .join("")}
                </p>
              ) : (
                <p className="mb-2 last:mb-0">{line}</p>
              )}
            </div>
          ))}
        </div>
      </div>

      {!isAssistant && (
        <div className="h-8 w-8 rounded-full bg-gray-300 flex-shrink-0" />
      )}
    </motion.div>
  )
}
