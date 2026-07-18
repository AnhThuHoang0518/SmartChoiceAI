import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { Tag } from "lucide-react"
import { Button } from "../ui/button"

// TRUOC: 4 san pham hardcode voi gia + sao + so danh gia BIA. Ca he thong
// pitch "moi con so deu co nguon" - landing khong duoc la ngoai le.
// GIO: keo top may giam sau nhat THAT tu /api/khuyen-mai (gia goc/gia KM
// trong catalog DMX). Khong co du lieu danh gia sao -> khong hien sao.

type KhuyenMai = { ten: string; gia: number; gia_goc: number; phan_tram: number; giam: number; qua?: string; anh_url?: string }

const anh = ["/images/ac1.png", "/images/ac2.png", "/images/ac3.png", "/images/ac4.png"]
const vnd = (n: number) => n.toLocaleString("vi-VN") + "đ"
const denChat = (hoi: string) => {
  window.location.href = `/chat?hoi=${encodeURIComponent(hoi)}`
}

export function ProductRecommendation() {
  const [ds, setDs] = useState<KhuyenMai[]>([])
  useEffect(() => {
    fetch("/api/khuyen-mai").then(r => r.json()).then(setDs).catch(() => {})
  }, [])
  if (!ds.length) return null

  return (
    <section className="py-10 container mx-auto">
      <div className="mb-6">
        <h2 className="text-xl md:text-2xl font-bold text-primary uppercase">Máy lạnh đang giảm sâu nhất — giá thật từ hệ thống</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {ds.slice(0, 4).map((sp, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.1 }}
            className="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-all duration-300 border border-gray-100 flex flex-col group relative"
          >
            <div className="absolute top-4 left-4 z-10">
              <div className="flex items-center gap-1 px-2 py-1 rounded-full text-[11px] font-semibold bg-red-100 text-red-600">
                <Tag className="w-3.5 h-3.5" />
                Giảm {vnd(sp.giam)}
              </div>
            </div>

            <div className="w-full h-36 flex items-center justify-center mt-8 mb-4 overflow-hidden">
              <img src={sp.anh_url || anh[i % anh.length]} alt={sp.ten} className="object-contain h-full transition-transform duration-500 group-hover:scale-105" />
            </div>

            <div className="flex-1 flex flex-col">
              <h3 className="font-bold text-gray-900 line-clamp-2 text-sm md:text-base group-hover:text-primary transition-colors">
                {sp.ten}
              </h3>

              {sp.qua && (
                <p className="text-[11.5px] text-green-700 mt-1.5 line-clamp-2">🎁 {sp.qua}</p>
              )}

              <div className="mt-auto pt-3">
                <div className="flex items-center gap-2 mb-3 flex-wrap">
                  <span className="text-red-600 font-bold text-lg">{vnd(sp.gia)}</span>
                  <span className="text-[11px] font-semibold text-red-600 bg-red-50 px-1.5 py-0.5 rounded">-{sp.phan_tram}%</span>
                  <span className="text-xs text-gray-400 line-through">{vnd(sp.gia_goc)}</span>
                </div>

                <Button
                  onClick={() => denChat(`Tư vấn máy lạnh ${sp.ten.split(" ")[0]} đang giảm giá, hợp phòng mình không?`)}
                  className="w-full rounded-lg bg-[#005BFF] hover:bg-[#005BFF]/90 text-white font-medium h-10"
                >
                  Tư vấn máy này
                </Button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="mt-6 text-center">
        <Button
          variant="link"
          onClick={() => denChat("Máy lạnh nào đang giảm giá?")}
          className="text-[#005BFF] hover:text-[#005BFF]/80 font-medium"
        >
          Hỏi AI về tất cả khuyến mãi <span className="ml-1">→</span>
        </Button>
      </div>
    </section>
  )
}
