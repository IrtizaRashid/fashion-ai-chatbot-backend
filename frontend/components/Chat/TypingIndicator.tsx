"use client"

import { motion } from "framer-motion"

export function TypingIndicator() {
  return (
    <div className="flex gap-2 items-center">
      <div className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0 text-white text-sm font-bold">
        ✨
      </div>
      <div className="flex gap-1 bg-gradient-to-r from-purple-600/40 to-pink-600/40 px-4 py-3 rounded-xl border border-purple-400/30 backdrop-blur-sm">
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            className="w-2 h-2 bg-gradient-to-r from-purple-300 to-pink-300 rounded-full"
            animate={{ opacity: [0.4, 1, 0.4] }}
            transition={{
              duration: 0.6,
              repeat: Infinity,
              delay: i * 0.1,
            }}
          />
        ))}
      </div>
    </div>
  )
}
