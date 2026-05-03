import { Link } from 'react-router-dom';
import { solutions } from '../data/solutions';
import { articles } from '../data/articles';

export default function HomePage() {
  const featuredSolutions = solutions.slice(0, 3);
  const latestArticles = articles.slice(0, 3);

  return (
    <div className="min-h-screen">
      {/* Hero Section - 整体下移，参考home.png设计 */}
      <section className="relative bg-gradient-to-b from-blue-950 via-blue-900 to-slate-900 text-white py-20 overflow-hidden">
        {/* 顶部背景装饰 */}
        <div className="absolute top-0 left-0 right-0 h-40 bg-gradient-to-b from-slate-900 to-transparent"></div>

        {/* 中心光效 */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-blue-500/10 rounded-full blur-3xl"></div>
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-cyan-400/10 rounded-full blur-2xl"></div>
        </div>

        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            {/* 主标题 */}
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6 leading-tight">
              <span className="bg-gradient-to-r from-blue-400 via-cyan-300 to-blue-400 bg-clip-text text-transparent">
                X.USV
              </span>
              <span className="text-white">——智绘深蓝，开源领航</span>
            </h1>

            {/* 副标题 */}
            <p className="text-xl md:text-2xl text-cyan-300 mb-8">
              国内首个AI无人艇开源平台，让每一片水域都拥有智慧之眼
            </p>

            {/* 描述文字 */}
            <p className="text-base md:text-lg text-slate-300 mb-6 max-w-3xl mx-auto leading-relaxed">
              不必再仰望昂贵的海洋装备——X.USV，将自主决策、环境感知与集群协同能力，装入一艘艘可定制、可复制的AI无人艇。从水文监测到应急救援，从渔业巡护到科研采样，开源架构让你自由调用核心算法、船控系统与仿真环境。
            </p>

            <p className="text-lg md:text-xl text-white font-semibold mb-8">
              代码、数据、解决方案，全部开放共享
            </p>

            
            {/* 按钮组 */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/solutions"
                className="px-8 py-4 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-xl font-semibold text-lg hover:shadow-lg hover:shadow-blue-500/30 transition-all"
              >
                查看方案库 →
              </Link>
              <Link
                to="/contact"
                className="px-8 py-4 bg-white/10 border-2 border-white/30 rounded-xl font-semibold text-lg hover:bg-white/20 transition-all"
              >
                获取定制方案
              </Link>
            </div>
          </div>
        </div>

        {/* 底部波浪效果 */}
        <div className="absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-slate-900 to-transparent"></div>
      </section>

      {/* USV Mini Product Showcase */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-end mb-12">
            <div>
              <h2 className="text-3xl font-bold text-slate-900 mb-2">XUSV Mini 产品展示</h2>
              <p className="text-slate-600">精准、高效、未来感 - 小型无人水面艇解决方案</p>
            </div>
            <Link to="/solutions/usv-mini" className="text-blue-600 hover:text-blue-700 font-medium">
              查看技术详情 →
            </Link>
          </div>

          <div className="bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 rounded-3xl overflow-hidden">
            <div className="grid lg:grid-cols-2 gap-8 items-center p-8 lg:p-12">
              {/* Product Image */}
              <div className="relative">
                <img
                  src="/open XUSV.png"
                  alt="XUSV Mini 无人水面艇"
                  className="w-full rounded-2xl shadow-2xl"
                />
                <div className="absolute -bottom-4 -right-4 bg-blue-500 text-white px-4 py-2 rounded-lg font-semibold shadow-lg">
                  XUSV Mini
                </div>
              </div>

              {/* Product Info */}
              <div className="text-white space-y-6">
                <div>
                  <h3 className="text-3xl font-bold mb-4">XUSV Mini 小型无人水面艇</h3>
                  <p className="text-slate-300 text-lg leading-relaxed">
                    精准、高效、未来感。XUSV Mini是一款专为近海巡逻、环境监测、水域搜救等场景设计的小型化无人水面艇。采用模块化设计，支持快速部署和换电，极大提升作业效率。
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white/10 rounded-xl p-4">
                    <div className="text-2xl font-bold text-cyan-400">1.5-2m</div>
                    <div className="text-sm text-slate-300">艇体长度</div>
                  </div>
                  <div className="bg-white/10 rounded-xl p-4">
                    <div className="text-2xl font-bold text-cyan-400">100km</div>
                    <div className="text-sm text-slate-300">续航里程</div>
                  </div>
                  <div className="bg-white/10 rounded-xl p-4">
                    <div className="text-2xl font-bold text-cyan-400">20km/h</div>
                    <div className="text-sm text-slate-300">最高航速</div>
                  </div>
                  <div className="bg-white/10 rounded-xl p-4">
                    <div className="text-2xl font-bold text-cyan-400">3分钟</div>
                    <div className="text-sm text-slate-300">快速换电</div>
                  </div>
                </div>

                <div className="flex flex-wrap gap-2">
                  <span className="px-3 py-1 bg-blue-500/30 border border-blue-400/30 rounded-full text-sm">
                    AI智能感知
                  </span>
                  <span className="px-3 py-1 bg-green-500/30 border border-green-400/30 rounded-full text-sm">
                    模块化换电
                  </span>
                  <span className="px-3 py-1 bg-purple-500/30 border border-purple-400/30 rounded-full text-sm">
                    低功耗设计
                  </span>
                  <span className="px-3 py-1 bg-cyan-500/30 border border-cyan-400/30 rounded-full text-sm">
                    远程监控
                  </span>
                </div>

                <Link
                  to="/solutions/usv-mini"
                  className="inline-block px-8 py-4 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-lg font-semibold hover:shadow-lg hover:shadow-blue-500/30 transition-all"
                >
                  查看完整技术方案 →
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Solutions */}
      <section className="py-20 bg-slate-50">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-end mb-12">
            <div>
              <h2 className="text-3xl font-bold text-slate-900 mb-2">精选方案库</h2>
              <p className="text-slate-600">覆盖主流艇型，精准硬件选型，详细成本估算</p>
            </div>
            <Link to="/solutions" className="text-blue-600 hover:text-blue-700 font-medium">
              查看全部方案 →
            </Link>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {featuredSolutions.map((solution) => (
              <Link
                key={solution.id}
                to={`/solutions/${solution.id}`}
                className="group bg-gradient-to-br from-slate-50 to-slate-100 rounded-2xl overflow-hidden hover:shadow-xl transition-all"
              >
                <div className="h-48 bg-gradient-to-br from-blue-600 to-cyan-600 flex items-center justify-center">
                  <div className="text-white text-center">
                    <div className="text-4xl font-bold">{solution.boatLength}米</div>
                    <div className="text-sm opacity-80">{solution.boatType}</div>
                  </div>
                </div>
                <div className="p-6">
                  <h3 className="text-lg font-semibold text-slate-900 mb-2 group-hover:text-blue-600 transition-colors">
                    {solution.name}
                  </h3>
                  <div className="flex flex-wrap gap-2 mb-4">
                    <span className="px-3 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                      {solution.batteryCapacity}kWh电池
                    </span>
                    <span className="px-3 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                      {solution.speed}km/h航速
                    </span>
                    <span className="px-3 py-1 bg-purple-100 text-purple-700 text-xs rounded-full">
                      {solution.range}km续航
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-900 font-bold">{solution.price}</span>
                    <span className="text-blue-600 text-sm group-hover:translate-x-1 transition-transform">
                      查看详情 →
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Latest Articles */}
      <section className="py-20 bg-slate-50">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-end mb-12">
            <div>
              <h2 className="text-3xl font-bold text-slate-900 mb-2">技术洞察</h2>
              <p className="text-slate-600">深度技术解析，行业趋势分析，实战经验分享</p>
            </div>
            <Link to="/blog" className="text-blue-600 hover:text-blue-700 font-medium">
              阅读更多 →
            </Link>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {latestArticles.map((article) => (
              <Link
                key={article.id}
                to={`/blog/${article.id}`}
                className="bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-lg transition-all group"
              >
                <div className="h-40 bg-gradient-to-br from-slate-700 to-slate-900 flex items-center justify-center">
                  <div className="text-white/80 text-sm px-4 text-center">
                    {article.category}
                  </div>
                </div>
                <div className="p-6">
                  <h3 className="text-lg font-semibold text-slate-900 mb-3 group-hover:text-blue-600 transition-colors line-clamp-2">
                    {article.title}
                  </h3>
                  <p className="text-slate-600 text-sm mb-4 line-clamp-2">
                    {article.excerpt}
                  </p>
                  <div className="flex justify-between items-center text-sm text-slate-500">
                    <span>{article.author}</span>
                    <span>{article.readTime}分钟阅读</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Value Proposition */}
      <section className="py-20 bg-slate-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">为什么选择我们</h2>
            <p className="text-slate-600 max-w-2xl mx-auto">
              我们不只是卖产品，我们提供的是经过验证的完整技术方案和行业资源
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white p-8 rounded-2xl shadow-sm hover:shadow-lg transition-shadow">
              <div className="w-14 h-14 bg-blue-100 rounded-xl flex items-center justify-center mb-6">
                <svg className="w-7 h-7 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-slate-900 mb-3">18年硬核经验</h3>
              <p className="text-slate-600">
                从芯片级到系统级，从硬件到软件，覆盖AI、机器人、储能、充电全栈技术能力
              </p>
            </div>

            <div className="bg-white p-8 rounded-2xl shadow-sm hover:shadow-lg transition-shadow">
              <div className="w-14 h-14 bg-green-100 rounded-xl flex items-center justify-center mb-6">
                <svg className="w-7 h-7 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-slate-900 mb-3">模块化极速交付</h3>
              <p className="text-slate-600">
                不同艇型、不同电量、不同应用，标准化模块组合，开发周期缩短70%
              </p>
            </div>

            <div className="bg-white p-8 rounded-2xl shadow-sm hover:shadow-lg transition-shadow">
              <div className="w-14 h-14 bg-purple-100 rounded-xl flex items-center justify-center mb-6">
                <svg className="w-7 h-7 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-slate-900 mb-3">生态资源对接</h3>
              <p className="text-slate-600">
                连接船厂、电池厂、电机厂、算法公司、政府用户，资源、资金、人才自然汇聚
              </p>
            </div>
          </div>

          {/* Stats Section */}
          <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            <div className="bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-2xl p-6">
              <div className="text-3xl md:text-4xl font-bold mb-2">18+</div>
              <div className="text-blue-100">年研发经验</div>
            </div>
            <div className="bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-2xl p-6">
              <div className="text-3xl md:text-4xl font-bold mb-2">8</div>
              <div className="text-blue-100">项发明专利</div>
            </div>
            <div className="bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-2xl p-6">
              <div className="text-3xl md:text-4xl font-bold mb-2">3200+</div>
              <div className="text-blue-100">产品量产经验</div>
            </div>
            <div className="bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-2xl p-6">
              <div className="text-3xl md:text-4xl font-bold mb-2">95%+</div>
              <div className="text-blue-100">AI识别率</div>
            </div>
          </div>
        </div>
      </section>

      {/* XUSV Team Image */}
      <section className="py-20 bg-slate-900">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-white mb-2">核心团队</h2>
            <p className="text-slate-400">来自中科院、国轩高科、欧科微等产业链知名企业</p>
          </div>
          <div className="max-w-4xl mx-auto">
            <img
              src="/xusv-team.jpg"
              alt="XUSV 核心团队"
              className="w-full rounded-2xl shadow-2xl"
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-slate-900 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">准备好开启您的XUSV之旅了吗？</h2>
          <p className="text-slate-400 mb-8 max-w-2xl mx-auto">
            无论是技术咨询、方案设计还是项目合作，我们都可以为您提供专业的支持
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/contact"
              className="px-8 py-4 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-lg font-semibold hover:shadow-lg hover:shadow-blue-500/30 transition-all"
            >
              立即联系
            </Link>
            <Link
              to="/solutions"
              className="px-8 py-4 bg-slate-800 rounded-lg font-semibold hover:bg-slate-700 transition-all"
            >
              浏览方案库
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
