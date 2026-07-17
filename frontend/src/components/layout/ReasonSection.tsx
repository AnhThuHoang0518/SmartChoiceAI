import { ShieldCheck, MessageCircle, Clock, ShoppingCart } from "lucide-react"

export function ReasonSection() {
  const reasons = [
    {
      icon: <ShieldCheck className="w-8 h-8 text-[#005BFF]" strokeWidth={1.5} />,
      title: "Dữ liệu chính xác",
      desc: "Từ hàng ngàn sản phẩm và đánh giá thật"
    },
    {
      icon: <MessageCircle className="w-8 h-8 text-[#005BFF]" strokeWidth={1.5} />,
      title: "Tư vấn thông minh",
      desc: "AI đặt câu hỏi và hiểu đúng nhu cầu"
    },
    {
      icon: <Clock className="w-8 h-8 text-[#005BFF]" strokeWidth={1.5} />,
      title: "Tiết kiệm thời gian",
      desc: "Tìm sản phẩm phù hợp chỉ trong vài phút"
    },
    {
      icon: <ShoppingCart className="w-8 h-8 text-[#005BFF]" strokeWidth={1.5} />,
      title: "Mua sắm dễ dàng",
      desc: "Xem giá, tồn kho, mua online thuận tiện"
    }
  ]

  return (
    <section className="py-10 bg-white mt-4">
      <div className="container mx-auto px-4">
        <h2 className="text-[18px] md:text-[22px] font-bold mb-8 text-[#001D6E] uppercase text-center">
          VÌ SAO NÊN CHỌN AI ADVISOR CỦA SMARTCHOICEAI?
        </h2>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 md:gap-8">
          {reasons.map((reason, index) => (
            <div key={index} className="flex flex-col items-center text-center">
              <div className="w-16 h-16 md:w-20 md:h-20 rounded-full bg-[#E8F0FF] flex items-center justify-center mb-4">
                {reason.icon}
              </div>
              <h3 className="font-bold text-[14px] md:text-[16px] text-slate-800 mb-2">{reason.title}</h3>
              <p className="text-gray-500 text-[12px] md:text-[14px] leading-snug px-1">{reason.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

