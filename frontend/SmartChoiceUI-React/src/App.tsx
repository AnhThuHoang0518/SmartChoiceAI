import { Navbar } from "./components/layout/Navbar"
import { CategoryNavigation } from "./components/layout/CategoryNavigation"
import { HeroSection } from "./components/layout/HeroSection"
import { FeatureSection } from "./components/layout/FeatureSection"
import { CategorySection } from "./components/layout/CategorySection"
import { ProductRecommendation } from "./components/layout/ProductRecommendation"
import { PromotionSection } from "./components/layout/PromotionSection"
import { ReasonSection } from "./components/layout/ReasonSection"
import { BottomCTA } from "./components/layout/BottomCTA"
import { Footer } from "./components/layout/Footer"

function App() {
  return (
    <div className="min-h-screen flex flex-col bg-background font-sans">
      <Navbar />
      <CategoryNavigation />
      
      <main className="flex-1">
        <HeroSection />
        <FeatureSection />
        <CategorySection />
        <ProductRecommendation />
        <PromotionSection />
        <ReasonSection />
        <BottomCTA />
      </main>

      <Footer />
    </div>
  )
}

export default App
