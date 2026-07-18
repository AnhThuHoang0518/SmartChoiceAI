import { Routes, Route } from "react-router-dom"
import { Navbar } from "./components/layout/Navbar"
import { CategoryNavigation } from "./components/layout/CategoryNavigation"
import { Footer } from "./components/layout/Footer"
import Home from "./pages/Home"
import CategoryDetail from "./pages/CategoryDetail"

function App() {
  return (
    <div className="min-h-screen flex flex-col bg-background font-sans">
      <Navbar />
      <CategoryNavigation />
      
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/category/:slug" element={<CategoryDetail />} />
      </Routes>

      <Footer />
    </div>
  )
}

export default App
