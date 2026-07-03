"use client"

import { useState, useRef } from "react"
import { ChatContainer } from "@/components/Chat/ChatContainer"
import { ChatInput } from "@/components/Chat/ChatInput"
import { StyleProfile } from "@/components/Dashboard/StyleProfile"
import { Message as MessageType, UserData } from "@/lib/types"

const MOCK_RESPONSES = [
  {
    trigger: "image_uploaded",
    response:
      "Great! I've received your photo. I can see you clearly. Now, what is your height? (Please provide in cm or feet/inches)",
  },
  {
    trigger: "height_provided",
    response:
      "Perfect, thank you. Now, what is your weight? (Please provide in kg or lbs)",
  },
  {
    trigger: "weight_provided",
    response:
      "Excellent! I'm analyzing your body shape and proportions...\n\n**Your Analysis:**\n• **Body Type**: Athletic build with balanced proportions\n• **Shoulders**: Slightly broad, perfect for structured styles\n• **Best Fits**: Slim fit and tailored garments\n• **Power Colors**: Navy, black, olive, burgundy\n• **Avoid**: Oversized or baggy cuts\n\nReady for style recommendations for casual, office, or formal occasions?",
  },
]

export default function Home() {
  const [messages, setMessages] = useState<MessageType[]>([
    {
      id: "1",
      role: "assistant",
      content:
        "Hello! I'm your AI Fashion Stylist. Upload your photo on the right to get started with personalized styling recommendations.",
      timestamp: new Date(),
    },
  ])

  const [isLoading, setIsLoading] = useState(false)
  const [userData, setUserData] = useState<UserData>({
    image: null,
    imagePreview: null,
  })
  const fileInputRef = useRef<HTMLInputElement>(null)
  const conversationStageRef = useRef<
    "initial" | "image_uploaded" | "height_provided" | "weight_provided"
  >("initial")

  const handleImageSelect = async (file: File, preview: string) => {
    setUserData((prev) => ({
      ...prev,
      image: file,
      imagePreview: preview,
    }))

    const userMessage: MessageType = {
      id: Date.now().toString(),
      role: "user",
      content: "📸 Photo uploaded",
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)
    conversationStageRef.current = "image_uploaded"

    await new Promise((resolve) => setTimeout(resolve, 1500))

    const response: MessageType = {
      id: (Date.now() + 1).toString(),
      role: "assistant",
      content: MOCK_RESPONSES[0].response,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, response])
    setIsLoading(false)
  }

  const handleImageRemove = () => {
    setUserData((prev) => ({
      ...prev,
      image: null,
      imagePreview: null,
    }))
    conversationStageRef.current = "initial"
    setMessages([
      {
        id: "1",
        role: "assistant",
        content:
          "Hello! I'm your AI Fashion Stylist. Upload your photo on the right to get started with personalized styling recommendations.",
        timestamp: new Date(),
      },
    ])
  }

  const handleSendMessage = async (content: string) => {
    const userMessage: MessageType = {
      id: Date.now().toString(),
      role: "user",
      content,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    await new Promise((resolve) => setTimeout(resolve, 1200))

    let responseText = ""

    if (
      conversationStageRef.current === "image_uploaded" &&
      !userData.height
    ) {
      userData.height = content
      conversationStageRef.current = "height_provided"
      responseText = MOCK_RESPONSES[1].response
    } else if (
      conversationStageRef.current === "height_provided" &&
      !userData.weight
    ) {
      userData.weight = content
      conversationStageRef.current = "weight_provided"
      responseText = MOCK_RESPONSES[2].response
    } else {
      responseText =
        "I'd love to help you find the perfect styles! What type of occasion are you shopping for—casual, office, or formal wear?"
    }

    const response: MessageType = {
      id: (Date.now() + 1).toString(),
      role: "assistant",
      content: responseText,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, response])
    setIsLoading(false)
  }

  return (
    <div className="flex h-screen bg-slate-950 overflow-hidden">
      {/* Subtle background gradient */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-0 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-pink-500/5 rounded-full blur-3xl"></div>
      </div>

      {/* Hidden file input */}
      <input ref={fileInputRef} type="file" className="hidden" />

      {/* Left Column - Chat (45%) */}
      <div className="w-[45%] flex flex-col relative z-10 border-r border-purple-500/10">
        {/* Slim Header */}
        <div className="px-8 py-4 border-b border-purple-500/10 bg-slate-900/50 backdrop-blur-sm">
          <h1 className="text-lg font-bold text-white">AI Fashion Stylist</h1>
          <p className="text-xs text-purple-300 mt-1">Your personal style assistant</p>
        </div>

        {/* Chat Area */}
        <ChatContainer messages={messages} isLoading={isLoading} />

        {/* Chat Input */}
        <div className="px-8 py-6 border-t border-purple-500/10 bg-slate-900/50 backdrop-blur-sm">
          <ChatInput
            onSend={handleSendMessage}
            disabled={isLoading || !userData.imagePreview}
            placeholder={
              userData.imagePreview
                ? "Ask me about your style..."
                : "Upload a photo to unlock chat..."
            }
          />
          {!userData.imagePreview && (
            <p className="text-xs text-gray-500 mt-2 text-center">
              Upload a photo first to start chatting
            </p>
          )}
        </div>
      </div>

      {/* Right Column - Dashboard (55%) */}
      <div className="w-[55%] relative z-10 flex flex-col">
        <StyleProfile
          hasImage={!!userData.imagePreview}
          onImageClick={() => fileInputRef.current?.click()}
          preview={userData.imagePreview}
        />
      </div>
    </div>
  )
}
