"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { motion } from "framer-motion"

interface ApiKeyModalProps {
  onSubmit: (apiKey: string) => void
}

export function ApiKeyModal({ onSubmit }: ApiKeyModalProps) {
  const [apiKey, setApiKey] = useState("")
  const [error, setError] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!apiKey.trim()) {
      setError("Please enter your Gemini API key")
      return
    }
    onSubmit(apiKey)
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4"
    >
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="bg-gradient-to-br from-slate-900 to-slate-800 p-8 rounded-xl border border-blue-500/20 max-w-md w-full"
      >
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-white mb-2">
            Enter Your Gemini API Key
          </h2>
          <p className="text-sm text-gray-400">
            Your key is only used for this session and never stored.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-semibold text-gray-200 mb-2">
              API Key
            </label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => {
                setApiKey(e.target.value)
                setError("")
              }}
              placeholder="Paste your Gemini API key here..."
              className="w-full px-4 py-3 bg-slate-800 border border-slate-700 text-white placeholder-gray-500 rounded-lg focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500/50"
            />
            <p className="text-xs text-gray-500 mt-2">
              Get your key from{" "}
              <a
                href="https://ai.google.dev/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-400 hover:text-blue-300 underline"
              >
                ai.google.dev
              </a>
            </p>
          </div>

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-3 bg-red-500/10 border border-red-500/50 rounded-lg text-sm text-red-200"
            >
              {error}
            </motion.div>
          )}

          <Button
            type="submit"
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition-colors"
          >
            Continue
          </Button>
        </form>

        <p className="text-xs text-gray-500 text-center mt-4">
          🔒 Your key is secure and never stored permanently
        </p>
      </motion.div>
    </motion.div>
  )
}
