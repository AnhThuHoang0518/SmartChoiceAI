import { Menu, Tv, Refrigerator, AirVent, Laptop, Smartphone, Package, Sparkles } from "lucide-react"

const CATEGORIES = [
  { icon: Tv, label: "Tivi" },
  { icon: Refrigerator, label: "Tủ lạnh" },
  { icon: AirVent, label: "Máy lạnh" },
  { icon: Package, label: "Máy giặt" },
  { icon: Laptop, label: "Laptop" },
  { icon: Smartphone, label: "Điện thoại" },
  { icon: Sparkles, label: "Khuyến mãi", highlight: true },
]

export function CategoryNavigation() {
  return (
    <nav className="w-full bg-[#FFD400] text-[#002D62] text-sm font-semibold border-t-[3px] border-[#005BFF] shadow-sm hidden md:block relative z-40">
      <div className="container mx-auto px-4 h-[44px] flex items-center justify-between">

        {/* Main Menu Button */}
        <div className="flex items-center gap-2 cursor-pointer px-3 py-1.5 rounded-full text-[#002D62] nav-item-hover -ml-4 md:-ml-3">
          <Menu className="w-5 h-5 transition-colors" />
          <span className="font-bold tracking-wide text-[13px] transition-colors">DANH MỤC SẢN PHẨM</span>
        </div>

        {/* Categories */}
        <div className="flex items-center overflow-x-auto no-scrollbar ml-2 flex-1">
          {CATEGORIES.map((cat, i) => {
            if (cat.label === "Khuyến mãi") return null; // Handle separately below
            return (
              <a
                href="#"
                key={i}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[#002D62] nav-item-hover whitespace-nowrap"
              >
                <cat.icon className="w-4 h-4 transition-colors" />
                <span className="text-[13px] font-medium transition-colors">{cat.label}</span>
              </a>
            )
          })}
        </div>

        {/* Right Links */}
        <div className="flex items-center gap-2 ml-4 flex-shrink-0">
          <a href="#" className="text-[13px] font-medium px-3 py-1.5 rounded-full text-[#002D62] nav-item-hover whitespace-nowrap">
            <span className="transition-colors">Mua online giá rẻ</span>
          </a>
          <a href="#" className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[#002D62] nav-item-hover whitespace-nowrap">
            <span className="text-[#E30A17] font-bold text-base leading-none mb-[2px] transition-colors">✿</span>
            <span className="text-[13px] font-semibold transition-colors">Khuyến mãi</span>
          </a>
        </div>

      </div>
    </nav>
  )
}

