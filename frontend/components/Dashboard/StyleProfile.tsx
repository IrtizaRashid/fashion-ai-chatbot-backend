"use client"

import { motion } from "framer-motion"
import { ImageIcon, Lightbulb, Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"

export interface ProductCardData {
  brand: string
  title: string
  price?: number | null
  currency?: string
  color?: string | null
  colors?: string[]
  sizes?: string[]
  material?: string | null
  image_url?: string | null
  product_url?: string | null
}

interface StyleProfileProps {
  onImageClick: () => void
  onImageDrop: (file: File) => void
  preview?: string | null
  products?: ProductCardData[]
  productsLoading?: boolean
}

const TIPS = [
  "Wear form-fitting clothes for better analysis",
  "Ensure good natural lighting",
  "Stand straight for accurate measurements",
  "Full body or upper body photos work best",
]

export function StyleProfile({
  onImageClick,
  onImageDrop,
  preview,
  products = [],
  productsLoading = false,
}: StyleProfileProps) {
  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
  }

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    const file = event.dataTransfer.files[0]
    if (file) {
      onImageDrop(file)
    }
  }

  return (
    <div className="flex h-full flex-col border-l border-purple-500/20 bg-gradient-to-br from-slate-900/50 to-purple-900/20">
      <div className="border-b border-blue-500/20 px-8 py-6">
        <div className="mb-2 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-600">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Your Style Profile</h2>
            <p className="text-xs text-purple-300">AI-powered boys recommendations</p>
          </div>
        </div>
      </div>

      <div className="flex-1 space-y-6 overflow-y-auto px-8 py-6">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <div>
            <div className="mb-4 flex items-center gap-2">
              <div className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-600 text-xs font-bold text-white">
                1
              </div>
              <h3 className="text-sm font-semibold tracking-wide text-white">
                UPLOAD YOUR PHOTO
              </h3>
            </div>

            <div
              onClick={onImageClick}
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              className="group relative flex min-h-[430px] cursor-pointer items-center justify-center rounded-xl border-2 border-dashed border-blue-500/60 bg-slate-950/40 p-6 text-center transition-all hover:border-blue-400 hover:bg-blue-500/5"
            >
              {preview ? (
                <motion.div
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className="relative h-full w-full"
                >
                  <img
                    src={preview}
                    alt="Profile"
                    className="max-h-[410px] w-full rounded-lg object-contain"
                  />
                </motion.div>
              ) : (
                <div>
                  <ImageIcon className="mx-auto mb-3 h-8 w-8 text-blue-300" />
                  <p className="text-sm font-semibold text-white">Drag and drop</p>
                  <p className="mt-1 text-xs text-blue-300">
                    JPG, PNG, WEBP, max 10 MB
                  </p>
                  <Button
                    type="button"
                    className="mt-5 bg-blue-600 text-white hover:bg-blue-700"
                    onClick={(event) => {
                      event.stopPropagation()
                      onImageClick()
                    }}
                  >
                    <ImageIcon className="h-4 w-4" />
                    Choose Photo
                  </Button>
                </div>
              )}
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="space-y-3"
        >
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <div className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-600 text-xs font-bold text-white">
                2
              </div>
              <p className="text-xs font-semibold tracking-wide text-white">BOYS PRODUCT PICKS</p>
            </div>
            {productsLoading && <span className="text-xs text-blue-300">Finding items...</span>}
          </div>

          {products.length > 0 ? (
            <div className="grid grid-cols-2 gap-3">
              {products.slice(0, 8).map((product) => (
                <a
                  key={`${product.brand}-${product.product_url ?? product.title}`}
                  href={product.product_url ?? "#"}
                  target="_blank"
                  rel="noreferrer"
                  className="overflow-hidden rounded-lg border border-blue-500/20 bg-slate-950/60 transition hover:border-blue-400/70 hover:bg-slate-900"
                >
                  <div className="aspect-[4/5] bg-slate-900">
                    {product.image_url ? (
                      <img
                        src={product.image_url}
                        alt={product.title}
                        className="h-full w-full object-cover"
                      />
                    ) : (
                      <div className="flex h-full items-center justify-center text-xs text-slate-500">
                        No image
                      </div>
                    )}
                  </div>
                  <div className="space-y-1 p-3">
                    <div className="text-[10px] font-semibold uppercase tracking-wide text-blue-300">
                      {product.brand}
                    </div>
                    <h4 className="line-clamp-2 min-h-[34px] text-xs font-semibold leading-snug text-white">
                      {product.title}
                    </h4>
                    <div className="text-sm font-bold text-white">
                      {product.currency ?? "PKR"} {product.price ?? "-"}
                    </div>
                    {product.sizes?.length ? (
                      <div className="truncate text-[11px] text-slate-400">
                        Sizes: {product.sizes.slice(0, 5).join(", ")}
                      </div>
                    ) : null}
                  </div>
                </a>
              ))}
            </div>
          ) : (
            <div className="rounded-lg border border-blue-500/20 bg-blue-500/5 p-4 text-xs leading-relaxed text-gray-300">
              Product picks will appear here after your analysis.
            </div>
          )}
        </motion.div>

        {!products.length && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="space-y-3"
          >
            <div className="flex items-center gap-2">
              <Lightbulb className="h-4 w-4 text-blue-400" />
              <p className="text-xs font-semibold tracking-wide text-white">PRO TIPS</p>
            </div>

            {TIPS.map((tip, index) => (
              <motion.div
                key={tip}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 + index * 0.1 }}
                className="flex gap-3 rounded-lg border border-blue-500/20 bg-blue-500/5 p-3 transition-colors hover:bg-blue-500/10"
              >
                <div className="mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-blue-500/30">
                  <span className="text-xs font-bold text-blue-300">{index + 1}</span>
                </div>
                <p className="text-xs leading-relaxed text-gray-300">{tip}</p>
              </motion.div>
            ))}
          </motion.div>
        )}

        <div className="pb-4 text-center text-xs text-gray-500">
          <p>Powered by AI Fashion Vision</p>
        </div>
      </div>
    </div>
  )
}

