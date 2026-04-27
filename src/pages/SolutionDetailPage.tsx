import { useParams, Link } from 'react-router-dom';

export default function SolutionDetailPage() {
  const { id } = useParams();

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <section className="bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white py-16">
        <div className="container mx-auto px-4">
          <Link to="/solutions" className="text-blue-400 hover:text-blue-300 mb-4 inline-block">
            ← 返回方案库
          </Link>
          <h1 className="text-4xl font-bold mb-4">XUSV Mini 海上"无人摩的"</h1>
          <p className="text-slate-300 max-w-2xl">模块化、高机动性的海上"无人摩的"，适用于近海巡逻、目标拦截与防御作战场景</p>

          {/* Quick Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-8">
            <div className="bg-white/10 rounded-lg p-4">
              <div className="text-3xl font-bold">1.5-2m</div>
              <div className="text-sm text-slate-300">艇体长度</div>
            </div>
            <div className="bg-white/10 rounded-lg p-4">
              <div className="text-3xl font-bold">60kWh</div>
              <div className="text-sm text-slate-300">电池容量</div>
            </div>
            <div className="bg-white/10 rounded-lg p-4">
              <div className="text-3xl font-bold">20节</div>
              <div className="text-sm text-slate-300">最高航速</div>
            </div>
            <div className="bg-white/10 rounded-lg p-4">
              <div className="text-3xl font-bold">100km</div>
              <div className="text-sm text-slate-300">续航里程</div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <section className="py-12">
        <div className="container mx-auto px-4">
          <div className="space-y-8">

            {/* Structure Analysis */}
            <div className="bg-white rounded-2xl p-8 shadow-sm">
              <h2 className="text-2xl font-bold text-slate-900 mb-6">结构解析</h2>
              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <h3 className="text-lg font-semibold text-slate-800 mb-4">爆炸分解图</h3>
                  <img
                    src="/xusv-fenjie.png"
                    alt="爆炸分解图"
                    className="w-full rounded-xl shadow-lg"
                  />
                  <p className="text-sm text-slate-500 mt-3">展示无人艇各核心组件的分解结构，便于理解系统组成</p>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-slate-800 mb-4">透视装机图</h3>
                  <img
                    src="/xusv-toushi.png"
                    alt="透视装机图"
                    className="w-full rounded-xl shadow-lg"
                  />
                  <p className="text-sm text-slate-500 mt-3">展示内部电气连接与元器件布局的实际装机效果</p>
                </div>
              </div>
            </div>

            {/* AI主控与计算模块 */}
            <div className="bg-white rounded-2xl p-8 shadow-sm">
              <h2 className="text-2xl font-bold text-slate-900 mb-6">核心硬件BOM清单与模块功能</h2>

              <h3 className="text-xl font-semibold text-slate-800 mb-4 mt-8">AI主控与计算模块</h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="bg-slate-100">
                      <th className="text-left py-3 px-4 text-sm font-medium text-slate-600">组件</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-slate-600">推荐型号</th>
                      <th className="text-center py-3 px-4 text-sm font-medium text-slate-600">数量</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-slate-600">功能描述</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b border-slate-100">
                      <td className="py-3 px-4 font-medium text-slate-900">AI主控</td>
                      <td className="py-3 px-4 text-slate-600">Jetson Orin NX Edge AI模块</td>
                      <td className="py-3 px-4 text-center text-slate-600">1块</td>
                      <td className="py-3 px-4 text-slate-600">核心算法运行平台，负责视觉与雷达融合感知</td>
                    </tr>
                    <tr className="border-b border-slate-100">
                      <td className="py-3 px-4 font-medium text-slate-900">工控板</td>
                      <td className="py-3 px-4 text-slate-600">工业载板</td>
                      <td className="py-3 px-4 text-center text-slate-600">1块</td>
                      <td className="py-3 px-4 text-slate-600">负责底层控制（CAN, PCIe, GbE）</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* 动力与能源系统 */}
              <h3 className="text-xl font-semibold text-slate-800 mb-4 mt-8">动力与能源系统（电芯减半方案）</h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="bg-slate-100">
                      <th className="text-left py-3 px-4 text-sm font-medium text-slate-600">组件</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-slate-600">参数/型号</th>
                      <th className="text-center py-3 px-4 text-sm font-medium text-slate-600">数量</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-slate-600">功能描述</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b border-slate-100">
                      <td className="py-3 px-4 font-medium text-slate-900">高压电池包</td>
                      <td className="py-3 px-4 text-slate-600">63S1P (300Ah/3.2V)</td>
                      <td className="py-3 px-4 text-center text-slate-600">1个</td>
                      <td className="py-3 px-4 text-slate-600">系统电压约200V，总能量约60kWh，大幅减轻重量</td>
                    </tr>
                    <tr className="border-b border-slate-100">
                      <td className="py-3 px-4 font-medium text-slate-900">BMS</td>
                      <td className="py-3 px-4 text-slate-600">工业级电池管理系统</td>
                      <td className="py-3 px-4 text-center text-slate-600">1</td>
                      <td className="py-3 px-4 text-slate-600">实时单体监控与均衡，确保电池安全</td>
                    </tr>
                    <tr className="border-b border-slate-100">
                      <td className="py-3 px-4 font-medium text-slate-900">DC/DC</td>
                      <td className="py-3 px-4 text-slate-600">Vicor / Delta</td>
                      <td className="py-3 px-4 text-center text-slate-600">2</td>
                      <td className="py-3 px-4 text-slate-600">高效率电压转换，为控制系统供电</td>
                    </tr>
                    <tr className="border-b border-slate-100">
                      <td className="py-3 px-4 font-medium text-slate-900">ESC控制器</td>
                      <td className="py-3 px-4 text-slate-600">水冷无刷电机控制器</td>
                      <td className="py-3 px-4 text-center text-slate-600">2</td>
                      <td className="py-3 px-4 text-slate-600">精确控制大功率电机转速与扭矩</td>
                    </tr>
                    <tr className="border-b border-slate-100">
                      <td className="py-3 px-4 font-medium text-slate-900">驱动电机</td>
                      <td className="py-3 px-4 text-slate-600">25kW BLDC永磁同步电机</td>
                      <td className="py-3 px-4 text-center text-slate-600">2</td>
                      <td className="py-3 px-4 text-slate-600">双发推进，单发25kW，总功率50kW</td>
                    </tr>
                    <tr className="border-b border-slate-100">
                      <td className="py-3 px-4 font-medium text-slate-900">喷水推进</td>
                      <td className="py-3 px-4 text-slate-600">Marine Jet喷水泵</td>
                      <td className="py-3 px-4 text-center text-slate-600">2</td>
                      <td className="py-3 px-4 text-slate-600">浅水适应，高机动转向</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* 通信与传感器模块 */}
              <h3 className="text-xl font-semibold text-slate-800 mb-4 mt-8">通信与传感器模块</h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="bg-slate-100">
                      <th className="text-left py-3 px-4 text-sm font-medium text-slate-600">类别</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-slate-600">推荐设备</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-slate-600">功能描述</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b border-slate-100">
                      <td className="py-3 px-4 font-medium text-slate-900">卫星通信</td>
                      <td className="py-3 px-4 text-slate-600">铱星（海外）/天通模块（内海）</td>
                      <td className="py-3 px-4 text-slate-600">远海超视距应急指挥链路</td>
                    </tr>
                    <tr className="border-b border-slate-100">
                      <td className="py-3 px-4 font-medium text-slate-900">4G/5G</td>
                      <td className="py-3 px-4 text-slate-600">工业路由器</td>
                      <td className="py-3 px-4 text-slate-600">近岸高带宽图像与数据传输</td>
                    </tr>
                    <tr className="border-b border-slate-100">
                      <td className="py-3 px-4 font-medium text-slate-900">Mesh</td>
                      <td className="py-3 px-4 text-slate-600">无线自组网模块</td>
                      <td className="py-3 px-4 text-slate-600">多艇协同及复杂电磁环境下的稳健通信</td>
                    </tr>
                    <tr className="border-b border-slate-100">
                      <td className="py-3 px-4 font-medium text-slate-900">GPS/RTK</td>
                      <td className="py-3 px-4 text-slate-600">双模定位模块</td>
                      <td className="py-3 px-4 text-slate-600">厘米级高精度定位</td>
                    </tr>
                    <tr className="border-b border-slate-100">
                      <td className="py-3 px-4 font-medium text-slate-900">INS</td>
                      <td className="py-3 px-4 text-slate-600">MEMS惯导</td>
                      <td className="py-3 px-4 text-slate-600">姿态感知，在GNSS失效时提供短时推算</td>
                    </tr>
                    <tr className="border-b border-slate-100">
                      <td className="py-3 px-4 font-medium text-slate-900">毫米波雷达</td>
                      <td className="py-3 px-4 text-slate-600">77GHz远距雷达</td>
                      <td className="py-3 px-4 text-slate-600">动态目标识别与全天候避障</td>
                    </tr>
                    <tr className="border-b border-slate-100">
                      <td className="py-3 px-4 font-medium text-slate-900">激光雷达</td>
                      <td className="py-3 px-4 text-slate-600">360°固态激光雷达</td>
                      <td className="py-3 px-4 text-slate-600">高精度近程环境建模与避障</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* 工程计算 */}
            <div className="bg-white rounded-2xl p-8 shadow-sm">
              <h2 className="text-2xl font-bold text-slate-900 mb-6">工程计算</h2>

              <div className="bg-blue-50 rounded-xl p-6 mb-6">
                <h3 className="text-lg font-semibold text-slate-800 mb-4">电池包计算</h3>
                <p className="text-slate-600 mb-2">基于 300Ah / 3.2V / 950Wh 电芯：</p>
                <ul className="list-disc list-inside text-slate-600 space-y-1">
                  <li>配置：63S1P</li>
                  <li>系统标称电压：201.6V</li>
                  <li>系统总能量：59.85 kWh</li>
                  <li>电池净重：约396.77 kg</li>
                  <li className="text-green-600 font-medium">价格（按照0.5元/Wh）：约3万元</li>
                </ul>
              </div>

              <div className="bg-green-50 rounded-xl p-6 mb-6">
                <h3 className="text-lg font-semibold text-slate-800 mb-4">壳体成本</h3>
                <p className="text-slate-600 mb-2">玻璃钢复合材料（FRP）+ 泡沫夹芯结构（PVC/PET）：</p>
                <ul className="list-disc list-inside text-slate-600 space-y-1">
                  <li>重量约200 kg</li>
                  <li>整体船体：RMB 3,000 - 5,000</li>
                </ul>
              </div>

              <div className="bg-purple-50 rounded-xl p-6 mb-6">
                <h3 className="text-lg font-semibold text-slate-800 mb-4">通信与传感器模块</h3>
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="text-slate-600">卫星模组：RMB 3,000</div>
                  <div className="text-slate-600">激光雷达：RMB 6,000</div>
                  <div className="text-slate-600">GPS/RTK：RMB 1,000</div>
                  <div className="text-slate-600">路由器：RMB 800</div>
                </div>
              </div>

              <div className="bg-orange-50 rounded-xl p-6 mb-6">
                <h3 className="text-lg font-semibold text-slate-800 mb-4">主控系统</h3>
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="text-slate-600">左脑（AI主控）：RMB 3,000</div>
                  <div className="text-slate-600">右脑（工控板）：RMB 1,000</div>
                </div>
              </div>

              <div className="bg-cyan-50 rounded-xl p-6 mb-6">
                <h3 className="text-lg font-semibold text-slate-800 mb-4">电源模块</h3>
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="text-slate-600">转48V DC/DC：RMB 1,000</div>
                  <div className="text-slate-600">转12V DC/DC：RMB 200</div>
                </div>
              </div>

              <div className="bg-red-50 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-slate-800 mb-4">电机及推进器</h3>
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="text-slate-600">2个电机：RMB 2,500</div>
                  <div className="text-slate-600">2个电机控制器：RMB 1,600</div>
                  <div className="text-slate-600">喷水推进器：RMB 2,000</div>
                  <div className="text-slate-600">传动系统：RMB 400</div>
                </div>
              </div>
            </div>

            {/* Cost Summary */}
            <div className="bg-gradient-to-r from-blue-600 to-cyan-600 rounded-2xl p-8 text-white">
              <h2 className="text-2xl font-bold mb-6">成本估算总计</h2>
              <div className="grid md:grid-cols-3 gap-6 mb-6">
                <div className="bg-white/20 rounded-xl p-4 text-center">
                  <div className="text-3xl font-bold">约3万</div>
                  <div className="text-sm text-blue-100">高压电池包</div>
                </div>
                <div className="bg-white/20 rounded-xl p-4 text-center">
                  <div className="text-3xl font-bold">约3-5千</div>
                  <div className="text-sm text-blue-100">玻璃钢壳体</div>
                </div>
                <div className="bg-white/20 rounded-xl p-4 text-center">
                  <div className="text-3xl font-bold">约2万</div>
                  <div className="text-sm text-blue-100">通信与传感器</div>
                </div>
              </div>
              <div className="text-center">
                <p className="text-lg text-blue-100 mb-2">核心BOM总成本（不含壳体）</p>
                <p className="text-5xl font-bold">约5-6万</p>
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
