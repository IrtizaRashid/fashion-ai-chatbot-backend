export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export interface UserData {
  image: File | null;
  imagePreview: string | null;
  height?: string;
  weight?: string;
  gender?: string;
  budget?: string;
  occasion?: string;
  favoriteColor?: string;
  preferredBrand?: string;
}

export interface AnalysisResult {
  bodyType: string;
  recommendations: {
    colors: string[];
    fits: string[];
    shirts: string[];
    reasons: string[];
  };
}
