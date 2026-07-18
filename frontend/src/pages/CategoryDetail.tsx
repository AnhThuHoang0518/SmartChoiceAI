import { useParams, Link } from "react-router-dom"
import { ChevronRight, Filter, SortDesc, BadgeCheck } from "lucide-react"
import { Button } from "../components/ui/button"
import { Badge } from "../components/ui/badge"

// Mock data (thay thế sau bằng data thật hoặc fallback logic nếu cần)
const MOCK_PRODUCTS = Array.from({ length: 8 }).map((_, i) => ({
  id: i,
  ten: "Smart Tivi Samsung 4K 65 inch UA65AU7700",
  gia: 12490000,
  gia_goc: 16900000,
  phan_tram: 26,
  anh_url: "/images/ac1.png", // Dùng tạm ảnh mock
}))

const vnd = (n: number) => n.toLocaleString("vi-VN") + "đ"

export default function CategoryDetail() {
  const { slug } = useParams()
  
  // Format tên category cho hiển thị (VD: "may-lanh" -> "Máy lạnh")
  const categoryName = slug ? slug.replace(/-/g, " ").replace(/\b\w/g, l => l.toUpperCase()) : "Danh mục"

  return (
    <main className="flex-1 bg-[#F3F4F6] min-h-screen pb-12">
      {/* Breadcrumb & Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-2 text-[13px] text-gray-500 mb-3">
            <Link to="/" className="hover:text-[#005BFF]">Trang chủ</Link>
            <ChevronRight className="w-3 h-3" />
            <span className="text-gray-900 font-semibold">{categoryName}</span>
          </div>
          <h1 className="text-2xl font-bold text-[#002D62]">{categoryName}</h1>
        </div>
      </div>

      <div className="container mx-auto px-4 mt-6 flex flex-col md:flex-row gap-6">
        {/* Sidebar Filters */}
        <div className="w-full md:w-[260px] flex-shrink-0">
          <div className="bg-white rounded-xl shadow-sm p-5 sticky top-[140px]">
            <div className="flex items-center gap-2 font-bold text-[#002D62] mb-4 pb-3 border-b border-gray-100">
              <Filter className="w-5 h-5" />
              BỘ LỌC SẢN PHẨM
            </div>
            
            <div className="mb-6">
              <h3 className="font-semibold text-sm mb-3">Hãng sản xuất</h3>
              <div className="flex flex-col gap-2">
                {["Samsung", "LG", "Sony", "TCL", "Daikin", "Panasonic"].map(brand => (
                  <label key={brand} className="flex items-center gap-2 cursor-pointer group">
                    <input type="checkbox" className="w-4 h-4 rounded border-gray-300 text-[#005BFF] focus:ring-[#005BFF]" />
                    <span className="text-sm text-gray-600 group-hover:text-[#005BFF] transition-colors">{brand}</span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <h3 className="font-semibold text-sm mb-3">Mức giá</h3>
              <div className="flex flex-col gap-2">
                {["Dưới 5 triệu", "5 - 10 triệu", "10 - 15 triệu", "Trên 15 triệu"].map(price => (
                  <label key={price} className="flex items-center gap-2 cursor-pointer group">
                    <input type="radio" name="price" className="w-4 h-4 border-gray-300 text-[#005BFF] focus:ring-[#005BFF]" />
                    <span className="text-sm text-gray-600 group-hover:text-[#005BFF] transition-colors">{price}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1">
          {/* Top Bar */}
          <div className="bg-white rounded-xl shadow-sm p-4 mb-6 flex flex-wrap items-center justify-between gap-4">
            <span className="text-sm text-gray-600">
              Hiển thị <strong className="text-gray-900">8</strong> sản phẩm
            </span>
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-600">Sắp xếp theo:</span>
              <button className="flex items-center gap-2 px-3 py-1.5 border border-gray-200 rounded-lg text-sm hover:border-[#005BFF] hover:text-[#005BFF] transition-colors bg-gray-50">
                <SortDesc className="w-4 h-4" />
                Khuyến mãi tốt nhất
              </button>
            </div>
          </div>

          {/* Product Grid */}
          <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {MOCK_PRODUCTS.map((item, idx) => (
              <div 
                key={idx}
                className="relative flex flex-col bg-white border border-gray-100 rounded-2xl p-4 shadow-sm hover:shadow-md hover:border-blue-200 transition-all cursor-pointer group"
                onClick={() => { window.location.href = `/chat?hoi=Tư vấn ${encodeURIComponent(item.ten)}` }}
              >
                <Badge className="absolute top-3 left-3 bg-green-100 text-green-700 hover:bg-green-100 border-none px-2 py-0.5 text-[10px] font-bold flex items-center gap-1 shadow-sm z-10">
                  <BadgeCheck className="w-3 h-3" /> Khuyến mãi thật
                </Badge>

                <div className="w-full h-[140px] flex items-center justify-center mt-6 mb-4">
                  {/* Using placeholder for category products, simulating AC or TV images */}
                  <img src={item.anh_url} alt={item.ten} className="object-contain h-full group-hover:scale-105 transition-transform duration-300 mix-blend-multiply" />
                </div>

                <h5 className="font-bold text-gray-900 text-[13px] leading-snug mb-2 group-hover:text-[#005BFF] transition-colors line-clamp-2">
                  {item.ten}
                </h5>

                <div className="flex items-end gap-2 mb-1 flex-wrap">
                  <span className="text-red-600 font-bold text-[16px]">{vnd(item.gia)}</span>
                  <span className="text-[11px] font-bold text-red-600 bg-red-50 px-1.5 py-0.5 rounded border border-red-100">
                    -{item.phan_tram}%
                  </span>
                </div>
                <div className="text-[12px] text-gray-400 line-through mb-4">{vnd(item.gia_goc)}</div>

                <div className="mt-auto pt-3 border-t border-gray-100">
                  <Button variant="outline" className="w-full text-[12px] font-semibold text-[#005BFF] border-[#005BFF] hover:bg-[#005BFF] hover:text-white rounded-lg transition-colors">
                    Hỏi AI tư vấn máy này
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </main>
  )
}
