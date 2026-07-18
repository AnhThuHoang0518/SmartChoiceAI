import { motion } from "framer-motion"

const CustomMessageIcon = ({ className }: { className?: string }) => (
  <svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg" className={className}>
    <path d="M19 4H5C3.34315 4 2 5.34315 2 7V20.5C2 21.3931 3.07823 21.839 3.70711 21.2101L7 17.9171H19C20.6569 17.9171 22 16.5739 22 14.9171V7C22 5.34315 20.6569 4 19 4Z" />
    <circle cx="7.5" cy="11" r="1.5" fill="white" />
    <circle cx="12" cy="11" r="1.5" fill="white" />
    <circle cx="16.5" cy="11" r="1.5" fill="white" />
  </svg>
)

const CustomScaleIcon = ({ className }: { className?: string }) => (
  <svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg" className={className}>
    <path d="M11 2C10.4477 2 10 2.44772 10 3C10 3.55228 10.4477 4 11 4H11.5V19H8C7.44772 19 7 19.4477 7 20C7 20.5523 7.44772 21 8 21H16C16.5523 21 17 20.5523 17 20C17 19.4477 16.5523 19 16 19H12.5V4H13C13.5523 4 14 3.55228 14 3C14 2.44772 13.5523 2 13 2H11Z" />
    <path d="M4 6H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    <path d="M4 7L2 14H6L4 7Z" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
    <path d="M1 15C1 16.6569 2.34315 18 4 18C5.65685 18 7 16.6569 7 15H1Z" />
    <path d="M20 7L18 14H22L20 7Z" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
    <path d="M17 15C17 16.6569 18.3431 18 20 18C21.6569 18 23 16.6569 23 15H17Z" />
  </svg>
)

const CustomBulbIcon = ({ className }: { className?: string }) => (
  <svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg" className={className}>
    <path d="M12 5C9.23858 5 7 7.23858 7 10C7 11.832 8.01633 13.4326 9.47953 14.3031C9.84587 14.5212 10.1691 14.8622 10.3664 15.3056C10.4285 15.4452 10.5 15.7538 10.5 16.5H13.5C13.5 15.7538 13.5715 15.4452 13.6336 15.3056C13.8309 14.8622 14.1541 14.5212 14.5205 14.3031C15.9837 13.4326 17 11.832 17 10C17 7.23858 14.7614 5 12 5Z" />
    <rect x="10.5" y="17.5" width="3" height="1.5" rx="0.5" fill="#F59E0B" />
    <rect x="11" y="20" width="2" height="1.5" rx="0.5" fill="#F59E0B" />
    <path d="M12 1.5V3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    <path d="M5.5 3.5L6.5 4.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    <path d="M18.5 3.5L17.5 4.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    <path d="M2.5 10H4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    <path d="M21.5 10H20" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
  </svg>
)

const CustomShieldIcon = ({ className }: { className?: string }) => (
  <svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg" className={className}>
    <path d="M11.2359 2.2131C11.7196 1.92897 12.2804 1.92897 12.7641 2.2131L20.2641 6.62486C20.724 6.89531 21 7.39162 21 7.92523V12C21 17.5758 17.3822 22.3888 12.3533 23.8643C12.1228 23.9319 11.8772 23.9319 11.6467 23.8643C6.61783 22.3888 3 17.5758 3 12V7.92523C3 7.39162 3.27599 6.89531 3.73587 6.62486L11.2359 2.2131Z" />
    <path d="M16.5303 9.53033C16.8232 9.23744 16.8232 8.76256 16.5303 8.46967C16.2374 8.17678 15.7626 8.17678 15.4697 8.46967L10.5 13.4393L8.53033 11.4697C8.23744 11.1768 7.76256 11.1768 7.46967 11.4697C7.17678 11.7626 7.17678 12.2374 7.46967 12.5303L9.96967 15.0303C10.2626 15.3232 10.7374 15.3232 11.0303 15.0303L16.5303 9.53033Z" fill="white" />
  </svg>
)

const features = [
  {
    icon: CustomMessageIcon,
    title: "Hiểu nhu cầu thật",
    description: "AI đặt câu hỏi thông minh để hiểu đúng nhu cầu của bạn",
    color: "text-[#005BFF]",
    bg: "bg-[#E6F0FF]"
  },
  {
    icon: CustomScaleIcon,
    title: "So sánh khách quan",
    description: "So sánh hàng ngàn sản phẩm dựa trên dữ liệu thực tế",
    color: "text-[#10B981]",
    bg: "bg-[#E6F9F0]"
  },
  {
    icon: CustomBulbIcon,
    title: "Giải thích dễ hiểu",
    description: "AI giải thích lý do chọn sản phẩm một cách rõ ràng",
    color: "text-[#F59E0B]",
    bg: "bg-[#FEF5E6]"
  },
  {
    icon: CustomShieldIcon,
    title: "Nguồn minh bạch",
    description: "Giá và khuyến mãi kèm nguồn; hệ thống nói rõ khi thiếu thời điểm cập nhật hoặc tồn kho",
    color: "text-[#8B5CF6]",
    bg: "bg-[#F3E8FF]"
  }
]

export function FeatureSection() {
  return (
    <section className="relative z-20 container mx-auto px-4 -mt-10 lg:-mt-14 mb-8">
      <div className="bg-white rounded-[24px] shadow-[0_8px_30px_rgb(0,0,0,0.06)] p-6 lg:p-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8 border border-gray-100">
        {features.map((feature, i) => (
          <motion.div
            key={i}
            whileHover={{ y: -4 }}
            className="flex items-start gap-4 cursor-pointer group"
          >
            <div className={`w-[88px] h-[88px] rounded-[24px] ${feature.bg} flex items-center justify-center flex-shrink-0 transition-transform duration-300 group-hover:scale-105`}>
              <feature.icon className={`w-12 h-12 ${feature.color}`} />
            </div>
            <div className="flex flex-col pt-1">
              <h3 className="font-bold text-[15px] lg:text-[16px] text-[#001D6E] mb-1 group-hover:text-[#005BFF] transition-colors">{feature.title}</h3>
              <p className="text-gray-500 text-[13px] leading-relaxed pr-2">{feature.description}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  )
}
