import { Link } from 'react-router-dom';
import { articles } from '../data/articles';

export default function BlogPage() {
  const categories = ['全部', '行业分析', '技术方案', '技术专题'];

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <section className="bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white py-16">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl font-bold mb-4">技术洞察</h1>
          <p className="text-slate-300 max-w-2xl">
            深度技术解析，行业趋势分析，实战经验分享。了解USV行业最新动态和技术方案。
          </p>
        </div>
      </section>

      {/* Filter */}
      <section className="py-6 bg-white border-b">
        <div className="container mx-auto px-4">
          <div className="flex flex-wrap gap-2">
            {categories.map((category) => (
              <button
                key={category}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  category === '全部'
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                {category}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Articles Grid */}
      <section className="py-12">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {articles.map((article) => (
              <Link
                key={article.id}
                to={`/blog/${article.id}`}
                className="bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-lg transition-all group"
              >
                {/* Article Image/Header */}
                <div className="h-48 bg-gradient-to-br from-slate-700 to-slate-900 flex items-center justify-center relative">
                  <div className="text-center text-white px-6">
                    <span className="inline-block px-3 py-1 bg-white/20 rounded-full text-xs mb-3">
                      {article.category}
                    </span>
                    <h3 className="text-lg font-semibold line-clamp-2">
                      {article.title}
                    </h3>
                  </div>
                  <div className="absolute top-4 right-4 bg-blue-600 text-white text-xs px-2 py-1 rounded">
                    {article.readTime}分钟
                  </div>
                </div>

                {/* Content */}
                <div className="p-6">
                  <p className="text-slate-600 text-sm mb-4 line-clamp-3">
                    {article.excerpt}
                  </p>

                  {/* Tags */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    {article.tags.slice(0, 3).map((tag) => (
                      <span
                        key={tag}
                        className="px-2 py-1 bg-slate-100 text-slate-600 text-xs rounded"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>

                  {/* Meta */}
                  <div className="flex justify-between items-center text-sm text-slate-500">
                    <span>{article.author}</span>
                    <span>{article.date}</span>
                  </div>

                  {/* Read More */}
                  <div className="mt-4 pt-4 border-t border-slate-100">
                    <span className="text-blue-600 font-medium text-sm group-hover:text-blue-700">
                      阅读全文 →
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Newsletter */}
      <section className="py-16 bg-gradient-to-r from-blue-600 to-cyan-600 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-2xl font-bold mb-4">订阅技术洞察</h2>
          <p className="text-blue-100 mb-6 max-w-xl mx-auto">
            获取最新的USV行业分析、技术方案和实战经验
          </p>
          <form className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
            <input
              type="email"
              placeholder="输入您的邮箱"
              className="flex-1 px-4 py-3 rounded-lg text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-300"
            />
            <button
              type="submit"
              className="px-6 py-3 bg-white text-blue-600 rounded-lg font-semibold hover:bg-blue-50 transition-colors"
            >
              订阅
            </button>
          </form>
        </div>
      </section>
    </div>
  );
}
