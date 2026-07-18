import { Menu, Refrigerator, AirVent, Package, Wind, Snowflake, Utensils, Droplets, Tablet, Sparkles } from "lucide-react"
import { Link } from "react-router-dom"

// Chi liet ke danh muc CO du lieu that trong catalog (khong show Tivi/Laptop/
// Dien thoai vi chua co san pham -> tranh giam khao bam vao trang rong).
const CATEGORIES = [
  { icon: AirVent, label: "Máy lạnh" },
  { icon: Refrigerator, label: "Tủ lạnh" },
  { icon: Package, label: "Máy giặt" },
  { icon: Wind, label: "Máy sấy" },
  { icon: Snowflake, label: "Tủ đông" },
  { icon: Utensils, label: "Máy rửa chén" },
  { icon: Droplets, label: "Máy nước nóng" },
  { icon: Tablet, label: "Máy tính bảng" },
  { icon: Sparkles, label: "Khuyến mãi", highlight: true },
]

export function CategoryNavigation() {
  const getSlug = (name: string) => {
    return name.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/đ/g, "d").replace(/\s+/g, '-')
  }

  return (
    <nav
      className="w-full bg-[#FFD400] text-[#002D62] text-sm font-semibold border-t-[3px] border-[#005BFF] shadow-sm hidden md:block sticky top-[80px] z-40"
    >
      <div className="container mx-auto px-4 h-[44px] flex items-center justify-between relative">

        {/* Main Menu Button */}
        <div className="group h-full flex items-center cursor-pointer relative -ml-1 md:-ml-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full text-[#002D62] group-hover:bg-[#005BFF] group-hover:text-white transition-all duration-300">
            <Menu className="w-5 h-5" />
            <span className="font-bold tracking-wide text-[13px]">DANH MỤC SẢN PHẨM ▾</span>
          </div>

          {/* Dropdown Content with bridge */}
          <div className="absolute top-[44px] left-0 pt-2 w-[280px] transition-all duration-200 opacity-0 invisible group-hover:opacity-100 group-hover:visible z-50">
            <div className="bg-white rounded-lg shadow-xl border border-gray-100 py-2">
              {CATEGORIES.map((cat, i) => (
                <Link
                  to={cat.label === "Khuyến mãi" ? "/chat" : `/category/${getSlug(cat.label)}`}
                  key={`drop-${i}`}
                  className="flex items-center gap-3 px-4 py-2.5 hover:bg-[#F3F4F6] hover:text-[#005BFF] text-[#002D62] transition-colors group/item"
                >
                  <cat.icon className="w-5 h-5 text-gray-500 group-hover/item:text-[#005BFF] transition-colors" />
                  <span className="text-[14px] font-medium">{cat.label}</span>
                </Link>
              ))}
            </div>
          </div>
        </div>

        {/* Categories */}
        <div className="flex items-center overflow-x-auto no-scrollbar ml-2 flex-1 h-full gap-1">
          {CATEGORIES.map((cat, i) => {
            if (cat.label === "Khuyến mãi") return null;
            return (
              <Link
                to={`/category/${getSlug(cat.label)}`}
                key={i}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[#002D62] hover:bg-[#005BFF] hover:text-white transition-all duration-300 whitespace-nowrap group"
              >
                <cat.icon className="w-4 h-4" />
                <span className="text-[13px] font-medium">{cat.label}</span>
              </Link>
            )
          })}
        </div>

        {/* Right Links */}
        <div className="flex items-center gap-2 ml-4 flex-shrink-0 h-full">
          <Link to="/chat" className="text-[13px] font-medium px-3 py-1.5 rounded-full text-[#002D62] hover:bg-[#005BFF] hover:text-white transition-all duration-300 whitespace-nowrap">
            Mua online giá rẻ
          </Link>
          <Link to="/chat" className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[#002D62] hover:bg-[#005BFF] hover:text-white transition-all duration-300 whitespace-nowrap group">
            <span className="text-[#E30A17] group-hover:text-white font-bold text-base leading-none mb-[2px]">✿</span>
            <span className="text-[13px] font-semibold">Khuyến mãi</span>
          </Link>
        </div>

      </div>
    </nav>
  )
}

