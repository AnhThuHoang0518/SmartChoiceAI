import { useRef, useEffect, useState } from "react"
import { motion } from "framer-motion"
import { ChevronRight, ChevronLeft } from "lucide-react"
import { useNavigate } from "react-router-dom"

// TRUOC: anh danh muc hardcode ("/images/image copy N.png") -> lech nhan (Máy sấy
// ra laptop, Tủ đông ra tivi, Máy rửa chén ra iPhone). GIO: keo tu /api/danh-muc
// - moi the lay anh THAT cua 1 san pham trong dung nganh do, nhan luon khop anh.

type DanhMuc = { ten: string; slug: string; tong: number; anh_url?: string }

export function CategorySection() {
  const scrollRef = useRef<HTMLDivElement>(null)
  const navigate = useNavigate()
  const [dm, setDm] = useState<DanhMuc[]>([])

  useEffect(() => {
    fetch("/api/danh-muc").then(r => r.json()).then(setDm).catch(() => setDm([]))
  }, [])

  const scroll = (direction: 'left' | 'right') => {
    if (scrollRef.current) {
      const scrollAmount = 400
      scrollRef.current.scrollBy({ left: direction === 'left' ? -scrollAmount : scrollAmount, behavior: 'smooth' })
    }
  }

  if (!dm.length) return null

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
          {dm.map((cat, i) => (
            <motion.div
              key={i}
              whileHover={{ y: -4 }}
              onClick={() => navigate(`/category/${cat.slug}`)}
              className="w-[150px] min-w-[150px] h-[180px] bg-white rounded-2xl p-4 flex flex-col items-center justify-between shadow-sm hover:shadow-md transition-all duration-300 border border-white cursor-pointer flex-shrink-0"
            >
              <div className="w-full h-[110px] flex items-center justify-center mt-1">
                {cat.anh_url
                  ? <img src={cat.anh_url} alt={cat.ten} loading="lazy" className="object-contain max-h-full max-w-full mix-blend-multiply" />
                  : <span className="text-3xl">📦</span>}
              </div>
              <span className="text-[15px] font-bold text-center text-[#001D6E] leading-tight mb-1">{cat.ten}</span>
            </motion.div>
          ))}

          {/* Xem tất cả Card -> chat */}
          <motion.div
            whileHover={{ y: -4 }}
            onClick={() => navigate("/category/may-lanh")}
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
