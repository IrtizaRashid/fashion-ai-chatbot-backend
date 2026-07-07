"use client"

import { useRef, useState } from "react"
import { ChatContainer } from "@/components/Chat/ChatContainer"
import { ChatInput } from "@/components/Chat/ChatInput"
import { ProductCardData, StyleProfile } from "@/components/Dashboard/StyleProfile"
import { ApiKeyModal } from "@/components/ApiKeyModal"
import { Message as MessageType, UserData } from "@/lib/types"

const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8001"
).replace(/\/api\/?$/, "")

interface GeminiAnalysis {
  body_type?: string
  body_build?: string
  shoulders?: string
  torso?: string
  legs?: string
  neck?: string
  posture?: string
  recommended_fit?: string[]
  recommended_shirts?: string[]
  recommended_trousers?: string[]
  recommended_colors?: string[]
  recommended_patterns?: string[]
  avoid?: string[]
  summary?: string
  disclaimer?: string
}

type ConversationStage =
  | "initial"
  | "image_uploaded"
  | "height_provided"
  | "analysis_complete"

const INITIAL_MESSAGE: MessageType = {
  id: "1",
  role: "assistant",
  content:
    "Hello! I'm your AI Fashion Stylist. Upload your photo on the right to get started with personalized men's styling recommendations.",
  timestamp: new Date(),
}

function extractNumber(input: string) {
  const match = input.match(/\d+(\.\d+)?/)
  return match ? match[0] : ""
}

function validateHeight(height: string) {
  const value = Number(height)
  if (Number.isNaN(value)) return "Please send your height as a number in cm, for example 170."
  if (value < 100) return "That height looks too low. Please enter a height between 100 cm and 250 cm."
  if (value > 250) return "That height looks too high. Please enter a height between 100 cm and 250 cm."
  return null
}

function validateWeight(weight: string) {
  const value = Number(weight)
  if (Number.isNaN(value)) return "Please send your weight as a number in kg, for example 70."
  if (value < 30) return "That weight looks too low. Please enter a weight between 30 kg and 300 kg."
  if (value > 300) return "That weight looks too high. Please enter a weight between 30 kg and 300 kg."
  return null
}


function isMensProductCard(product: ProductCardData) {
  const text = [
    product.brand,
    product.title,
    product.color,
    ...(product.colors ?? []),
    product.material,
    product.product_url,
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase()
    .replaceAll("-", " ")

  const blocked = [
    "girl", "girls", "woman", "women", "ladies", "female", "cropped", "crop top",
    "lace", "skirt", "dress", "blouse", "camisole", "bra", "bralette", "legging",
    "leggings", "frock", "kurti", "dupatta", "heels", "/women", "/girls", "/ladies",
  ]

  return !blocked.some((term) => text.includes(term.replaceAll("-", " ")))
}

function menOnlyProducts(products: ProductCardData[]) {
  return products.filter(isMensProductCard)
}
function formatList(label: string, items?: string[]) {
  if (!items?.length) return undefined
  return `**${label}:** ${items.join(" ")}`
}

function formatAnalysisMessage(result: GeminiAnalysis) {
  return [
    "**Gemini Style Analysis**",
    `- **Body type**: ${result.body_type ?? "Not specified"}`,
    result.body_build ? `- **Build**: ${result.body_build}` : undefined,
    "",
    formatList("Best fits", result.recommended_fit?.slice(0, 2)),
    formatList("Top picks", [
      ...(result.recommended_shirts ?? []).slice(0, 1),
      ...(result.recommended_trousers ?? []).slice(0, 1),
    ]),
    formatList("Colors", result.recommended_colors?.slice(0, 2)),
    formatList("Avoid", result.avoid?.slice(0, 2)),
  ]
    .filter((line): line is string => line !== undefined)
    .join("\n")
}

function buildProductRequest(analysis: GeminiAnalysis | null, message = "") {
  const text = message.toLowerCase()
  const colors = ["black", "white", "blue", "green", "navy", "brown", "grey", "gray", "red"]
    .filter((color) => text.includes(color))
    .map((color) => (color === "gray" ? "Grey" : color.charAt(0).toUpperCase() + color.slice(1)))
  const budgetMatch = text.match(/\d{3,6}/)?.[0]
  const wantsOnly = text.includes("only")
  const wantsShirt = text.includes("shirt") || text.includes("t-shirt") || text.includes("tshirt") || text.includes("tee") || text.includes("polo")
  const wantsPant = text.includes("pant") || text.includes("pants") || text.includes("trouser") || text.includes("trousers") || text.includes("jean") || text.includes("jeans") || text.includes("chino")

  const requestedTops = [
    text.includes("polo") ? "Polo Shirt" : undefined,
    text.includes("t-shirt") || text.includes("tshirt") || text.includes("tee") ? "T-Shirt" : undefined,
    wantsShirt ? "Shirt" : undefined,
  ].filter((item): item is string => Boolean(item))

  const requestedBottoms = [
    text.includes("jean") || text.includes("jeans") ? "Jeans" : undefined,
    text.includes("chino") ? "Chinos" : undefined,
    wantsPant || text.includes("trouser") || text.includes("trousers") ? "Trousers" : undefined,
  ].filter((item): item is string => Boolean(item))

  let products: string[] = []
  if (wantsOnly && wantsShirt && !wantsPant) {
    products = requestedTops.length ? requestedTops : ["Shirt", "Polo Shirt", "T-Shirt"]
  } else if (wantsOnly && wantsPant && !wantsShirt) {
    products = requestedBottoms.length ? requestedBottoms : ["Trousers", "Jeans", "Chinos"]
  } else if (wantsShirt || wantsPant) {
    products = [...requestedTops, ...requestedBottoms]
  } else {
    products = [
      ...(analysis?.recommended_shirts?.slice(0, 3) ?? ["Shirt", "Polo Shirt", "T-Shirt"]),
      ...(analysis?.recommended_trousers?.slice(0, 3) ?? ["Trousers", "Jeans", "Chinos"]),
    ]
  }

  return {
    recommended_fit: analysis?.recommended_fit?.slice(0, 2) ?? ["Regular Fit"],
    recommended_shirts: Array.from(new Set(products)),
    recommended_colors:
      colors.length > 0
        ? colors
        : analysis?.recommended_colors?.length
          ? analysis.recommended_colors.slice(0, 3)
          : ["Black", "Blue", "White"],
    budget: budgetMatch ? Number(budgetMatch) : 10000,
  }
}

function isProductRequest(message: string) {
  const text = message.toLowerCase()
  return [
    "show me", "give me", "find me", "link", "links", "website", "websites",
    "product", "products", "buy", "under", "budget", "price", "shirt", "polo",
    "t-shirt", "tshirt", "pant", "pants", "trouser", "jeans", "cotton", "only",
    "remove", "outfitters", "breakout", "formal", "casual",
  ].some((word) => text.includes(word))
}

function formatProductLinks(products: ProductCardData[], message: string) {
  if (!products.length) {
    return "I could not find boys products for that request in the saved list. Try a broader request like: show me black shirts under 10000."
  }

  const topProducts = products.slice(0, 5)
  return [
    `I found ${products.length} boys products for: "${message}"`,
    "",
    ...topProducts.map((product, index) => {
      const price = product.price ? `${product.currency ?? "PKR"} ${product.price}` : "Price not shown"
      return `${index + 1}. ${product.brand} - ${product.title} (${price})\n${product.product_url ?? ""}`
    }),
    "",
    "I updated the product cards on the right from your saved recommendations.",
  ].join("\n")
}

function formatAutomaticProductIntro(products: ProductCardData[]) {
  if (!products.length) {
    return "I analyzed your style profile, but I could not find matching boys products right now. Try asking: show me boys black shirts under 5000."
  }

  const topProducts = products.slice(0, 5)
  return [
    "These shirts and pants should fit your body profile and look suitable on you. Please try these options:",
    "",
    ...topProducts.map((product, index) => {
      const price = product.price ? `${product.currency ?? "PKR"} ${product.price}` : "Price not shown"
      return `${index + 1}. ${product.brand} - ${product.title} (${price})\n${product.product_url ?? ""}`
    }),
    "",
    "I saved these recommendations, so follow-up filters will reuse this list instead of searching websites again.",
  ].join("\n")
}

export default function Home() {
  const [geminiApiKey, setGeminiApiKey] = useState<string | null>(null)
  const [messages, setMessages] = useState<MessageType[]>([INITIAL_MESSAGE])
  const [isLoading, setIsLoading] = useState(false)
  const [productsLoading, setProductsLoading] = useState(false)
  const [products, setProducts] = useState<ProductCardData[]>([])
  const [sessionId, setSessionId] = useState(() => `fashion-${Date.now()}-${Math.random().toString(16).slice(2)}`)
  const [userData, setUserData] = useState<UserData>({ image: null, imagePreview: null })
  const [analysisResult, setAnalysisResult] = useState<GeminiAnalysis | null>(null)

  const fileInputRef = useRef<HTMLInputElement>(null)
  const conversationStageRef = useRef<ConversationStage>("initial")

  const selectImageFile = (file: File) => {
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
    reader.onload = (event) => handleImageSelect(file, String(event.target?.result ?? ""))
    reader.readAsDataURL(file)
  }

  const handleImageSelect = (file: File, preview: string) => {
    setSessionId(`fashion-${Date.now()}-${Math.random().toString(16).slice(2)}`)
    setUserData({ image: file, imagePreview: preview })
    conversationStageRef.current = "image_uploaded"
    setAnalysisResult(null)
    setProducts([])
    setIsLoading(false)
    setProductsLoading(false)
    setMessages([
      { id: Date.now().toString(), role: "user", content: `Photo uploaded: ${file.name}`, timestamp: new Date() },
      { id: (Date.now() + 1).toString(), role: "assistant", content: "New photo received. I am starting fresh. What is your height in cm?", timestamp: new Date() },
    ])
  }

  const analyzeCurrentImage = async (height: string, weight: string) => {
    if (!userData.image) throw new Error("Please upload an image first.")
    if (!geminiApiKey) throw new Error("Please provide your Gemini API key.")

    const payload = new FormData()
    payload.append("image", userData.image)
    payload.append("height", height)
    payload.append("weight", weight)
    payload.append("gemini_api_key", geminiApiKey)

    const response = await fetch(`${API_BASE_URL}/analyze-body`, { method: "POST", body: payload })
    if (!response.ok) {
      const errorBody = await response.json().catch(() => null)
      throw new Error(errorBody?.detail ?? "Gemini analysis failed.")
    }
    return (await response.json()) as GeminiAnalysis
  }

  const searchRankAndCacheProducts = async (analysis: GeminiAnalysis, message = "") => {
    setProductsLoading(true)
    try {
      const searchResponse = await fetch(`${API_BASE_URL}/search-products`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(buildProductRequest(analysis, message)),
      })
      if (!searchResponse.ok) throw new Error("Product search failed.")
      const searchData = (await searchResponse.json()) as { products: ProductCardData[] }
      const searchedProducts = menOnlyProducts(searchData.products ?? [])

      const rankResponse = await fetch(`${API_BASE_URL}/recommend`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          body_analysis: analysis,
          products: searchedProducts,
          budget: buildProductRequest(analysis, message).budget,
        }),
      })
      if (!rankResponse.ok) throw new Error("Ranking failed.")
      const rankData = (await rankResponse.json()) as { recommendations: ProductCardData[] }
      const rankedProducts = menOnlyProducts(rankData.recommendations ?? [])

      await fetch(`${API_BASE_URL}/sessions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          body_analysis: analysis,
          recommendations: rankedProducts,
        }),
      })

      setProducts(rankedProducts)
      return rankedProducts
    } catch {
      setProducts([])
      return []
    } finally {
      setProductsLoading(false)
    }
  }

  const filterCachedProducts = async (message: string) => {
    setProductsLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, message }),
      })
      if (!response.ok) throw new Error("Cached filter failed.")
      const data = (await response.json()) as { reply: string; recommendations: ProductCardData[] }
      const foundProducts = menOnlyProducts(data.recommendations ?? [])
      setProducts(foundProducts)
      return { reply: data.reply, products: foundProducts }
    } catch {
      const fallbackProducts = analysisResult ? await searchRankAndCacheProducts(analysisResult, message) : []
      return { reply: formatProductLinks(menOnlyProducts(fallbackProducts), message), products: menOnlyProducts(fallbackProducts) }
    } finally {
      setProductsLoading(false)
    }
  }

  const chatWithGemini = async (message: string) => {
    const response = await fetch(`${API_BASE_URL}/chat-gemini`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, analysis: analysisResult }),
    })
    if (!response.ok) {
      const errorBody = await response.json().catch(() => null)
      throw new Error(errorBody?.detail ?? "Gemini chat failed.")
    }
    const data = (await response.json()) as { message: string }
    return data.message
  }

  const handleSendMessage = async (content: string) => {
    const userMessage: MessageType = { id: Date.now().toString(), role: "user", content, timestamp: new Date() }
    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    let responseText = ""

    if (conversationStageRef.current === "image_uploaded") {
      const height = extractNumber(content)
      const heightError = height ? validateHeight(height) : null
      if (!height) responseText = "Please send your height as a number in cm, for example 170."
      else if (heightError) responseText = heightError
      else {
        setUserData((prev) => ({ ...prev, height }))
        conversationStageRef.current = "height_provided"
        responseText = "Perfect. Now what is your weight in kg?"
      }
    } else if (conversationStageRef.current === "height_provided") {
      const weight = extractNumber(content)
      const weightError = weight ? validateWeight(weight) : null
      const height = userData.height
      if (!weight) responseText = "Please send your weight as a number in kg, for example 70."
      else if (weightError) responseText = weightError
      else if (!height) {
        conversationStageRef.current = "image_uploaded"
        responseText = "I missed your height. Please send your height in cm again."
      } else {
        setUserData((prev) => ({ ...prev, weight }))
        setMessages((prev) => [...prev, { id: (Date.now() + 1).toString(), role: "assistant", content: "Analyzing your image with Gemini now...", timestamp: new Date() }])
        try {
          const result = await analyzeCurrentImage(height, weight)
          setAnalysisResult(result)
          conversationStageRef.current = "analysis_complete"
          const foundProducts = await searchRankAndCacheProducts(result)
          responseText = [formatAnalysisMessage(result), "", formatAutomaticProductIntro(foundProducts)].join("\n")
        } catch (error) {
          responseText = error instanceof Error ? error.message : "I could not analyze this image. Please upload it again."
        }
      }
    } else if (conversationStageRef.current === "analysis_complete") {
      try {
        if (isProductRequest(content)) {
          const result = await filterCachedProducts(content)
          responseText = [result.reply, "", formatProductLinks(result.products, content)].join("\n")
        } else {
          responseText = await chatWithGemini(content)
        }
      } catch (error) {
        responseText = error instanceof Error ? error.message : "I could not answer that right now."
      }
    } else {
      responseText = "Please upload a photo first so I can start the style analysis."
    }

    setMessages((prev) => [...prev, { id: (Date.now() + 2).toString(), role: "assistant", content: responseText, timestamp: new Date() }])
    setIsLoading(false)
  }

  return (
    <div className="flex h-screen overflow-hidden bg-slate-950">
      {!geminiApiKey && <ApiKeyModal onSubmit={setGeminiApiKey} />}

      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        className="hidden"
        onChange={(event) => {
          const file = event.target.files?.[0]
          if (file) selectImageFile(file)
          event.target.value = ""
        }}
      />

      <div className="relative z-10 flex w-[45%] flex-col border-r border-blue-500/10">
        <div className="border-b border-blue-500/10 bg-slate-900/50 px-8 py-4 backdrop-blur-sm">
          <h1 className="text-lg font-bold text-white">AI Fashion Stylist</h1>
          <p className="mt-1 text-xs text-purple-300">Men's-only product picks</p>
        </div>

        <ChatContainer messages={messages} isLoading={isLoading} />

        <div className="border-t border-blue-500/10 bg-slate-900/50 px-8 py-6 backdrop-blur-sm">
          <ChatInput
            onSend={handleSendMessage}
            disabled={isLoading || !userData.imagePreview}
            placeholder={userData.imagePreview ? "Reply with height, weight, or ask for styling..." : "Upload a photo to unlock chat..."}
          />
          {!userData.imagePreview && (
            <p className="mt-2 text-center text-xs text-gray-500">Upload a photo first to start chatting</p>
          )}
        </div>
      </div>

      <div className="relative z-10 flex w-[55%] flex-col">
        <StyleProfile
          onImageClick={() => fileInputRef.current?.click()}
          onImageDrop={selectImageFile}
          preview={userData.imagePreview}
          products={products}
          productsLoading={productsLoading}
        />
      </div>
    </div>
  )
}


