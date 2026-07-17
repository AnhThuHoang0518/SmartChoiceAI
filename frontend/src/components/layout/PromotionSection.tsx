import { motion } from "framer-motion"

export function PromotionSection() {
  return (
    <section className="py-12 container mx-auto px-4">
      <h2 className="text-xl font-bold mb-6">KHUYẾN MÃI HOT HÔM NAY</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Banner 1 */}
        <motion.div 
          whileHover={{ y: -5 }}
          className="rounded-2xl relative overflow-hidden cursor-pointer shadow-md hover:shadow-xl transition-shadow aspect-[2/0.95]"
        >
          <img src="/images/sale1.png" alt="Sale 1" className="w-full h-full object-cover scale-[1.08] object-center" />
        </motion.div>

        {/* Banner 2 */}
        <motion.div 
          whileHover={{ y: -5 }}
          className="rounded-2xl relative overflow-hidden cursor-pointer shadow-md hover:shadow-xl transition-shadow aspect-[2/0.95]"
        >
          <img src="/images/sale2.png" alt="Sale 2" className="w-full h-full object-cover scale-[1.08] object-center" />
        </motion.div>

        {/* Banner 3 */}
        <motion.div 
          whileHover={{ y: -5 }}
          className="rounded-2xl relative overflow-hidden cursor-pointer shadow-md hover:shadow-xl transition-shadow aspect-[2/0.95]"
        >
          <img src="/images/sale3.png" alt="Sale 3" className="w-full h-full object-cover scale-[1.08] object-center" />
        </motion.div>

        {/* Banner 4 */}
        <motion.div 
          whileHover={{ y: -5 }}
          className="rounded-2xl relative overflow-hidden cursor-pointer shadow-md hover:shadow-xl transition-shadow aspect-[2/0.95]"
        >
          <img src="/images/sale4.png" alt="Sale 4" className="w-full h-full object-cover scale-[1.08] object-center" />
        </motion.div>
      </div>
    </section>
  )
}

