"use client"

import { useState, useRef } from "react"
import { useRouter } from "next/navigation"
import { Upload, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select } from "@/components/ui/select"

const OCCASIONS = ["Casual", "Office", "Wedding", "Party"]

export function ImageUploadForm() {
  const router = useRouter()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const dropZoneRef = useRef<HTMLDivElement>(null)

  const [image, setImage] = useState<File | null>(null)
  const [preview, setPreview] = useState<string>("")
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
    const newErrors = { ...errors }
    delete newErrors.image

    // Validate file type
    const validTypes = ["image/jpeg", "image/png", "image/webp"]
    if (!validTypes.includes(file.type)) {
      setErrors({ ...newErrors, image: "Only JPG, PNG, and WEBP files are allowed" })
      return
    }

    // Validate file size (10 MB)
    if (file.size > 10 * 1024 * 1024) {
      setErrors({ ...newErrors, image: "File size must be less than 10 MB" })
      return
    }

    setImage(file)
    const reader = new FileReader()
    reader.onload = (e) => {
      setPreview(e.target?.result as string)
    }
    reader.readAsDataURL(file)
  }

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
    // Clear error for this field
    setErrors((prev) => {
      const newErrors = { ...prev }
      delete newErrors[name]
      return newErrors
    })
  }

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!image) {
      newErrors.image = "Please upload an image"
    }

    if (!formData.height) {
      newErrors.height = "Height is required"
    } else if (isNaN(Number(formData.height)) || Number(formData.height) <= 0) {
      newErrors.height = "Height must be a positive number"
    }

    if (!formData.weight) {
      newErrors.weight = "Weight is required"
    } else if (isNaN(Number(formData.weight)) || Number(formData.weight) <= 0) {
      newErrors.weight = "Weight must be a positive number"
    }

    if (!formData.occasion) {
      newErrors.occasion = "Please select an occasion"
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    setLoading(true)

    // Simulate API call
    setTimeout(() => {
      setLoading(false)
      router.push("/results")
    }, 2000)
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
        {/* Image Upload */}
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
                ref={dropZoneRef}
                onDragEnter={handleDragEnter}
                onDragOver={handleDragEnter}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-12 transition-colors ${
                  isDragging
                    ? "border-black bg-black/5"
                    : "border-gray-300 hover:border-black"
                }`}
              >
                <Upload className="h-8 w-8 text-gray-400" />
                <p className="mt-2 font-medium text-black">
                  Drag your photo here
                </p>
                <p className="text-sm text-gray-600">or click to browse</p>
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
                  }}
                  className="absolute -right-2 -top-2 rounded-full bg-red-500 p-2 text-white hover:bg-red-600"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            )}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={handleFileInputChange}
              className="hidden"
            />
            {errors.image && (
              <p className="mt-2 text-sm text-red-500">{errors.image}</p>
            )}
          </CardContent>
        </Card>

        {/* Body Measurements */}
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

        {/* Preferences */}
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

        {/* Submit Button */}
        <Button
          type="submit"
          size="lg"
          className="w-full"
          disabled={loading}
        >
          {loading ? "Analyzing Your Style..." : "Analyze My Style"}
        </Button>
      </form>
    </div>
  )
}
