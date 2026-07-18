import { useEffect, useState } from "react"
import { useParams, Link } from "react-router-dom"
import { ChevronRight, Filter, SortDesc, BadgeCheck } from "lucide-react"
import { Button } from "../components/ui/button"
import { Badge } from "../components/ui/badge"

// TRUOC: MOCK_PRODUCTS - 8 cai TV Samsung y het nhau, gia bia, anh mock. Ca he
// thong pitch "moi con so deu co nguon" - trang danh muc khong duoc la ngoai le.
// GIO: keo san pham THAT tu /api/san-pham theo nganh (gia/anh/hang tu catalog
// DMX). Loc hang + muc gia + sap xep deu chay server tren data that.

type SanPham = { ten: string; hang: string; gia: number; gia_goc: number; phan_tram: number; giam: number; qua?: string; anh_url?: string }
type KetQua = { nganh: string; ten: string; tong: number; hang: string[]; san_pham: SanPham[] }

const vnd = (n: number) => n.toLocaleString("vi-VN") + "đ"
const anhMacDinh = ["/images/ac1.png", "/images/ac2.png", "/images/ac3.png", "/images/ac4.png"]

const MUC_GIA = [
  { nhan: "Dưới 5 triệu", min: 0, max: 5000000 },
  { nhan: "5 - 10 triệu", min: 5000000, max: 10000000 },
  { nhan: "10 - 15 triệu", min: 10000000, max: 15000000 },
  { nhan: "Trên 15 triệu", min: 15000000, max: 0 },
]

const SAP_XEP = [
  { ma: "giam", nhan: "Khuyến mãi tốt nhất" },
  { ma: "gia_tang", nhan: "Giá thấp → cao" },
  { ma: "gia_giam", nhan: "Giá cao → thấp" },
]

export default function CategoryDetail() {
  const { slug } = useParams()
  const [kq, setKq] = useState<KetQua | null>(null)
  const [dangTai, setDangTai] = useState(true)
  const [hangChon, setHangChon] = useState<Set<string>>(new Set())
  const [giaChon, setGiaChon] = useState<number | null>(null)
  const [sapXep, setSapXep] = useState("giam")

  const tenHienThi = kq?.ten || (slug ? slug.replace(/-/g, " ").replace(/\b\w/g, l => l.toUpperCase()) : "Danh mục")

  useEffect(() => {
    if (!slug) return
    setDangTai(true)
    const q = new URLSearchParams({ nganh: slug, sap_xep: sapXep })
    if (hangChon.size) q.set("hang", [...hangChon].join(","))
    if (giaChon !== null) {
      const g = MUC_GIA[giaChon]
      if (g.min) q.set("gia_min", String(g.min))
      if (g.max) q.set("gia_max", String(g.max))
    }
    fetch(`/api/san-pham?${q.toString()}`)
      .then(r => r.json())
      .then((d: KetQua) => setKq(d))
      .catch(() => setKq(null))
      .finally(() => setDangTai(false))
  }, [slug, sapXep, hangChon, giaChon])

  const toggleHang = (h: string) => {
    setHangChon(prev => {
      const n = new Set(prev)
      n.has(h) ? n.delete(h) : n.add(h)
      return n
    })
  }

  const sp = kq?.san_pham || []
  const hangDs = kq?.hang || []
  const trong = !dangTai && kq && kq.ten === ""      // nganh chua co du lieu

  return (
    <main className="flex-1 bg-[#F3F4F6] min-h-screen pb-12">
      {/* Breadcrumb & Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-2 text-[13px] text-gray-500 mb-3">
            <Link to="/" className="hover:text-[#005BFF]">Trang chủ</Link>
            <ChevronRight className="w-3 h-3" />
            <span className="text-gray-900 font-semibold">{tenHienThi}</span>
          </div>
          <h1 className="text-2xl font-bold text-[#002D62] capitalize">{tenHienThi}</h1>
        </div>
      </div>

      {trong ? (
        <div className="container mx-auto px-4 mt-16 text-center">
          <p className="text-lg font-semibold text-[#002D62] mb-2">Danh mục này đang được cập nhật dữ liệu</p>
          <p className="text-gray-500 mb-6">Bạn có thể hỏi trực tiếp trợ lý AI để được tư vấn ngay.</p>
          <Button onClick={() => { window.location.href = "/chat" }} className="bg-[#005BFF] hover:bg-[#005BFF]/90 text-white font-medium h-11 px-6 rounded-lg">
            Hỏi AI tư vấn
          </Button>
        </div>
      ) : (
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
                <div className="flex flex-col gap-2 max-h-[220px] overflow-y-auto">
                  {hangDs.length === 0 && <span className="text-xs text-gray-400">Đang tải…</span>}
                  {hangDs.map(brand => (
                    <label key={brand} className="flex items-center gap-2 cursor-pointer group">
                      <input
                        type="checkbox"
                        checked={hangChon.has(brand)}
                        onChange={() => toggleHang(brand)}
                        className="w-4 h-4 rounded border-gray-300 text-[#005BFF] focus:ring-[#005BFF]"
                      />
                      <span className="text-sm text-gray-600 group-hover:text-[#005BFF] transition-colors">{brand}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="font-semibold text-sm mb-3">Mức giá</h3>
                <div className="flex flex-col gap-2">
                  {MUC_GIA.map((g, i) => (
                    <label key={g.nhan} className="flex items-center gap-2 cursor-pointer group">
                      <input
                        type="radio"
                        name="price"
                        checked={giaChon === i}
                        onChange={() => setGiaChon(giaChon === i ? null : i)}
                        onClick={() => giaChon === i && setGiaChon(null)}
                        className="w-4 h-4 border-gray-300 text-[#005BFF] focus:ring-[#005BFF]"
                      />
                      <span className="text-sm text-gray-600 group-hover:text-[#005BFF] transition-colors">{g.nhan}</span>
                    </label>
                  ))}
                </div>
                {(hangChon.size > 0 || giaChon !== null) && (
                  <button
                    onClick={() => { setHangChon(new Set()); setGiaChon(null) }}
                    className="mt-4 text-[13px] text-[#005BFF] hover:underline"
                  >
                    Xóa bộ lọc
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1">
            {/* Top Bar */}
            <div className="bg-white rounded-xl shadow-sm p-4 mb-6 flex flex-wrap items-center justify-between gap-4">
              <span className="text-sm text-gray-600">
                {dangTai ? "Đang tải…" : <>Hiển thị <strong className="text-gray-900">{sp.length}</strong> / {kq?.tong ?? 0} sản phẩm</>}
              </span>
              <div className="flex items-center gap-3">
                <span className="text-sm text-gray-600 flex items-center gap-1"><SortDesc className="w-4 h-4" /> Sắp xếp:</span>
                <select
                  value={sapXep}
                  onChange={e => setSapXep(e.target.value)}
                  className="px-3 py-1.5 border border-gray-200 rounded-lg text-sm bg-gray-50 hover:border-[#005BFF] focus:border-[#005BFF] focus:outline-none cursor-pointer"
                >
                  {SAP_XEP.map(s => <option key={s.ma} value={s.ma}>{s.nhan}</option>)}
                </select>
              </div>
            </div>

            {/* Product Grid */}
            {!dangTai && sp.length === 0 ? (
              <div className="bg-white rounded-xl shadow-sm p-12 text-center text-gray-500">
                Không có sản phẩm nào khớp bộ lọc. Thử bỏ bớt điều kiện nhé.
              </div>
            ) : (
              <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {sp.map((item, idx) => (
                  <div
                    key={idx}
                    className="relative flex flex-col bg-white border border-gray-100 rounded-2xl p-4 shadow-sm hover:shadow-md hover:border-blue-200 transition-all cursor-pointer group"
                    onClick={() => { window.location.href = `/chat?hoi=${encodeURIComponent(`Tư vấn ${item.ten}, có hợp nhu cầu mình không?`)}` }}
                  >
                    {item.giam > 0 && (
                      <Badge className="absolute top-3 left-3 bg-green-100 text-green-700 hover:bg-green-100 border-none px-2 py-0.5 text-[10px] font-bold flex items-center gap-1 shadow-sm z-10">
                        <BadgeCheck className="w-3 h-3" /> Giảm {vnd(item.giam)}
                      </Badge>
                    )}

                    <div className="w-full h-[140px] flex items-center justify-center mt-6 mb-4">
                      <img src={item.anh_url || anhMacDinh[idx % anhMacDinh.length]} alt={item.ten} className="object-contain h-full group-hover:scale-105 transition-transform duration-300 mix-blend-multiply" />
                    </div>

                    <h5 className="font-bold text-gray-900 text-[13px] leading-snug mb-2 group-hover:text-[#005BFF] transition-colors line-clamp-2">
                      {item.ten}
                    </h5>

                    <div className="flex items-end gap-2 mb-1 flex-wrap">
                      <span className="text-red-600 font-bold text-[16px]">{vnd(item.gia)}</span>
                      {item.phan_tram > 0 && (
                        <span className="text-[11px] font-bold text-red-600 bg-red-50 px-1.5 py-0.5 rounded border border-red-100">
                          -{item.phan_tram}%
                        </span>
                      )}
                    </div>
                    {item.gia_goc > item.gia && (
                      <div className="text-[12px] text-gray-400 line-through mb-4">{vnd(item.gia_goc)}</div>
                    )}

                    <div className="mt-auto pt-3 border-t border-gray-100">
                      <Button variant="outline" className="w-full text-[12px] font-semibold text-[#005BFF] border-[#005BFF] hover:bg-[#005BFF] hover:text-white rounded-lg transition-colors">
                        Hỏi AI tư vấn máy này
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </main>
  )
}
