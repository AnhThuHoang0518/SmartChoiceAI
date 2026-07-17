import { motion } from "framer-motion"
import { Mic, SendHorizontal, Star, BadgeCheck, Brain, Scale, Lightbulb, RefreshCcw, Wind, Laptop, Headphones, MessageSquare, Package } from "lucide-react"
import { Button } from "../ui/button"
import { Badge } from "../ui/badge"

const bulletPoints = [
  { icon: Brain,       text: "Hiểu nhu cầu thật của bạn" },
  { icon: Scale,       text: "So sánh sản phẩm khách quan" },
  { icon: Lightbulb,   text: "Giải thích dễ hiểu, dễ ra quyết định" },
  { icon: RefreshCcw,  text: "Cập nhật giá, khuyến mãi & tồn kho" },
]

const suggestions = [
  { icon: Wind,      text: "Máy lạnh cho phòng 20m²" },
  { icon: Laptop,    text: "Laptop cho sinh viên" },
  { icon: Package,   text: "Tủ lạnh dưới 10 triệu" },
  { icon: Headphones,text: "Tai nghe chống ồn" },
]

const features = ["Phù hợp phòng 15 - 20m²", "Tiết kiệm điện Inverter", "Bảo hành 5 năm"]

export function HeroSection() {
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
          <Button className="bg-[#FFD400] text-blue-900 hover:bg-yellow-300 font-bold rounded-full px-7 h-12 w-fit flex items-center gap-2 shadow-lg text-[15px]">
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
                    className="flex items-center gap-2.5 px-4 py-2.5 rounded-xl border border-gray-200 text-[13px] font-semibold text-gray-700 hover:border-[#005BFF] hover:text-[#005BFF] hover:bg-blue-50 transition-all text-left"
                  >
                    <Icon className="w-4 h-4 text-[#005BFF] shrink-0" />
                    {text}
                  </button>
                ))}
              </div>

              {/* Input */}
              <div className="relative mt-auto">
                <input
                  type="text"
                  placeholder="Nhập nhu cầu của bạn..."
                  className="w-full h-11 pl-4 pr-20 rounded-full border border-gray-200 focus:outline-none focus:border-[#005BFF] text-[13px] shadow-sm transition-colors"
                />
                <div className="absolute right-1 top-1/2 -translate-y-1/2 flex items-center gap-0.5">
                  <button className="w-9 h-9 rounded-full flex items-center justify-center text-gray-400 hover:text-[#005BFF] transition-colors">
                    <Mic className="w-4 h-4" />
                  </button>
                  <button className="w-9 h-9 rounded-full flex items-center justify-center bg-[#005BFF] text-white hover:bg-blue-700 shadow-md transition-colors">
                    <SendHorizontal className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>

            {/* Product Panel */}
            <div className="w-[200px] xl:w-[215px] shrink-0 border-l border-gray-100 pl-5 flex flex-col">
              <h4 className="font-bold text-gray-900 text-[13px] mb-3">Gợi ý cho bạn</h4>

              <div className="relative flex flex-col flex-1 bg-white border border-gray-100 rounded-2xl p-3 shadow-sm hover:border-green-200 transition-colors cursor-pointer group">
                <Badge className="absolute -top-2.5 left-3 bg-green-100 text-green-700 hover:bg-green-100 border-none px-2 py-0.5 text-[10px] font-bold flex items-center gap-1 shadow-sm z-10">
                  <BadgeCheck className="w-3 h-3" /> Best Match
                </Badge>

                <div className="w-full h-[90px] flex items-center justify-center mt-3 mb-2">
                  <img src="/images/ac1.png" alt="Daikin" className="object-contain h-full group-hover:scale-105 transition-transform duration-300" />
                </div>

                <h5 className="font-bold text-gray-900 text-[12px] leading-snug mb-1.5 group-hover:text-[#005BFF] transition-colors">
                  Daikin FTKB35YVMV<br />Inverter 1.5 HP
                </h5>

                <div className="flex items-center gap-1 mb-2">
                  <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                  <span className="text-[11px] font-bold text-gray-800">4.8</span>
                  <span className="text-[10px] text-gray-500">(128 đánh giá)</span>
                </div>

                <div className="text-red-600 font-bold text-[15px] mb-2">9.990.000đ</div>

                <div className="flex flex-col gap-1.5 mb-3">
                  {features.map((f, i) => (
                    <div key={i} className="flex items-center gap-1 text-[10px] text-green-700 font-medium">
                      <BadgeCheck className="w-3 h-3 shrink-0" /> {f}
                    </div>
                  ))}
                </div>

                <Button variant="outline" className="w-full h-8 text-[11px] font-medium text-[#005BFF] border-[#005BFF] hover:bg-blue-50 rounded-lg mt-auto">
                  Xem chi tiết
                </Button>
              </div>
            </div>
          </motion.div>
        </div>

      </div>
    </section>
  )
}
