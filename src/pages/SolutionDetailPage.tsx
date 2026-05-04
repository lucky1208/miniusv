import { useParams, Link } from 'react-router-dom';
import { solutions, Solution } from '../data/solutions';

export default function SolutionDetailPage() {
  const { id } = useParams();
  const solution = solutions.find((s) => s.id === id);

  // If solution not found, show error
  if (!solution) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-slate-900 mb-4">方案未找到</h1>
          <p className="text-slate-600 mb-6">抱歉，您查找的方案不存在。</p>
          <Link
            to="/solutions"
            className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-all"
          >
            返回方案库
          </Link>
        </div>
      </div>
    );
  }

  // Get cost summary based on solution
  const getCostBreakdown = (sol: Solution) => {
    if (sol.id === 'usv-mini') {
      return {
        battery: '0.8W',
        hull: '0.2W',
        sensors: '0.4W',
        total: '1.5W-2W',
        batteryConfig: '15S1P (100Ah/3.2V)',
        batteryVoltage: '48V',
        batteryEnergy: '15 kWh',
        batteryWeight: '~80 kg'
      };
    } else if (sol.id === 'usv-3m-patrol') {
      return {
        battery: '3W',
        hull: '0.4W',
        sensors: '2W',
        total: '5W-6W',
        batteryConfig: '63S1P (300Ah/3.2V)',
        batteryVoltage: '201.6V',
        batteryEnergy: '59.85 kWh',
        batteryWeight: '396.77 kg'
      };
    } else if (sol.id === 'usv-5m-work') {
      return {
        battery: '5W',
        hull: '0.8W',
        sensors: '4W',
        total: '10W-12W',
        batteryConfig: '108S1P (300Ah/3.2V)',
        batteryVoltage: '345.6V',
        batteryEnergy: '103.68 kWh',
        batteryWeight: '~650 kg'
      };
    } else if (sol.id === 'usv-8m-survey') {
      return {
        battery: '8W',
        hull: '1.5W',
        sensors: '8W',
        total: '18W-20W',
        batteryConfig: '126S2P (280Ah/3.2V)',
        batteryVoltage: '403.2V',
        batteryEnergy: '225.8 kWh',
        batteryWeight: '~1100 kg'
      };
    }
    return {
      battery: '3W',
      hull: '0.4W',
      sensors: '2W',
      total: '5W-6W',
      batteryConfig: '63S1P (300Ah/3.2V)',
      batteryVoltage: '201.6V',
      batteryEnergy: '59.85 kWh',
      batteryWeight: '396.77 kg'
    };
  };

  const costs = getCostBreakdown(solution);

  // Get description based on solution
  const getDescription = (sol: Solution) => {
    if (sol.id === 'usv-mini') return 'XUSV Mini是一款专为近海巡逻、环境监测、水域搜救等场景设计的小型化无人水面艇。采用模块化设计，支持快速部署和换电，极大提升作业效率。';
    if (sol.boatLength === 3) return '模块化、高机动性的海上"无人摩的"，适用于近海巡逻、目标拦截与防御作战场景';
    if (sol.boatLength === 5) return '100kWh大容量作业艇，支持长时间海上任务，适用于海洋监测、水质采样、海上施工辅助';
    if (sol.boatLength === 8) return '150kWh专业测量艇，支持多波束声呐等高精度测量设备，适用于海洋地形测绘、水文水质调查';
    return sol.description;
  };

  // Get hull info based on solution
  const getHullInfo = (sol: Solution) => {
    if (sol.id === 'usv-mini') return { weight: '~50 kg', type: 'FRP轻量化结构，适合快速部署' };
    if (sol.boatLength === 3) return { weight: '~200 kg', type: '玻璃钢复合材料（FRP）+ 泡沫夹芯结构（PVC/PET）' };
    if (sol.boatLength === 5) return { weight: '~350 kg', type: 'FRP+泡沫夹芯结构，5米双体船结构' };
    if (sol.boatLength === 8) return { weight: '~500 kg', type: '碳纤维+FRP混合结构，轻量化高强度船体' };
    return { weight: '~200 kg', type: '玻璃钢复合材料' };
  };

  const hullInfo = getHullInfo(solution);

  // Get media (images or video) based on solution
  const getSolutionMedia = (sol: Solution) => {
    if (sol.id === 'usv-3m-patrol') {
      return {
        mediaType: 'single-image',
        images: ['/3mgz.png'],
        labels: ['3米突击艇'],
        video: null
      };
    } else if (sol.id === 'usv-5m-work') {
      return {
        mediaType: 'video',
        images: [],
        labels: [],
        video: '/wuren.mp4'
      };
    } else if (sol.id === 'usv-8m-survey') {
      return {
        mediaType: 'single-image',
        images: ['/8m.png'],
        labels: ['8米测量艇'],
        video: null
      };
    }
    // Default for usv-mini
    return {
      mediaType: 'images',
      images: ['/xusv-fenjie.png', '/mini USV-new.png'],
      labels: ['爆炸分解图', '透视装机图'],
      video: null
    };
  };

  const solutionMedia = getSolutionMedia(solution);

  // Get tab title based on solution
  const getTabTitle = (sol: Solution) => {
    if (sol.id === 'usv-3m-patrol') return '预安装图';
    if (sol.id === 'usv-5m-work') return '样船改造成品';
    if (sol.id === 'usv-8m-survey') return '结构解析';
    return '结构解析';
  };

  // Get structure analysis content (for images replacement in red frame area)
  const getStructureAnalysisContent = (sol: Solution) => {
    if (sol.id === 'usv-3m-patrol') {
      return {
        showImage: true,
        imagePath: '/xusv-toushi.png',
        title: '',
        description: ''
      };
    }
    return null;
  };

  // Get speed unit based on solution
  const getSpeedUnit = (sol: Solution) => {
    return 'km/h';
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <section className="bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white py-16">
        <div className="container mx-auto px-4">
          <Link to="/solutions" className="text-blue-400 hover:text-blue-300 mb-4 inline-block">
            ← 返回方案库
          </Link>
          <h1 className="text-4xl font-bold mb-4">{solution.name}</h1>
          <p className="text-slate-300 max-w-2xl">{getDescription(solution)}</p>

          {/* Quick Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-8">
            <div className="bg-white/10 rounded-lg p-4">
              <div className="text-3xl font-bold">{solution.boatLength}m</div>
              <div className="text-sm text-slate-300">艇体长度</div>
            </div>
            <div className="bg-white/10 rounded-lg p-4">
              <div className="text-3xl font-bold">{solution.batteryCapacity}kWh</div>
              <div className="text-sm text-slate-300">电池容量</div>
            </div>
            <div className="bg-white/10 rounded-lg p-4">
              <div className="text-3xl font-bold">{solution.speed}{getSpeedUnit(solution)}</div>
              <div className="text-sm text-slate-300">最高航速</div>
            </div>
            <div className="bg-white/10 rounded-lg p-4">
              <div className="text-3xl font-bold">{solution.range}km</div>
              <div className="text-sm text-slate-300">续航里程</div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <section className="py-12">
        <div className="container mx-auto px-4">
          <div className="space-y-8">

            {/* Structure Analysis - Dynamic Media */}
            <div className="bg-white rounded-2xl p-8 shadow-sm">
              <h2 className="text-2xl font-bold text-slate-900 mb-6">{getTabTitle(solution)}</h2>

              {solutionMedia.mediaType === 'video' ? (
                // Video display for 5米作业艇
                <div>
                  <h3 className="text-lg font-semibold text-slate-800 mb-4">产品演示视频</h3>
                  <video
                    src={solutionMedia.video!}
                    controls
                    className="w-full rounded-xl shadow-lg"
                  >
                    您的浏览器不支持视频播放
                  </video>
                  <p className="text-sm text-slate-500 mt-3">展示{solution.boatLength}米{solution.boatType}实际作业场景</p>
                </div>
              ) : solutionMedia.mediaType === 'single-image' ? (
                // Single image display for 3米突击艇 and 8米测量艇
                <div>
                  {solution.id === 'usv-3m-patrol' ? (
                    // For 3米突击艇: Show 3mgz.png with exploded view removed
                    <div>
                      <h3 className="text-lg font-semibold text-slate-800 mb-4">透视装机图</h3>
                      <img
                        src="/3mgz.png"
                        alt="3米突击艇透视装机图"
                        className="w-full rounded-xl shadow-lg"
                      />
                      <p className="text-sm text-slate-500 mt-3">展示内部电气连接与元器件布局的实际装机效果</p>
                    </div>
                  ) : (
                    // For other single-image solutions (8米测量艇 etc.)
                    <div>
                      <h3 className="text-lg font-semibold text-slate-800 mb-4">{(solutionMedia as { mediaType: string; images: string[]; labels: string[]; video: null }).labels[0]}</h3>
                      <img
                        src={(solutionMedia as { mediaType: string; images: string[]; labels: string[]; video: null }).images[0]}
                        alt="产品图片"
                        className="w-full rounded-xl shadow-lg"
                      />
                      <p className="text-sm text-slate-500 mt-3">展示{solution.boatLength}米{solution.boatType}实物外观</p>
                    </div>
                  )}
                </div>
              ) : (
                // Dual image display for usv-mini
                <div className="grid md:grid-cols-2 gap-8">
                  <div>
                    <h3 className="text-lg font-semibold text-slate-800 mb-4">爆炸分解图</h3>
                    <img
                      src={solutionMedia.images[0]}
                      alt="爆炸分解图"
                      className="w-full rounded-xl shadow-lg"
                    />
                    <p className="text-sm text-slate-500 mt-3">展示{solution.boatLength}米{solution.boatType}各核心组件的分解结构</p>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-slate-800 mb-4">透视装机图</h3>
                    <img
                      src={solutionMedia.images[1]}
                      alt="透视装机图"
                      className="w-full rounded-xl shadow-lg"
                    />
                    <p className="text-sm text-slate-500 mt-3">展示内部电气连接与元器件布局的实际装机效果</p>
                  </div>
                </div>
              )}
            </div>

            {/* BOM Tables - Dynamic from solution data */}
            <div className="bg-white rounded-2xl p-8 shadow-sm">
              <h2 className="text-2xl font-bold text-slate-900 mb-6">核心硬件BOM清单与模块功能</h2>

              {/* Dynamically render BOM categories from solution data */}
              {solution.bom.map((category) => (
                <div key={category.category}>
                  <h3 className="text-xl font-semibold text-slate-800 mb-4 mt-8">{category.category}</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="bg-slate-100">
                          <th className="text-left py-3 px-4 text-sm font-medium text-slate-600">组件</th>
                          <th className="text-left py-3 px-4 text-sm font-medium text-slate-600">型号/参数</th>
                          <th className="text-center py-3 px-4 text-sm font-medium text-slate-600">数量</th>
                          <th className="text-left py-3 px-4 text-sm font-medium text-slate-600">功能描述</th>
                        </tr>
                      </thead>
                      <tbody>
                        {category.items.map((item, idx) => (
                          <tr key={idx} className="border-b border-slate-100">
                            <td className="py-3 px-4 font-medium text-slate-900">{item.name}</td>
                            <td className="py-3 px-4 text-slate-600">{item.model}</td>
                            <td className="py-3 px-4 text-center text-slate-600">{item.quantity} {item.unit}</td>
                            <td className="py-3 px-4 text-slate-600">{item.function}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ))}
            </div>

            {/* Engineering Calculations - Dynamic based on solution */}
            <div className="bg-white rounded-2xl p-8 shadow-sm">
              <h2 className="text-2xl font-bold text-slate-900 mb-6">工程计算</h2>

              {/* Battery Calculation */}
              <div className="bg-blue-50 rounded-xl p-6 mb-6">
                <h3 className="text-lg font-semibold text-slate-800 mb-4">电池包计算</h3>
                <p className="text-slate-600 mb-2">基于 300Ah / 3.2V / 950Wh 电芯：</p>
                <ul className="list-disc list-inside text-slate-600 space-y-1">
                  <li>配置：{costs.batteryConfig}</li>
                  <li>系统标称电压：{costs.batteryVoltage}</li>
                  <li>系统总能量：{costs.batteryEnergy}</li>
                  <li>电池净重：约{costs.batteryWeight}</li>
                  <li className="text-green-600 font-medium">价格：{costs.battery}</li>
                </ul>
              </div>

              {/* Hull Cost */}
              <div className="bg-green-50 rounded-xl p-6 mb-6">
                <h3 className="text-lg font-semibold text-slate-800 mb-4">壳体成本</h3>
                <p className="text-slate-600 mb-2">{hullInfo.type}：</p>
                <ul className="list-disc list-inside text-slate-600 space-y-1">
                  <li>重量约{hullInfo.weight}</li>
                  <li>整体船体：{costs.hull}</li>
                </ul>
              </div>

              {/* Sensor Cost - Based on solution BOM */}
              <div className="bg-purple-50 rounded-xl p-6 mb-6">
                <h3 className="text-lg font-semibold text-slate-800 mb-4">通信与传感器模块</h3>
                <p className="text-slate-600 mb-2">根据{solution.boatLength}米{solution.boatType}配置：</p>
                <div className="grid md:grid-cols-2 gap-4">
                  {solution.bom
                    .find(c => c.category === '通信与传感器')?.items.map((item, idx) => (
                      <div key={idx} className="text-slate-600">
                        {item.name}：RMB {item.price.toLocaleString()}
                      </div>
                    ))}
                </div>
              </div>

              {/* Main Control System */}
              <div className="bg-orange-50 rounded-xl p-6 mb-6">
                <h3 className="text-lg font-semibold text-slate-800 mb-4">主控系统</h3>
                <div className="grid md:grid-cols-2 gap-4">
                  {solution.bom
                    .find(c => c.category === 'AI主控与计算')?.items.map((item, idx) => (
                      <div key={idx} className="text-slate-600">
                        {item.name}：RMB {item.price.toLocaleString()}
                      </div>
                    ))}
                </div>
              </div>

              {/* Power Module */}
              <div className="bg-cyan-50 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-slate-800 mb-4">动力与能源系统</h3>
                <div className="grid md:grid-cols-2 gap-4">
                  {solution.bom
                    .find(c => c.category === '动力与能源系统')?.items.map((item, idx) => (
                      <div key={idx} className="text-slate-600">
                        {item.name}：RMB {item.price.toLocaleString()}
                      </div>
                    ))}
                </div>
              </div>
            </div>

            {/* Cost Summary */}
            <div className="bg-gradient-to-r from-blue-600 to-cyan-600 rounded-2xl p-8 text-white">
              <h2 className="text-2xl font-bold mb-6">成本估算总计</h2>
              <div className="grid md:grid-cols-3 gap-6 mb-6">
                <div className="bg-white/20 rounded-xl p-4 text-center">
                  <div className="text-3xl font-bold">{costs.battery}</div>
                  <div className="text-sm text-blue-100">高压电池包</div>
                </div>
                <div className="bg-white/20 rounded-xl p-4 text-center">
                  <div className="text-3xl font-bold">{costs.hull}</div>
                  <div className="text-sm text-blue-100">船体结构</div>
                </div>
                <div className="bg-white/20 rounded-xl p-4 text-center">
                  <div className="text-3xl font-bold">{costs.sensors}</div>
                  <div className="text-sm text-blue-100">感知与通信</div>
                </div>
              </div>
              <div className="text-center">
                <p className="text-lg text-blue-100 mb-2">核心BOM总成本（不含改装服务）</p>
                <p className="text-5xl font-bold">{costs.total}</p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="bg-white rounded-2xl p-8 shadow-sm">
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  to="/contact"
                  className="px-8 py-4 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-lg font-semibold text-center hover:shadow-lg transition-all"
                >
                  获取完整方案
                </Link>
                <a
                  href="/src/assets/xusv-design-v6.pdf"
                  download="XUSV模块化设计方案V6.0.pdf"
                  className="px-8 py-4 bg-green-600 text-white rounded-lg font-semibold text-center hover:bg-green-700 transition-all"
                >
                  下载完整技术方案PDF
                </a>
              </div>
            </div>

          </div>
        </div>
      </section>
    </div>
  );
}
