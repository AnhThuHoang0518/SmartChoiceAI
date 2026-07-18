import { Search, MapPin, PhoneCall, ShoppingCart, User } from "lucide-react"
import { Button } from "../ui/button"
import { Link } from "react-router-dom"

export function Navbar() {
  return (
    <header className="h-[80px] bg-white border-b border-border sticky top-0 z-50 flex items-center">
      <div className="container mx-auto px-4 flex items-center justify-between gap-8">
        {/* Logo */}
        <Link to="/" className="flex-shrink-0 flex items-center -ml-4 md:-ml-11">
          <img src="/images/Logo.png" alt="smartchoiceAI logo" className="h-[60px] md:h-[72px] w-auto object-contain" />
        </Link>

        {/* Search */}
        <div className="flex-1 max-w-2xl relative hidden md:block">
          <input
            type="text"
            placeholder="Bạn tìm gì hôm nay?"
            className="w-full h-12 pl-4 pr-12 rounded-full bg-background border border-border focus:outline-none focus:ring-2 focus:ring-primary/50 text-body transition-shadow"
          />
          <button className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 flex items-center justify-center bg-primary rounded-full text-white hover:bg-primary/90 transition-colors">
            <Search className="w-4 h-4" />
          </button>
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-6">
          <button className="flex flex-col items-center gap-1 text-secondary-text hover:text-primary transition-colors hidden lg:flex">
            <MapPin className="w-5 h-5" />
            <span className="text-[11px] font-medium">Vị trí</span>
          </button>
          <button className="flex flex-col items-center gap-1 text-secondary-text hover:text-primary transition-colors hidden lg:flex">
            <PhoneCall className="w-5 h-5" />
            <span className="text-[11px] font-medium">1800.1061</span>
          </button>
          <button className="flex flex-col items-center gap-1 text-secondary-text hover:text-primary transition-colors relative">
            <ShoppingCart className="w-5 h-5" />
            <span className="text-[11px] font-medium">Giỏ hàng</span>
            <span className="absolute -top-1 -right-1 bg-secondary text-text text-[10px] font-bold w-4 h-4 rounded-full flex items-center justify-center">2</span>
          </button>
          <button className="flex flex-col items-center gap-1 text-secondary-text hover:text-primary transition-colors hidden sm:flex">
            <User className="w-5 h-5" />
            <span className="text-[11px] font-medium">Đăng nhập</span>
          </button>

          <Button className="hidden md:flex" onClick={() => { window.location.href = "/chat" }}>Tư vấn AI</Button>
        </div>
      </div>
    </header>
  )
}
