import { Button } from "../ui/button"

export function BottomCTA() {
  return (
    <section className="relative z-10 -mt-26 -mb-30 md:-mt-[190px] md:-mb-[230px] lg:-mt-[235px] lg:-mb-[295px] pointer-events-none">
      <div className="container mx-auto px-4 pointer-events-auto">
        {/* Card Container using the image as the entire card */}
        <div className="relative w-full max-w-[1200px] mx-auto flex items-center justify-center">
          {/* The image is the card itself */}
          <img
            src="/images/card.png"
            alt="AI Advisor Card"
            className="w-full h-auto object-contain drop-shadow-2xl"
          />

          {/* Content Wrapper */}
          <div className="absolute inset-0 z-10 px-6 md:px-12 py-4 w-full flex flex-col md:flex-row items-center justify-end md:justify-between transform -translate-y-1 md:-translate-y-5">

            {/* Empty space for the robot part of the image (assuming it's on the left) */}
            <div className="hidden md:block w-32 md:w-48 lg:w-64 flex-shrink-0"></div>

            <div className="flex flex-col text-center md:text-left mb-2 md:mb-0 md:flex-1 md:pl-8">
              <h2 className="text-[16px] md:text-2xl lg:text-[28px] leading-tight font-black text-white mb-1 md:mb-2 uppercase drop-shadow-lg">
                ĐỂ AI ADVISOR GIÚP BẠN<br className="hidden md:block" /> CHỌN SẢN PHẨM TỐT NHẤT!
              </h2>
              <p className="text-white/95 text-[13px] md:text-[16px] drop-shadow-md font-medium">
                Tư vấn miễn phí - Nhanh chóng - Chính xác
              </p>
            </div>

            <div className="flex-shrink-0 w-full md:w-auto mt-2 md:mt-0 flex justify-center">
              <Button
                onClick={() => { window.location.href = "/chat" }}
                className="w-full md:w-auto bg-[#FFDE00] text-[#001D6E] font-extrabold text-[15px] md:text-[18px] hover:bg-[#F2D300] hover:-translate-y-1 h-10 md:h-14 px-8 md:px-10 rounded-full shadow-lg hover:shadow-xl transition-all duration-300"
              >
                Bắt đầu ngay
              </Button>
            </div>

          </div>
        </div>
      </div>
    </section>
  )
}
