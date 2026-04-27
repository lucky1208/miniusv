import { Link } from 'react-router-dom';
import { solutions, boatTypes, applications } from '../data/solutions';

export default function SolutionsPage() {
  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <section className="bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white py-16">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl font-bold mb-4">USV油改电方案库</h1>
          <p className="text-slate-300 max-w-2xl">
            覆盖3米到10米主流艇型，提供从硬件选型到成本估算的完整解决方案。
            不同电量、不同应用、不同场景，精准匹配您的需求。
          </p>
        </div>
      </section>

      {/* Quick Stats */}
      <section className="py-8 bg-white border-b">
        <div className="container mx-auto px-4">
          <div className="flex flex-wrap gap-6 justify-center">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <div className="text-2xl font-bold text-slate-900">{solutions.length}</div>
                <div className="text-sm text-slate-500">精选方案</div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div>
                <div className="text-2xl font-bold text-slate-900">60kWh-225kWh</div>
                <div className="text-sm text-slate-500">电量范围</div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <div className="text-2xl font-bold text-slate-900">8-45万</div>
                <div className="text-sm text-slate-500">价格区间</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Filter Section */}
      <section className="py-8 bg-white">
        <div className="container mx-auto px-4">
          <div className="flex flex-wrap gap-8">
            <div>
              <h3 className="text-sm font-medium text-slate-700 mb-3">按艇型筛选</h3>
              <div className="flex flex-wrap gap-2">
                <button className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg">
                  全部
                </button>
                {boatTypes.map((type) => (
                  <button
                    key={type.value}
                    className="px-4 py-2 bg-slate-100 text-slate-700 text-sm rounded-lg hover:bg-slate-200 transition-colors"
                  >
                    {type.label}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <h3 className="text-sm font-medium text-slate-700 mb-3">按应用场景</h3>
              <div className="flex flex-wrap gap-2">
                <button className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg">
                  全部
                </button>
                {applications.map((app) => (
                  <button
                    key={app.value}
                    className="px-4 py-2 bg-slate-100 text-slate-700 text-sm rounded-lg hover:bg-slate-200 transition-colors"
                  >
                    {app.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Solutions Grid */}
      <section className="py-12">
        <div className="container mx-auto px-4">
          <div className="space-y-8">
            {solutions.map((solution, index) => (
              <div
                key={solution.id}
                className="bg-white rounded-2xl shadow-sm hover:shadow-lg transition-all overflow-hidden"
              >
                <div className="grid md:grid-cols-5">
                  {/* Visual */}
                  <div className="md:col-span-2 bg-gradient-to-br from-blue-600 to-cyan-600 p-8 flex items-center justify-center">
                    <div className="text-center text-white">
                      <div className="text-6xl font-bold mb-2">{solution.boatLength}</div>
                      <div className="text-lg opacity-80">米级{index === 0 ? '突击' : index === 1 ? '作业' : '测量'}艇</div>
                      <div className="mt-4 text-sm opacity-70">
                        {solution.application}
                      </div>
                    </div>
                  </div>

                  {/* Content */}
                  <div className="md:col-span-3 p-8">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-2xl font-bold text-slate-900 mb-2">
                          {solution.name}
                        </h3>
                        <p className="text-slate-600">{solution.description}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-blue-600">{solution.price}</div>
                        <div className="text-sm text-slate-500">预估成本</div>
                      </div>
                    </div>

                    {/* Key Specs */}
                    <div className="grid grid-cols-4 gap-4 mb-6">
                      <div className="bg-slate-50 rounded-lg p-3 text-center">
                        <div className="text-xl font-bold text-slate-900">{solution.batteryCapacity}kWh</div>
                        <div className="text-xs text-slate-500">电池容量</div>
                      </div>
                      <div className="bg-slate-50 rounded-lg p-3 text-center">
                        <div className="text-xl font-bold text-slate-900">{solution.speed}节</div>
                        <div className="text-xs text-slate-500">最高航速</div>
                      </div>
                      <div className="bg-slate-50 rounded-lg p-3 text-center">
                        <div className="text-xl font-bold text-slate-900">{solution.range}km</div>
                        <div className="text-xs text-slate-500">续航里程</div>
                      </div>
                      <div className="bg-slate-50 rounded-lg p-3 text-center">
                        <div className="text-xl font-bold text-slate-900">{solution.voltage}V</div>
                        <div className="text-xs text-slate-500">系统电压</div>
                      </div>
                    </div>

                    {/* Features */}
                    <div className="mb-6">
                      <h4 className="text-sm font-medium text-slate-700 mb-2">核心特性</h4>
                      <div className="flex flex-wrap gap-2">
                        {solution.features.map((feature, idx) => (
                          <span
                            key={idx}
                            className="px-3 py-1 bg-blue-50 text-blue-700 text-xs rounded-full"
                          >
                            {feature}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* BOM Summary */}
                    <div className="mb-6">
                      <h4 className="text-sm font-medium text-slate-700 mb-2">BOM清单</h4>
                      <div className="space-y-2">
                        {solution.bom.map((category) => (
                          <div key={category.category} className="flex justify-between text-sm">
                            <span className="text-slate-600">{category.category}</span>
                            <span className="text-slate-900 font-medium">
                              {category.items.length}项
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-4">
                      <Link
                        to={`/solutions/${solution.id}`}
                        className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-lg font-medium text-center hover:shadow-lg transition-all"
                      >
                        查看完整方案
                      </Link>
                      <button className="px-6 py-3 bg-slate-100 text-slate-700 rounded-lg font-medium hover:bg-slate-200 transition-all">
                        下载BOM清单
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 bg-slate-900 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-2xl font-bold mb-4">没有找到合适的方案？</h2>
          <p className="text-slate-400 mb-6">
            我们提供定制化方案设计服务，根据您的具体需求量身打造
          </p>
          <Link
            to="/contact"
            className="inline-block px-8 py-4 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-lg font-semibold hover:shadow-lg transition-all"
          >
            咨询定制方案
          </Link>
        </div>
      </section>
    </div>
  );
}
