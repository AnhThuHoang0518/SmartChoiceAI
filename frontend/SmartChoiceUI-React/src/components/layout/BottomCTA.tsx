import { Button } from "../ui/button"

export function BottomCTA() {
  return (
    <section className="py-12 md:py-16">
      <div className="container mx-auto px-4">
        {/* Card Container using the image as the entire card */}
        <div className="relative min-h-[180px] md:min-h-[220px] flex items-center">
          {/* The image is the card itself */}
          <img 
            src="/images/card.png" 
            alt="AI Advisor Card" 
            className="absolute inset-0 w-full h-full object-cover object-left md:object-center drop-shadow-xl" 
          />
          
          {/* Content Wrapper */}
          <div className="relative z-10 px-6 md:px-12 py-6 md:py-8 w-full flex flex-col md:flex-row items-center justify-end md:justify-between">
            
            {/* Empty space for the robot part of the image (assuming it's on the left) */}
            <div className="hidden md:block w-32 md:w-48 lg:w-64"></div>

            <div className="flex flex-col text-center md:text-left mb-6 md:mb-0 md:flex-1 md:pl-4">
              <h2 className="text-[16px] md:text-xl lg:text-2xl font-bold text-white mb-1 md:mb-2 uppercase drop-shadow-md">
                ĐỂ AI ADVISOR GIÚP BẠN CHỌN SẢN PHẨM TỐT NHẤT!
              </h2>
              <p className="text-white/90 text-[13px] md:text-[15px] drop-shadow-md">
                Tư vấn miễn phí - Nhanh chóng - Chính xác
              </p>
            </div>

            <div className="flex-shrink-0 w-full md:w-auto mt-2 md:mt-0">
              <Button 
                className="w-full md:w-auto bg-[#FFDE00] text-[#001D6E] font-bold text-[15px] md:text-[16px] hover:bg-[#F2D300] h-12 px-8 rounded-full shadow-md hover:shadow-lg transition-all"
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
