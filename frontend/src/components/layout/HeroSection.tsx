import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { Mic, SendHorizontal, BadgeCheck, Brain, Scale, Lightbulb, ShieldCheck, Wind, Tablet, MessageSquare, Package, WashingMachine } from "lucide-react"
import { Button } from "../ui/button"
import { Badge } from "../ui/badge"

// "Cap nhat ton kho" cu bi bo: he thong CHUA co Stock API va bot noi thang
// dieu do - landing khong duoc hua thu chat khong lam.
const bulletPoints = [
  { icon: Brain,       text: "Hiểu nhu cầu thật của bạn" },
  { icon: Scale,       text: "So sánh sản phẩm khách quan" },
  { icon: Lightbulb,   text: "Giải thích dễ hiểu, dễ ra quyết định" },
  { icon: ShieldCheck, text: "Mọi con số đều có nguồn — không bịa" },
]

// Chi goi y nganh CO du lieu that (laptop/tai nghe chua co sheet -> bot tu
// choi, dua len landing la tu ban vao chan luc demo).
const suggestions = [
  { icon: Wind,           text: "Máy lạnh cho phòng 20m²" },
  { icon: Package,        text: "Tủ lạnh dưới 10 triệu" },
  { icon: Tablet,         text: "Tablet màn 11 inch pin trâu" },
  { icon: WashingMachine, text: "Máy giặt cho nhà 4 người" },
]

const denChat = (hoi?: string) => {
  window.location.href = hoi ? `/chat?hoi=${encodeURIComponent(hoi)}` : "/chat"
}

type KhuyenMai = { ten: string; gia: number; gia_goc: number; phan_tram: number; anh_url?: string }
const vnd = (n: number) => n.toLocaleString("vi-VN") + "đ"

export function HeroSection() {
  // Card "Goi y cho ban": may giam sau nhat THAT tu catalog, khong hardcode.
  const [km, setKm] = useState<KhuyenMai | null>(null)
  const [oNhap, setONhap] = useState("")
  useEffect(() => {
    fetch("/api/khuyen-mai").then(r => r.json()).then(d => setKm(d[0] ?? null)).catch(() => {})
  }, [])
  return (
    <section
      className="relative w-full bg-cover bg-center overflow-hidden"
      style={{ backgroundImage: 'url("/images/background.png")' }}
    >
      <div className="absolute inset-0 bg-blue-900/25 mix-blend-multiply pointer-events-none" />

      <div className="container mx-auto relative z-10 flex items-center min-h-[480px] pt-10 pb-20 lg:pb-28">

        {/* ── Left Column ── */}
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8 }}
          className="flex flex-col justify-center items-start w-[45%] xl:w-[40%] shrink-0 pr-4"
        >
          {/* Header Block (Label + Title) */}
          <div className="w-fit flex flex-col">
            {/* Label */}
            <div className="w-full mb-4 text-center">
              <span className="text-yellow-400 text-[11px] font-bold tracking-widest uppercase">AI PRODUCT ADVISOR</span>
            </div>

            {/* Title */}
            <h1 className="text-[28px] xl:text-[34px] font-extrabold leading-[1.2] mb-5 drop-shadow-md text-left whitespace-nowrap">
              <span className="text-yellow-400">AI TƯ VẤN </span>
              <span className="text-white">CHỌN SẢN PHẨM</span><br />
              <span className="text-white">PHÙ HỢP NHẤT CHO BẠN</span>
            </h1>
          </div>

          {/* Bullet points */}
          <ul className="flex flex-col gap-3 mb-8 w-full">
            {bulletPoints.map(({ icon: Icon, text }, i) => (
              <li key={i} className="flex items-center gap-3 text-white/90 text-[14px] font-medium text-left">
                <Icon className="w-5 h-5 text-yellow-400 shrink-0" />
                {text}
              </li>
            ))}
          </ul>

          {/* CTA */}
          <Button
            onClick={() => denChat()}
            className="bg-[#FFD400] text-blue-900 hover:bg-yellow-300 font-bold rounded-full px-7 h-12 w-fit flex items-center gap-2 shadow-lg text-[15px]"
          >
            <MessageSquare className="w-5 h-5" />
            Bắt đầu tư vấn ngay
          </Button>
        </motion.div>

        {/* ── Right: Robot + Card ── */}
        <div className="flex-1 relative flex items-end">

          {/* Robot */}
          <div
            className="absolute left-[-20px] xl:left-[-30px] bottom-[-20px] z-30 hidden lg:block pointer-events-none"
          >
            <img src="/images/robot.png" alt="AI Robot" className="w-[200px] xl:w-[240px] h-auto drop-shadow-2xl" />
          </div>

          {/* White Card */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="ml-[160px] xl:ml-[185px] flex-1 bg-white rounded-2xl shadow-2xl p-5 flex gap-5"
          >
            {/* Chat Panel */}
            <div className="flex-1 flex flex-col min-w-0">
              <h3 className="text-gray-900 font-bold text-[15px] mb-1">Xin chào! 👋</h3>
              <p className="text-gray-500 text-[13px] leading-relaxed mb-4">
                Bạn đang tìm sản phẩm gì?<br />
                Mình sẽ giúp bạn chọn sản phẩm<br />
                phù hợp nhất.
              </p>

              {/* Vertical suggestions */}
              <div className="flex flex-col gap-2 mb-4">
                {suggestions.map(({ icon: Icon, text }, i) => (
                  <button
                    key={i}
                    onClick={() => denChat(text)}
                    className="flex items-center gap-2.5 px-4 py-2.5 rounded-xl border border-gray-200 text-[13px] font-semibold text-gray-700 hover:border-[#005BFF] hover:text-[#005BFF] hover:bg-blue-50 transition-all text-left"
                  >
                    <Icon className="w-4 h-4 text-[#005BFF] shrink-0" />
                    {text}
                  </button>
                ))}
              </div>

              {/* Input: go xong Enter/bam gui -> sang trang chat, cau duoc gui luon */}
              <form
                className="relative mt-auto"
                onSubmit={e => { e.preventDefault(); if (oNhap.trim()) denChat(oNhap.trim()) }}
              >
                <input
                  type="text"
                  value={oNhap}
                  onChange={e => setONhap(e.target.value)}
                  placeholder="Nhập nhu cầu của bạn..."
                  className="w-full h-11 pl-4 pr-20 rounded-full border border-gray-200 focus:outline-none focus:border-[#005BFF] text-[13px] shadow-sm transition-colors"
                />
                <div className="absolute right-1 top-1/2 -translate-y-1/2 flex items-center gap-0.5">
                  <button type="button" onClick={() => denChat()} title="Nói trong trang chat" className="w-9 h-9 rounded-full flex items-center justify-center text-gray-400 hover:text-[#005BFF] transition-colors">
                    <Mic className="w-4 h-4" />
                  </button>
                  <button type="submit" className="w-9 h-9 rounded-full flex items-center justify-center bg-[#005BFF] text-white hover:bg-blue-700 shadow-md transition-colors">
                    <SendHorizontal className="w-4 h-4" />
                  </button>
                </div>
              </form>
            </div>

            {/* Product Panel: may giam sau nhat THAT tu /api/khuyen-mai -
                khong hardcode gia, khong sao/danh gia bia (khong co du lieu do) */}
            {km && (
              <div className="w-[200px] xl:w-[215px] shrink-0 border-l border-gray-100 pl-5 flex-col hidden sm:flex">
                <h4 className="font-bold text-gray-900 text-[13px] mb-3">Đang giảm sâu nhất</h4>

                <div
                  onClick={() => denChat("Máy lạnh nào đang giảm giá?")}
                  className="relative flex flex-col flex-1 bg-white border border-gray-100 rounded-2xl p-3 shadow-sm hover:border-green-200 transition-colors cursor-pointer group"
                >
                  <Badge className="absolute -top-2.5 left-3 bg-green-100 text-green-700 hover:bg-green-100 border-none px-2 py-0.5 text-[10px] font-bold flex items-center gap-1 shadow-sm z-10">
                    <BadgeCheck className="w-3 h-3" /> Khuyến mãi thật
                  </Badge>

                  <div className="w-full h-[90px] flex items-center justify-center mt-3 mb-2">
                    <img src={km.anh_url || "/images/ac1.png"} alt={km.ten} className="object-contain h-full group-hover:scale-105 transition-transform duration-300" />
                  </div>

                  <h5 className="font-bold text-gray-900 text-[12px] leading-snug mb-1.5 group-hover:text-[#005BFF] transition-colors">
                    {km.ten}
                  </h5>

                  <div className="flex items-center gap-1.5 mb-2 flex-wrap">
                    <span className="text-red-600 font-bold text-[15px]">{vnd(km.gia)}</span>
                    <span className="text-[10px] font-bold text-red-600 bg-red-50 px-1.5 py-0.5 rounded">-{km.phan_tram}%</span>
                  </div>
                  <div className="text-[11px] text-gray-400 line-through mb-3">{vnd(km.gia_goc)}</div>

                  <Button variant="outline" className="w-full h-8 text-[11px] font-medium text-[#005BFF] border-[#005BFF] hover:bg-blue-50 rounded-lg mt-auto">
                    Tư vấn máy này
                  </Button>
                </div>
              </div>
            )}
          </motion.div>
        </div>

      </div>
    </section>
  )
}
