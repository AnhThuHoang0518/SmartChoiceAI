import { MapPin } from "lucide-react"

const Facebook = ({ className }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z" />
  </svg>
)

const Youtube = ({ className }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M22.54 6.42a2.78 2.78 0 0 0-1.94-2C18.88 4 12 4 12 4s-6.88 0-8.6.46a2.78 2.78 0 0 0-1.94 2A29 29 0 0 0 1 11.75a29 29 0 0 0 .46 5.33A2.78 2.78 0 0 0 3.4 19c1.72.46 8.6.46 8.6.46s6.88 0 8.6-.46a2.78 2.78 0 0 0 1.94-2 29 29 0 0 0 .46-5.25 29 29 0 0 0-.46-5.33z" />
    <polygon points="9.75 15.02 15.5 11.75 9.75 8.48 9.75 15.02" />
  </svg>
)

const Instagram = ({ className }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <rect width="20" height="20" x="2" y="2" rx="5" ry="5" />
    <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z" />
    <line x1="17.5" x2="17.51" y1="6.5" y2="6.5" />
  </svg>
)

export function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200 text-sm text-gray-700">
      {/* Main Footer Links */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">

          {/* Column 1 */}
          <div>
            <h4 className="font-bold text-[#001D6E] mb-4 uppercase text-[13px]">Tổng đài hỗ trợ (Miễn phí)</h4>
            <ul className="space-y-3 text-[13px]">
              <li className="flex items-center gap-2">
                <span className="text-gray-600">Gọi mua:</span>
                <a href="#" className="font-bold text-[#005BFF] hover:underline">1800.1061</a>
                <span className="text-gray-500 text-xs">(7:30 - 22:00)</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-gray-600">Kỹ thuật:</span>
                <a href="#" className="font-bold text-[#005BFF] hover:underline">1800.1764</a>
                <span className="text-gray-500 text-xs">(7:30 - 22:00)</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-gray-600">Khiếu nại:</span>
                <a href="#" className="font-bold text-[#005BFF] hover:underline">1800.1063</a>
                <span className="text-gray-500 text-xs">(8:00 - 21:30)</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-gray-600">Bảo hành:</span>
                <a href="#" className="font-bold text-[#005BFF] hover:underline">1800.1065</a>
                <span className="text-gray-500 text-xs">(8:00 - 21:00)</span>
              </li>
            </ul>
          </div>

          {/* Column 2 */}
          <div>
            <h4 className="font-bold text-[#001D6E] mb-4 uppercase text-[13px]">Thông tin công ty</h4>
            <ul className="space-y-3 text-[13px]">
              <li><a href="#" className="hover:text-[#005BFF] hover:underline transition-colors">Giới thiệu công ty (MWG.vn)</a></li>
              <li><a href="#" className="hover:text-[#005BFF] hover:underline transition-colors">Tuyển dụng</a></li>
              <li><a href="#" className="hover:text-[#005BFF] hover:underline transition-colors">Gửi góp ý, khiếu nại</a></li>
              <li><a href="#" className="hover:text-[#005BFF] hover:underline transition-colors flex items-center gap-1"><MapPin className="w-4 h-4" /> Tìm siêu thị (3300+ shop)</a></li>
              <li><a href="#" className="hover:text-[#005BFF] hover:underline transition-colors">Xem bản mobile</a></li>
            </ul>
          </div>

          {/* Column 3 */}
          <div>
            <h4 className="font-bold text-[#001D6E] mb-4 uppercase text-[13px]">Chính sách & Hỗ trợ</h4>
            <ul className="space-y-3 text-[13px]">
              <li><a href="#" className="hover:text-[#005BFF] hover:underline transition-colors">Tích điểm Quà tặng VIP</a></li>
              <li><a href="#" className="hover:text-[#005BFF] hover:underline transition-colors">Lịch sử mua hàng</a></li>
              <li><a href="#" className="hover:text-[#005BFF] hover:underline transition-colors">Chính sách trả góp</a></li>
              <li><a href="#" className="hover:text-[#005BFF] hover:underline transition-colors">Chính sách bảo hành</a></li>
              <li><a href="#" className="hover:text-[#005BFF] hover:underline transition-colors">Chính sách đổi trả</a></li>
            </ul>
          </div>

          {/* Column 4 */}
          <div>
            <h4 className="font-bold text-[#001D6E] mb-4 uppercase text-[13px]">Kết nối với chúng tôi</h4>
            <div className="flex items-center gap-3 mb-6">
              <a href="#" className="w-8 h-8 rounded-full bg-[#005BFF] text-white flex items-center justify-center hover:bg-[#0046CC] transition-colors"><Facebook className="w-4 h-4" /></a>
              <a href="#" className="w-8 h-8 rounded-full bg-red-600 text-white flex items-center justify-center hover:bg-red-700 transition-colors"><Youtube className="w-4 h-4" /></a>
              <a href="#" className="w-8 h-8 rounded-full bg-gradient-to-tr from-yellow-400 via-pink-500 to-purple-500 text-white flex items-center justify-center hover:opacity-90 transition-opacity"><Instagram className="w-4 h-4" /></a>
            </div>
            <h4 className="font-bold text-[#001D6E] mb-3 uppercase text-[13px]">Website cùng tập đoàn</h4>
            <div className="flex flex-wrap gap-2 text-[12px]">
              <span className="px-2 py-1 bg-gray-50 border border-gray-200 rounded text-gray-700 hover:bg-gray-100 cursor-pointer transition-colors">Thế Giới Di Động</span>
              <span className="px-2 py-1 bg-green-50 border border-green-200 rounded text-green-700 font-medium hover:bg-green-100 cursor-pointer transition-colors">Bách Hóa XANH</span>
              <span className="px-2 py-1 bg-blue-50 border border-blue-200 rounded text-blue-600 font-medium hover:bg-blue-100 cursor-pointer transition-colors">Nhà Thuốc An Khang</span>
              <span className="px-2 py-1 bg-purple-50 border border-purple-200 rounded text-purple-700 font-medium hover:bg-purple-100 cursor-pointer transition-colors">AVAKids</span>
            </div>
          </div>

        </div>
      </div>

      {/* Bottom Copyright */}
      <div className="bg-[#F8F9FA] py-6">
        <div className="container mx-auto px-4 text-center text-[12px] text-gray-500 leading-relaxed">
          <p>© 2026. Công ty Cổ phần Thế Giới Di Động. GPDKKD: 0303217354 do sở KH & ĐT TP.HCM cấp ngày 02/01/2007.</p>
          <p className="mt-1">Địa chỉ: 128 Trần Quang Khải, P.Tân Định, Q.1, TP.Hồ Chí Minh. Điện thoại: 028 38125960. Email: cskh@thegioididong.com.</p>
        </div>
      </div>
    </footer>
  )
}
