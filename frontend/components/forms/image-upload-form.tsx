"use client"

import { useRef, useState } from "react"
import { useRouter } from "next/navigation"
import { ImageIcon, Upload, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select } from "@/components/ui/select"

const OCCASIONS = ["Casual", "Office", "Wedding", "Party"]
const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000"
).replace(/\/api\/?$/, "")

export function ImageUploadForm() {
  const router = useRouter()
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [image, setImage] = useState<File | null>(null)
  const [preview, setPreview] = useState("")
  const [isDragging, setIsDragging] = useState(false)
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const [formData, setFormData] = useState({
    height: "",
    weight: "",
    gender: "",
    budget: "",
    occasion: OCCASIONS[0],
    favoriteColor: "",
    preferredBrand: "",
  })

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

    const file = e.dataTransfer.files[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleFileSelect(file)
    }
    e.target.value = ""
  }

  const handleFileSelect = (file: File) => {
    const nextErrors = { ...errors }
    delete nextErrors.image
    delete nextErrors.submit

    const validTypes = ["image/jpeg", "image/png", "image/webp"]
    if (!validTypes.includes(file.type)) {
      setErrors({
        ...nextErrors,
        image: "Only JPG, PNG, and WEBP files are allowed",
      })
      return
    }

    if (file.size > 10 * 1024 * 1024) {
      setErrors({
        ...nextErrors,
        image: "File size must be less than 10 MB",
      })
      return
    }

    setImage(file)
    setErrors(nextErrors)

    const reader = new FileReader()
    reader.onload = (event) => {
      setPreview(String(event.target?.result ?? ""))
    }
    reader.readAsDataURL(file)
  }

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
    setErrors((prev) => {
      const nextErrors = { ...prev }
      delete nextErrors[name]
      delete nextErrors.submit
      return nextErrors
    })
  }

  const validateForm = () => {
    const nextErrors: Record<string, string> = {}

    if (!image) {
      nextErrors.image = "Please upload an image"
    }

    if (!formData.height) {
      nextErrors.height = "Height is required"
    } else if (Number.isNaN(Number(formData.height)) || Number(formData.height) <= 0) {
      nextErrors.height = "Height must be a positive number"
    }

    if (!formData.weight) {
      nextErrors.weight = "Weight is required"
    } else if (Number.isNaN(Number(formData.weight)) || Number(formData.weight) <= 0) {
      nextErrors.weight = "Weight must be a positive number"
    }

    if (!formData.occasion) {
      nextErrors.occasion = "Please select an occasion"
    }

    setErrors(nextErrors)
    return Object.keys(nextErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    setLoading(true)
    sessionStorage.removeItem("fashion-analysis-result")

    try {
      const payload = new FormData()
      payload.append("image", image as File)
      payload.append("height", formData.height)
      payload.append("weight", formData.weight)

      const response = await fetch(`${API_BASE_URL}/analyze-body`, {
        method: "POST",
        body: payload,
      })

      if (!response.ok) {
        const errorBody = await response.json().catch(() => null)
        throw new Error(errorBody?.detail ?? "Image analysis failed")
      }

      const result = await response.json()
      sessionStorage.setItem(
        "fashion-analysis-result",
        JSON.stringify({
          result,
          formData,
          imageName: image?.name,
          analyzedAt: new Date().toISOString(),
          imagePreview: preview,
        })
      )

      router.push("/results")
    } catch (error) {
      setErrors({
        submit:
          error instanceof Error
            ? error.message
            : "Unable to analyze this image. Please try again.",
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold text-black">Analyze Your Style</h1>
        <p className="mt-2 text-gray-600">
          Upload a photo and tell us about yourself to get personalized recommendations.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        <Card>
          <CardHeader>
            <CardTitle>Upload Photo</CardTitle>
            <CardDescription>
              Drag and drop or click to upload. JPG, PNG, or WEBP (max 10 MB)
            </CardDescription>
          </CardHeader>
          <CardContent>
            {!preview ? (
              <div
                onDragEnter={handleDragEnter}
                onDragOver={handleDragEnter}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-12 text-center transition-colors ${
                  isDragging
                    ? "border-black bg-black/5"
                    : "border-gray-300 hover:border-black"
                }`}
              >
                <Upload className="h-8 w-8 text-gray-400" />
                <p className="mt-2 font-medium text-black">Drag your photo here</p>
                <p className="text-sm text-gray-600">or click to browse</p>
                <Button
                  type="button"
                  className="mt-4 bg-black text-white hover:bg-black/90"
                  onClick={(event) => {
                    event.stopPropagation()
                    fileInputRef.current?.click()
                  }}
                >
                  <ImageIcon className="h-4 w-4" />
                  Choose Photo
                </Button>
              </div>
            ) : (
              <div className="relative inline-block w-full">
                <img
                  src={preview}
                  alt="Preview"
                  className="h-64 w-full rounded-lg object-cover"
                />
                <button
                  type="button"
                  onClick={() => {
                    setImage(null)
                    setPreview("")
                    setErrors((prev) => {
                      const nextErrors = { ...prev }
                      delete nextErrors.image
                      delete nextErrors.submit
                      return nextErrors
                    })
                  }}
                  className="absolute -right-2 -top-2 rounded-full bg-red-500 p-2 text-white hover:bg-red-600"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            )}
            <input
              id="photo-upload"
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={handleFileInputChange}
              className="sr-only"
            />
            {errors.image && (
              <p className="mt-2 text-sm text-red-500">{errors.image}</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Body Measurements</CardTitle>
            <CardDescription>These help us recommend the right size</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="height">Height (cm)</Label>
                <Input
                  id="height"
                  name="height"
                  type="number"
                  placeholder="170"
                  value={formData.height}
                  onChange={handleInputChange}
                  min="0"
                />
                {errors.height && (
                  <p className="text-sm text-red-500">{errors.height}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="weight">Weight (kg)</Label>
                <Input
                  id="weight"
                  name="weight"
                  type="number"
                  placeholder="70"
                  value={formData.weight}
                  onChange={handleInputChange}
                  min="0"
                />
                {errors.weight && (
                  <p className="text-sm text-red-500">{errors.weight}</p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Preferences</CardTitle>
            <CardDescription>Help us refine recommendations</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="gender">Gender (optional)</Label>
                <Select
                  id="gender"
                  name="gender"
                  value={formData.gender}
                  onChange={handleInputChange}
                >
                  <option value="">Select gender</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="occasion">Occasion</Label>
                <Select
                  id="occasion"
                  name="occasion"
                  value={formData.occasion}
                  onChange={handleInputChange}
                >
                  {OCCASIONS.map((occ) => (
                    <option key={occ} value={occ}>
                      {occ}
                    </option>
                  ))}
                </Select>
                {errors.occasion && (
                  <p className="text-sm text-red-500">{errors.occasion}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="budget">Budget (PKR, optional)</Label>
                <Input
                  id="budget"
                  name="budget"
                  placeholder="5000"
                  value={formData.budget}
                  onChange={handleInputChange}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="favoriteColor">Favorite Color (optional)</Label>
                <Input
                  id="favoriteColor"
                  name="favoriteColor"
                  placeholder="Blue"
                  value={formData.favoriteColor}
                  onChange={handleInputChange}
                />
              </div>

              <div className="space-y-2 sm:col-span-2">
                <Label htmlFor="preferredBrand">Preferred Brand (optional)</Label>
                <Input
                  id="preferredBrand"
                  name="preferredBrand"
                  placeholder="e.g., Gul Ahmed, Sana Safinaz"
                  value={formData.preferredBrand}
                  onChange={handleInputChange}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <Button type="submit" size="lg" className="w-full" disabled={loading}>
          {loading ? "Analyzing Your Style..." : "Analyze My Style"}
        </Button>
        {errors.submit && (
          <p className="text-center text-sm text-red-500">{errors.submit}</p>
        )}
      </form>
    </div>
  )
}
