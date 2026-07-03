"use client"

import { motion } from "framer-motion"
import { Sparkles, Lightbulb } from "lucide-react"

interface StyleProfileProps {
  hasImage: boolean
  onImageClick: () => void
  preview?: string | null
}

const BODY_SHAPES = [
  { name: "Rectangle", icon: "▭" },
  { name: "Hourglass", icon: "⧖" },
  { name: "Pear", icon: "🍐" },
  { name: "Apple", icon: "🍎" },
]

const TIPS = [
  "Wear form-fitting clothes for better analysis",
  "Ensure good natural lighting",
  "Stand straight for accurate measurements",
  "Full body or upper body photos work best",
]

export function StyleProfile({
  hasImage,
  onImageClick,
  preview,
}: StyleProfileProps) {
  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-slate-900/50 to-purple-900/20 border-l border-purple-500/20">
      {/* Header Section */}
      <div className="px-8 py-6 border-b border-blue-500/20">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Your Style Profile</h2>
            <p className="text-xs text-purple-300">AI-powered recommendations</p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto space-y-6 px-8 py-6">
        {/* Step 1: Upload */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="flex items-center justify-center w-6 h-6 rounded-full bg-blue-600 text-white text-xs font-bold">
                1
              </div>
              <h3 className="text-sm font-semibold text-white tracking-wide">
                UPLOAD YOUR PHOTO
              </h3>
            </div>

            {/* Upload Area */}
            <div
              onClick={onImageClick}
              className="group relative border-2 border-dashed border-blue-500/60 rounded-xl p-12 py-20 text-center cursor-pointer transition-all hover:border-blue-400 hover:bg-blue-500/5"
            >
              {preview ? (
                <motion.div
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className="relative"
                >
                  <img
                    src={preview}
                    alt="Profile"
                    className="w-full h-40 object-cover rounded-lg"
                  />
                  <div className="absolute inset-0 rounded-lg bg-gradient-to-t from-black/30 to-transparent flex items-end p-3">
                    <span className="text-xs text-white font-semibold">✓ Photo Uploaded</span>
                  </div>
                </motion.div>
              ) : (
                <>
                  <div className="text-3xl mb-3">📸</div>
                  <p className="text-sm font-semibold text-white">Drag & Drop</p>
                  <p className="text-xs text-blue-300 mt-1">JPG, PNG, WEBP (Max 10MB)</p>
                </>
              )}
            </div>
          </div>

          {/* Image Preview Area */}
          {hasImage && preview && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
              className="rounded-xl overflow-hidden border-2 border-blue-500/40 shadow-xl"
            >
              <img
                src={preview}
                alt="Profile Preview"
                className="w-full h-48 object-cover"
              />
            </motion.div>
          )}
        </motion.div>

        {/* Tips Section */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="space-y-3"
        >
          <div className="flex items-center gap-2">
            <Lightbulb className="w-4 h-4 text-blue-400" />
            <p className="text-xs font-semibold text-white tracking-wide">PRO TIPS</p>
          </div>

          {TIPS.map((tip, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 + idx * 0.1 }}
              className="flex gap-3 p-3 rounded-lg bg-blue-500/5 border border-blue-500/20 hover:bg-blue-500/10 transition-colors"
            >
              <div className="flex-shrink-0 w-5 h-5 rounded-full bg-blue-500/30 flex items-center justify-center mt-0.5">
                <span className="text-xs font-bold text-blue-300">{idx + 1}</span>
              </div>
              <p className="text-xs text-gray-300 leading-relaxed">{tip}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* Spacer */}
        <div className="flex-1" />

        {/* Footer Info */}
        <div className="text-center text-xs text-gray-500 pb-4">
          <p>Powered by AI Fashion Vision</p>
        </div>
      </div>
    </div>
  )
}
