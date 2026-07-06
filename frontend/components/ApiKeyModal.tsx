"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { motion } from "framer-motion"
import { Key, Shield } from "lucide-react"

interface ApiKeyModalProps {
  onSubmit: (apiKey: string) => void
}

export function ApiKeyModal({ onSubmit }: ApiKeyModalProps) {
  const [apiKey, setApiKey] = useState("")
  const [error, setError] = useState("")
  const [showKey, setShowKey] = useState(false)

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
      className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4"
    >
      <motion.div
        initial={{ scale: 0.95, opacity: 0, y: 20 }}
        animate={{ scale: 1, opacity: 1, y: 0 }}
        className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8 rounded-2xl border border-blue-500/30 max-w-lg w-full shadow-2xl"
      >
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-full bg-blue-600 flex items-center justify-center">
              <Key className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-3xl font-bold text-white">API Key Required</h2>
              <p className="text-sm text-blue-300">One-time setup to get started</p>
            </div>
          </div>
        </div>

        {/* Instructions */}
        <div className="bg-slate-700/30 border border-blue-500/20 rounded-lg p-4 mb-6">
          <p className="text-sm text-gray-200 leading-relaxed">
            You need a <span className="font-semibold text-blue-300">Google Gemini API Key</span> to use this fashion stylist app.
            Don't worry — your key is only used during this session and never saved or stored anywhere.
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Input Field */}
          <div>
            <label className="block text-sm font-bold text-white mb-3">
              Paste Your API Key
            </label>
            <div className="relative">
              <input
                type={showKey ? "text" : "password"}
                value={apiKey}
                onChange={(e) => {
                  setApiKey(e.target.value)
                  setError("")
                }}
                placeholder="AQ.Ab8RN6KuIJLOnU8N_Yk0oF0VOPcdggIz..."
                className="w-full px-4 py-3 bg-slate-800 border border-slate-600 text-white placeholder-gray-600 rounded-lg focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all"
              />
              <button
                type="button"
                onClick={() => setShowKey(!showKey)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-200 text-sm"
              >
                {showKey ? "Hide" : "Show"}
              </button>
            </div>
            <p className="text-xs text-gray-400 mt-3">
              Don't have a key?{" "}
              <a
                href="https://ai.google.dev/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-400 hover:text-blue-300 underline font-semibold"
              >
                Get it free from Google AI Studio
              </a>
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-3 bg-red-500/15 border border-red-500/50 rounded-lg text-sm text-red-200 flex items-start gap-2"
            >
              <span className="text-lg">⚠️</span>
              <span>{error}</span>
            </motion.div>
          )}

          {/* Submit Button */}
          <Button
            type="submit"
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-lg transition-all hover:shadow-lg hover:shadow-blue-600/50"
          >
            Start Styling →
          </Button>
        </form>

        {/* Security Footer */}
        <div className="flex items-center justify-center gap-2 mt-6 text-xs text-gray-400">
          <Shield className="w-4 h-4 text-green-400" />
          <span>Your key stays on your device. We never store it.</span>
        </div>
      </motion.div>
    </motion.div>
  )
}
