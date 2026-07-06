"use client"

import { motion } from "framer-motion"
import { Message as MessageType } from "@/lib/types"

interface MessageProps {
  message: MessageType
}

function renderLine(line: string) {
  const parts = line.split(/(https?:\/\/[^\s]+)/g)

  return parts.map((part, index) => {
    if (part.startsWith("http://") || part.startsWith("https://")) {
      return (
        <a
          key={`${part}-${index}`}
          href={part}
          target="_blank"
          rel="noreferrer"
          className="break-words text-blue-300 underline underline-offset-2 hover:text-blue-200"
        >
          Open product
        </a>
      )
    }

    return <span key={`${part}-${index}`}>{part}</span>
  })
}

export function Message({ message }: MessageProps) {
  const isAssistant = message.role === "assistant"

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex gap-3 ${isAssistant ? "justify-start" : "justify-end"}`}
    >
      {isAssistant && (
        <div className="h-7 w-7 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0 text-white text-xs font-bold">
          AI
        </div>
      )}

      <div
        className={`max-w-[360px] px-4 py-3 rounded-lg ${
          isAssistant
            ? "bg-slate-800 text-gray-100 border border-blue-500/20"
            : "bg-blue-600/80 text-white"
        }`}
      >
        <div className="text-sm leading-relaxed">
          {message.content.split("\n").map((line, i) => (
            <div key={i}>
              {line.includes("**") ? (
                <p className="mb-2 font-semibold">
                  {renderLine(line.replace(/\*\*/g, ""))}
                </p>
              ) : (
                <p className="mb-2 last:mb-0">{renderLine(line)}</p>
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
