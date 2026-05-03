import { useParams, Link } from 'react-router-dom';
import { articles } from '../data/articles';

export default function ArticleDetailPage() {
  const { id } = useParams();
  const article = articles.find((a) => a.id === id);

  if (!article) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-slate-900 mb-4">文章未找到</h1>
          <Link to="/blog" className="text-blue-600 hover:underline">
            返回博客
          </Link>
        </div>
      </div>
    );
  }

  // Convert markdown-like content to HTML
  const renderContent = (content: string) => {
    return content.split('\n').map((line, index) => {
      // Remove bold markers **...** and convert to span
      const processBold = (text: string) => {
        return text.split(/(\*\*[^*]+\*\*)/).map((part, i) => {
          if (part.startsWith('**') && part.endsWith('**')) {
            return <strong key={i}>{part.slice(2, -2)}</strong>;
          }
          return part;
        });
      };

      if (line.startsWith('# ')) {
        return (
          <h1 key={index} className="text-3xl font-bold text-slate-900 mt-12 mb-6">
            {line.substring(2)}
          </h1>
        );
      }
      if (line.startsWith('## ')) {
        return (
          <h2 key={index} className="text-2xl font-bold text-slate-900 mt-10 mb-4">
            {line.substring(3)}
          </h2>
        );
      }
      if (line.startsWith('### ')) {
        return (
          <h3 key={index} className="text-xl font-bold text-slate-900 mt-8 mb-3">
            {line.substring(4)}
          </h3>
        );
      }
      if (line.startsWith('#### ')) {
        return (
          <h4 key={index} className="text-lg font-bold text-slate-900 mt-6 mb-2">
            {line.substring(5)}
          </h4>
        );
      }
      if (line.startsWith('| ')) {
        // Simple table parsing
        const cells = line.split('|').filter(cell => cell.trim());
        return (
          <div key={index} className="grid grid-cols- gap-4 py-2 border-b border-slate-100">
            {cells.map((cell, i) => (
              <span key={i} className="text-slate-700">{cell.trim()}</span>
            ))}
          </div>
        );
      }
      if (line.startsWith('- ')) {
        return (
          <li key={index} className="ml-6 text-slate-700 list-disc mb-2">
            {line.substring(2)}
          </li>
        );
      }
      if (line.startsWith('```')) {
        return null; // Skip code block markers
      }
      if (line.trim() === '') {
        return <div key={index} className="h-4"></div>;
      }
      // Regular paragraph with bold text support
      if (line.trim()) {
        return (
          <p key={index} className="text-slate-700 leading-relaxed mb-4">
            {processBold(line)}
          </p>
        );
      }
      return null;
    });
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <section className="bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white py-16">
        <div className="container mx-auto px-4 max-w-4xl">
          <Link to="/blog" className="text-blue-400 hover:text-blue-300 mb-6 inline-block">
            ← 返回博客
          </Link>
          <div className="mb-4">
            <span className="inline-block px-3 py-1 bg-blue-500/30 rounded-full text-sm">
              {article.category}
            </span>
          </div>
          <h1 className="text-4xl font-bold mb-6">{article.title}</h1>
          <div className="flex flex-wrap gap-4 text-slate-300 text-sm">
            <span>{article.author}</span>
            <span>·</span>
            <span>{article.date}</span>
            <span>·</span>
            <span>{article.readTime}分钟阅读</span>
          </div>
        </div>
      </section>

      {/* Article Content */}
      <section className="py-12">
        <div className="container mx-auto px-4 max-w-4xl">
          <div className="bg-white rounded-2xl shadow-sm p-8 md:p-12">
            {/* Excerpt */}
            <div className="text-xl text-slate-600 italic border-l-4 border-blue-500 pl-6 mb-8">
              {article.excerpt}
            </div>

            {/* Content */}
            <div className="prose max-w-none">
              {renderContent(article.content)}
            </div>

            {/* Tags */}
            <div className="mt-12 pt-8 border-t border-slate-200">
              <div className="flex flex-wrap gap-2">
                {article.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-3 py-1 bg-slate-100 text-slate-600 text-sm rounded-full"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Author Card */}
      <section className="py-8">
        <div className="container mx-auto px-4 max-w-4xl">
          <div className="bg-white rounded-2xl shadow-sm p-8">
            <div className="flex items-center gap-6">
              <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-full flex items-center justify-center text-white text-2xl font-bold">
                卢
              </div>
              <div>
                <h3 className="text-xl font-bold text-slate-900 mb-2">卢继雄</h3>
                <p className="text-slate-600 mb-3">
                  18年硬件+AI研发经验，专注USV油改电方案设计。曾主导3200+台移动储能充电机器人全球量产。
                </p>
                <div className="flex gap-3">
                  <Link
                    to="/about"
                    className="text-blue-600 font-medium text-sm hover:text-blue-700"
                  >
                    了解更多 →
                  </Link>
                  <Link
                    to="/contact"
                    className="text-blue-600 font-medium text-sm hover:text-blue-700"
                  >
                    联系我 →
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Related Articles */}
      <section className="py-8 pb-16">
        <div className="container mx-auto px-4 max-w-4xl">
          <h2 className="text-2xl font-bold text-slate-900 mb-6">相关阅读</h2>
          <div className="grid md:grid-cols-2 gap-6">
            {articles
              .filter((a) => a.id !== article.id)
              .slice(0, 2)
              .map((relatedArticle) => (
                <Link
                  key={relatedArticle.id}
                  to={`/blog/${relatedArticle.id}`}
                  className="bg-white rounded-xl p-6 shadow-sm hover:shadow-lg transition-all"
                >
                  <span className="text-xs text-blue-600 font-medium">
                    {relatedArticle.category}
                  </span>
                  <h3 className="text-lg font-semibold text-slate-900 mt-2 mb-3 line-clamp-2">
                    {relatedArticle.title}
                  </h3>
                  <div className="flex justify-between text-sm text-slate-500">
                    <span>{relatedArticle.author}</span>
                    <span>{relatedArticle.readTime}分钟</span>
                  </div>
                </Link>
              ))}
          </div>
        </div>
      </section>
    </div>
  );
}
