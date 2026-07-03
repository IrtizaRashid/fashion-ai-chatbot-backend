"use client"

import { useEffect, useRef } from "react"
import { motion } from "framer-motion"
import { Message } from "./Message"
import { TypingIndicator } from "./TypingIndicator"
import { Message as MessageType } from "@/lib/types"

interface ChatContainerProps {
  messages: MessageType[]
  isLoading?: boolean
}

export function ChatContainer({ messages, isLoading }: ChatContainerProps) {
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, isLoading])

  return (
    <motion.div
      ref={scrollRef}
      className="flex-1 overflow-y-auto space-y-4 p-6 bg-slate-900/50"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      {messages.length === 0 ? (
        <div className="flex items-center justify-center h-full">
          <div className="text-center max-w-xs">
            <div className="text-4xl mb-4">✨</div>
            <h2 className="text-xl font-bold text-white mb-2">
              Ready to discover your style?
            </h2>
            <p className="text-sm text-gray-400 leading-relaxed">
              Upload a photo on the right panel to get personalized clothing recommendations based on your body type.
            </p>
          </div>
        </div>
      ) : (
        <>
          {messages.map((message) => (
            <Message key={message.id} message={message} />
          ))}
          {isLoading && <TypingIndicator />}
        </>
      )}
    </motion.div>
  )
}
