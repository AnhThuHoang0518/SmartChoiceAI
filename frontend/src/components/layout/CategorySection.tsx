import { useRef } from "react"
import { motion } from "framer-motion"
import { ChevronRight, ChevronLeft } from "lucide-react"

const categories = [
  { name: "Tivi", image: "/images/image.png" },
  { name: "Tủ lạnh", image: "/images/image copy.png" },
  { name: "Máy lạnh", image: "/images/image copy 2.png" },
  { name: "Máy giặt", image: "/images/image copy 3.png" },
  { name: "Laptop", image: "/images/image copy 4.png" },
  { name: "Điện thoại", image: "/images/image copy 5.png" },
  { name: "Tai nghe", image: "/images/image copy 6.png" },
  { name: "Màn hình", image: "/images/image copy 7.png" },
  { name: "Phụ kiện", image: "/images/image copy 8.png" },
]

export function CategorySection() {
  const scrollRef = useRef<HTMLDivElement>(null)

  const scroll = (direction: 'left' | 'right') => {
    if (scrollRef.current) {
      const scrollAmount = 400; // Scroll amount per click
      scrollRef.current.scrollBy({ 
        left: direction === 'left' ? -scrollAmount : scrollAmount, 
        behavior: 'smooth' 
      })
    }
  }

  return (
    <section className="py-8 bg-[#F5F8FD] container mx-auto px-4">
      <h2 className="text-lg md:text-xl font-bold mb-4 text-[#001D6E] uppercase">TƯ VẤN THEO DANH MỤC</h2>
      
      <div className="relative group">
        {/* Left Scroll Button */}
        <button 
          onClick={() => scroll('left')}
          className="absolute left-0 top-1/2 -translate-y-1/2 -ml-4 w-10 h-10 bg-white border border-gray-200 rounded-full shadow-md flex items-center justify-center text-gray-500 hover:text-[#005BFF] hover:border-[#005BFF] z-10 opacity-0 group-hover:opacity-100 transition-all duration-300 hidden md:flex"
        >
          <ChevronLeft className="w-6 h-6" />
        </button>

        <div ref={scrollRef} className="flex overflow-x-auto gap-4 pb-4 no-scrollbar items-center scroll-smooth px-1">
          {categories.map((cat, i) => (
            <motion.div
              key={i}
              whileHover={{ y: -4 }}
              className="w-[150px] min-w-[150px] h-[180px] bg-white rounded-2xl p-4 flex flex-col items-center justify-between shadow-sm hover:shadow-md transition-all duration-300 border border-white cursor-pointer flex-shrink-0"
            >
              <div className="w-full h-[110px] flex items-center justify-center mt-1">
                <img src={cat.image} alt={cat.name} className="object-contain max-h-full max-w-full" />
              </div>
              <span className="text-[15px] font-bold text-center text-[#001D6E] leading-tight mb-1">{cat.name}</span>
            </motion.div>
          ))}

          {/* Xem tất cả Card */}
          <motion.div
            whileHover={{ y: -4 }}
            className="w-[120px] min-w-[120px] h-[180px] bg-white rounded-2xl p-3 flex flex-col items-center justify-center gap-3 shadow-sm hover:shadow-md transition-all duration-300 border border-white cursor-pointer flex-shrink-0"
          >
            <div className="w-12 h-12 bg-white shadow rounded-full flex items-center justify-center text-[#005BFF]">
              <ChevronRight className="w-7 h-7" />
            </div>
            <span className="text-[14px] font-medium text-center text-[#005BFF]">Xem tất cả</span>
          </motion.div>
        </div>

        {/* Right Scroll Button */}
        <button 
          onClick={() => scroll('right')}
          className="absolute right-0 top-1/2 -translate-y-1/2 -mr-4 w-10 h-10 bg-white border border-gray-200 rounded-full shadow-md flex items-center justify-center text-gray-500 hover:text-[#005BFF] hover:border-[#005BFF] z-10 opacity-0 group-hover:opacity-100 transition-all duration-300 hidden md:flex"
        >
          <ChevronRight className="w-6 h-6" />
        </button>
      </div>
    </section>
  )
}
