import { HeroSection } from "../components/layout/HeroSection"
import { FeatureSection } from "../components/layout/FeatureSection"
import { CategorySection } from "../components/layout/CategorySection"
import { ProductRecommendation } from "../components/layout/ProductRecommendation"
import { PromotionSection } from "../components/layout/PromotionSection"
import { ReasonSection } from "../components/layout/ReasonSection"
import { BottomCTA } from "../components/layout/BottomCTA"

export default function Home() {
  return (
    <main className="flex-1">
      <HeroSection />
      <FeatureSection />
      <CategorySection />
      <ProductRecommendation />
      <PromotionSection />
      <ReasonSection />
      <BottomCTA />
    </main>
  )
}
