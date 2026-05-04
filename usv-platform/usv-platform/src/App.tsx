import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { useState } from 'react';
import HomePage from './pages/HomePage';
import SolutionsPage from './pages/SolutionsPage';
import SolutionDetailPage from './pages/SolutionDetailPage';
import BlogPage from './pages/BlogPage';
import ArticleDetailPage from './pages/ArticleDetailPage';
import AboutPage from './pages/AboutPage';
import ContactPage from './pages/ContactPage';

function Navigation() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <nav className="bg-white shadow-sm sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <img src="/logo.png" alt="XUSV" className="w-10 h-10 object-contain rounded-lg" />
            <span className="font-bold text-xl text-slate-900">XUSV油改电AI艇</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-8">
            <Link to="/" className="text-slate-600 hover:text-blue-600 font-medium transition-colors">
              首页
            </Link>
            <Link to="/solutions" className="text-slate-600 hover:text-blue-600 font-medium transition-colors">
              方案库
            </Link>
            <Link to="/blog" className="text-slate-600 hover:text-blue-600 font-medium transition-colors">
              技术洞察
            </Link>
            <Link to="/about" className="text-slate-600 hover:text-blue-600 font-medium transition-colors">
              关于我们
            </Link>
            <Link
              to="/contact"
              className="px-5 py-2 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-lg font-medium hover:shadow-lg transition-all"
            >
              立即咨询
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 text-slate-600"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            )}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-slate-100 py-4">
            <div className="flex flex-col gap-4">
              <Link
                to="/"
                className="text-slate-600 hover:text-blue-600 font-medium transition-colors px-2 py-2"
                onClick={() => setMobileMenuOpen(false)}
              >
                首页
              </Link>
              <Link
                to="/solutions"
                className="text-slate-600 hover:text-blue-600 font-medium transition-colors px-2 py-2"
                onClick={() => setMobileMenuOpen(false)}
              >
                方案库
              </Link>
              <Link
                to="/blog"
                className="text-slate-600 hover:text-blue-600 font-medium transition-colors px-2 py-2"
                onClick={() => setMobileMenuOpen(false)}
              >
                技术洞察
              </Link>
              <Link
                to="/about"
                className="text-slate-600 hover:text-blue-600 font-medium transition-colors px-2 py-2"
                onClick={() => setMobileMenuOpen(false)}
              >
                关于我们
              </Link>
              <Link
                to="/contact"
                className="px-5 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-lg font-medium text-center"
                onClick={() => setMobileMenuOpen(false)}
              >
                立即咨询
              </Link>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}

function Footer() {
  return (
    <footer className="bg-slate-900 text-white py-12">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <img src="/logo.png" alt="XUSV" className="w-10 h-10 object-contain rounded-lg" />
              <span className="font-bold text-xl">XUSV油改电AI艇</span>
            </div>
            <p className="text-slate-400 text-sm">
              国内领先XUSV油改电配套方案平台，让每一艘船都能智能电动化。
            </p>
          </div>

          <div>
            <h4 className="font-semibold mb-4">快速链接</h4>
            <ul className="space-y-2 text-slate-400">
              <li><Link to="/solutions" className="hover:text-white transition-colors">方案库</Link></li>
              <li><Link to="/blog" className="hover:text-white transition-colors">技术洞察</Link></li>
              <li><Link to="/about" className="hover:text-white transition-colors">关于我们</Link></li>
              <li><Link to="/contact" className="hover:text-white transition-colors">联系我们</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold mb-4">服务范围</h4>
            <ul className="space-y-2 text-slate-400">
              <li>XUSV油改电方案设计</li>
              <li>硬件选型咨询</li>
              <li>系统集成服务</li>
              <li>技术培训支持</li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold mb-4">联系方式</h4>
            <ul className="space-y-2 text-slate-400">
              <li>📧 luly101@163.com</li>
              <li>📱 150-2695-3905</li>
              <li>📍 上海市</li>
            </ul>
          </div>
        </div>

        <div className="border-t border-slate-800 mt-8 pt-8 text-center text-slate-400 text-sm">
          <p>&copy; 2025 XUSV油改电. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col bg-slate-50">
        <Navigation />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/solutions" element={<SolutionsPage />} />
            <Route path="/solutions/:id" element={<SolutionDetailPage />} />
            <Route path="/blog" element={<BlogPage />} />
            <Route path="/blog/:id" element={<ArticleDetailPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/contact" element={<ContactPage />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  );
}

export default App;
