import { motion } from "framer-motion"
import { Star, CheckCircle2, Award, Tag } from "lucide-react"
import { Button } from "../ui/button"

const products = [
  {
    badge: { text: "Best Match", icon: CheckCircle2, bg: "bg-green-100", textCol: "text-green-700" },
    name: "Daikin FTKB35YVMV",
    subtitle: "Inverter 1.5 HP",
    rating: 4.8,
    reviews: 128,
    price: "9.990.000₫",
    oldPrice: "11.990.000₫",
    discount: "-16%",
    image: "/images/ac1.png"
  },
  {
    badge: { text: "Best Value", icon: Award, bg: "bg-amber-100", textCol: "text-amber-600" },
    name: "Panasonic CU/CS-PU9XKH-8",
    subtitle: "Inverter 1 HP",
    rating: 4.6,
    reviews: 98,
    price: "8.990.000₫",
    oldPrice: "10.990.000₫",
    discount: "-18%",
    image: "/images/ac2.png"
  },
  {
    badge: { text: "Khuyến mãi tốt", icon: Tag, bg: "bg-red-100", textCol: "text-red-600" },
    name: "LG V10WIN1",
    subtitle: "Inverter 1 HP",
    rating: 4.5,
    reviews: 76,
    price: "8.490.000₫",
    oldPrice: "9.990.000₫",
    discount: "-15%",
    image: "/images/ac3.png"
  },
  {
    badge: null,
    name: "Aqua AQA-RV10TA",
    subtitle: "Inverter 1 HP",
    rating: 4.4,
    reviews: 52,
    price: "7.990.000₫",
    oldPrice: "9.990.000₫",
    discount: "-20%",
    image: "/images/ac4.png"
  }
]

export function ProductRecommendation() {
  return (
    <section className="py-10 container mx-auto">
      <div className="mb-6">
        <h2 className="text-xl md:text-2xl font-bold text-primary uppercase">AI GỢI Ý SẢN PHẨM PHÙ HỢP VỚI BẠN</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {products.map((product, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.1 }}
            className="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-all duration-300 border border-gray-100 flex flex-col group relative"
          >
            {product.badge && (
              <div className="absolute top-4 left-4 z-10">
                <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-[11px] font-semibold ${product.badge.bg} ${product.badge.textCol}`}>
                  <product.badge.icon className="w-3.5 h-3.5" />
                  {product.badge.text}
                </div>
              </div>
            )}
            
            <div className="w-full h-36 flex items-center justify-center mt-8 mb-4 overflow-hidden">
              <img src={product.image} alt={product.name} className="object-contain h-full transition-transform duration-500 group-hover:scale-105" />
            </div>

            <div className="flex-1 flex flex-col">
              <h3 className="font-bold text-gray-900 line-clamp-2 text-sm md:text-base group-hover:text-primary transition-colors">
                {product.name}
              </h3>
              <p className="text-sm text-gray-500 mt-0.5 mb-2">
                {product.subtitle}
              </p>
              
              <div className="flex items-center gap-1.5 mb-3">
                <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
                <span className="text-sm text-gray-700 font-medium">{product.rating}</span>
                <span className="text-sm text-gray-500">({product.reviews})</span>
              </div>

              <div className="mt-auto">
                <div className="flex items-center gap-2 mb-3 flex-wrap">
                  <span className="text-red-600 font-bold text-lg">{product.price}</span>
                  <span className="text-[11px] font-semibold text-red-600 bg-red-50 px-1.5 py-0.5 rounded">{product.discount}</span>
                  <span className="text-xs text-gray-400 line-through">
                    {product.oldPrice}
                  </span>
                </div>

                <Button className="w-full rounded-lg bg-[#005BFF] hover:bg-[#005BFF]/90 text-white font-medium h-10">
                  Xem chi tiết
                </Button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="mt-6 text-center">
        <Button variant="link" className="text-[#005BFF] hover:text-[#005BFF]/80 font-medium">
          Xem tất cả sản phẩm phù hợp <span className="ml-1">→</span>
        </Button>
      </div>
    </section>
  )
}
