# AI Fashion Stylist - Frontend (Phase 2)

A modern, responsive Next.js frontend for the AI Fashion Stylist application. This phase focuses on building a polished UI that can later connect to the backend.

## 🎯 Features

- **Landing Page** - Hero section with call-to-action buttons and brand information
- **Analysis Page** - Professional image upload form with:
  - Drag-and-drop image upload
  - Body measurement inputs (height, weight)
  - Preference selections (gender, occasion, budget, color, brand)
  - Form validation
  - Real-time error messages
- **Results Page** - Beautiful placeholder cards for displaying results
- **Loading Screen** - Animated progress indicator with rotating messages
- **Responsive Navigation** - Navbar and footer on all pages
- **Mobile-First Design** - Fully responsive on desktop, tablet, and mobile

## 🛠️ Tech Stack

- **Next.js 15** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS
- **React Hook Form** - Form management (ready to integrate)
- **Lucide React** - Icon library

## 📦 Installation

```bash
npm install
```

## 🚀 Running the Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## 📁 Project Structure

```
frontend/
├── app/
│   ├── page.tsx              # Landing page
│   ├── analyze/
│   │   └── page.tsx          # Analysis page
│   ├── results/
│   │   └── page.tsx          # Results page
│   ├── layout.tsx            # Root layout with navbar/footer
│   └── globals.css           # Global styles
├── components/
│   ├── ui/                   # Reusable UI components
│   ├── layout/               # Layout components (navbar, footer)
│   ├── forms/                # Form components
│   └── cards/                # Card components
├── lib/
│   ├── types.ts              # TypeScript types
│   └── utils.ts              # Utility functions
└── package.json
```

## 🎨 Design System

- **Colors**: Black, white, gray palette (Apple-inspired, minimal)
- **Spacing**: Consistent padding/margin using Tailwind scale
- **Components**: Reusable, composable UI elements
- **Responsive**: Mobile-first design approach

## ✅ Completed

- Landing page with hero section and features
- Image upload form with validation
- Body measurements inputs (height, weight)
- Preference options (gender, occasion, budget, color, brand)
- Results page with placeholder cards
- Fully responsive design
- Navigation bar and footer
- Loading states with skeletons
- Form error handling

## 🔄 Ready for Backend Integration

The form component is structured to easily connect to the backend API. When ready, update:

1. `components/forms/image-upload-form.tsx` - Connect to POST `/analyze`
2. `app/results/page.tsx` - Display actual results from backend

All fields match backend requirements:
- `image` (File)
- `height`, `weight` (numbers)
- `gender`, `budget`, `occasion`, `favorite_color`, `preferred_brand`

## 📝 Next Steps

1. Build backend API (Phase 2)
2. Connect frontend to backend (Phase 3)
3. Implement AI analysis results display
4. Add payment/subscription features
5. Deploy to production
