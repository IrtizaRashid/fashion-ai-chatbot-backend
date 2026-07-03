"use client"

import { useState, useRef } from "react"
import { motion } from "framer-motion"
import { Upload, X, Image as ImageIcon } from "lucide-react"
import { Button } from "@/components/ui/button"

interface ImageUploaderProps {
  onImageSelect: (file: File, preview: string) => void
  onImageRemove: () => void
  preview?: string | null
}

export function ImageUploader({
  onImageSelect,
  onImageRemove,
  preview,
}: ImageUploaderProps) {
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    const files = e.dataTransfer.files
    if (files.length > 0) {
      handleFileSelect(files[0])
    }
  }

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelect(e.target.files[0])
    }
  }

  const handleFileSelect = (file: File) => {
    const validTypes = ["image/jpeg", "image/png", "image/webp"]
    if (!validTypes.includes(file.type)) {
      alert("Only JPG, PNG, and WEBP files are allowed")
      return
    }

    if (file.size > 10 * 1024 * 1024) {
      alert("File size must be less than 10 MB")
      return
    }

    const reader = new FileReader()
    reader.onload = (e) => {
      onImageSelect(file, e.target?.result as string)
    }
    reader.readAsDataURL(file)
  }

  return (
    <div className="space-y-4">
      {!preview ? (
        <motion.div
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragEnter}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          animate={{
            borderColor: isDragging ? "#ec4899" : "#a855f7",
            backgroundColor: isDragging ? "rgba(236, 72, 153, 0.1)" : "rgba(168, 85, 247, 0.05)",
          }}
          className="border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all hover:border-pink-500 group"
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={handleFileInputChange}
            className="hidden"
          />

          <motion.div
            animate={{ y: isDragging ? -5 : 0 }}
            className="flex justify-center mb-4"
          >
            <div className="w-16 h-16 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center group-hover:scale-110 transition-transform">
              <Upload className="h-8 w-8 text-white" />
            </div>
          </motion.div>

          <p className="font-semibold text-white text-lg">Drag & Drop Your Photo</p>
          <p className="text-purple-200 text-sm mt-2">or click to browse files</p>

          <div className="mt-4 text-xs text-purple-300 space-y-1 bg-purple-500/10 rounded-lg p-3">
            <p className="flex items-center justify-center gap-1">
              <ImageIcon className="w-3 h-3" /> JPG, PNG, WEBP
            </p>
            <p>Max 10 MB</p>
          </div>
        </motion.div>
      ) : (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="relative group"
        >
          <div className="rounded-xl overflow-hidden border-2 border-gradient-to-r from-purple-400 to-pink-400 shadow-2xl">
            <img
              src={preview}
              alt="Preview"
              className="w-full h-64 object-cover group-hover:scale-105 transition-transform duration-300"
            />
          </div>

          <Button
            onClick={onImageRemove}
            size="icon"
            className="absolute -top-3 -right-3 bg-gradient-to-r from-red-500 to-pink-500 hover:from-red-600 hover:to-pink-600 shadow-lg"
          >
            <X className="h-4 w-4" />
          </Button>

          <div className="mt-3 p-3 rounded-lg bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-400/30">
            <p className="text-sm text-purple-200 text-center font-medium">✓ Photo Ready</p>
          </div>
        </motion.div>
      )}
    </div>
  )
}
