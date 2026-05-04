import { Link } from 'react-router-dom';

export default function AboutPage() {
  const skills = [
    { category: '硬件设计', items: ['模数电路设计', 'PCB设计', 'FPGA开发', 'SI/PI仿真'] },
    { category: '软件架构', items: ['C/C++/Python/Java', 'ROS机器人系统', '嵌入式开发', '云平台架构'] },
    { category: '项目管理', items: ['产品生命周期管理', '跨部门协调', '供应商管理', '量产导入'] },
    { category: 'AI技术', items: ['深度学习算法', '传感器融合', '运动控制', '自动驾驶'] }
  ];

  const achievements = [
    { number: '20+', label: '年研发经验' },
    { number: '8', label: '项发明专利' },
    { number: '3200+', label: '产品量产经验' },
    { number: '30亿', label: '销售额贡献' }
  ];

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Hero - Company Introduction */}
      <section className="bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white py-20">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-4xl font-bold mb-6">关于我们</h1>
            <div className="bg-white/10 rounded-2xl p-8 backdrop-blur">
              <h2 className="text-2xl font-bold mb-4 text-blue-300">X.USV 简介</h2>
              <p className="text-slate-300 leading-relaxed text-left">
                X.USV 是国内领先的一站式电动无人艇解决方案提供商，聚焦商用与民用多元水域场景，提供定制化的电动无人艇产品升级方案。
              </p>
              <p className="text-slate-300 leading-relaxed text-left mt-4">
                公司业务覆盖硬件、软件及系统方案三大板块：硬件方面，自主开发低成本卫星模块、定制化电池包及多功能充放电系统；软件方面，打造低成本一体化智能监控平台（涵盖管理调度、设备监控、数据分析）及手机端监控软件；方案层面，可针对具体船型提供完整BOM级别的油改电方案。
              </p>
              <p className="text-slate-300 leading-relaxed text-left mt-4">
                核心团队来自中科院、国轩高科、欧科微等产业链知名企业，并与上述机构保持深度资源合作。
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-slate-900 mb-12 text-center">核心团队</h2>
          <div className="grid md:grid-cols-2 gap-12 max-w-5xl mx-auto">

            {/* 卢继雄 - With Photo */}
            <div className="bg-gradient-to-br from-slate-50 to-slate-100 rounded-2xl p-8">
              <div className="flex items-center gap-6 mb-6">
                <img
                  src="/lu.jpg"
                  alt="卢继雄"
                  className="w-20 h-20 rounded-full object-cover border-2 border-blue-500"
                />
                <div>
                  <h3 className="text-2xl font-bold text-slate-900">卢继雄</h3>
                  <p className="text-blue-600">创始人 / CEO</p>
                </div>
              </div>
              <p className="text-slate-600 leading-relaxed">
                十几年系统产品软硬件研发和项目管理经验，深谙AI、机器人、储能充电、云计算等领域产品，精通软硬件，从架构设计到批量量产的全生命周期流程。拥有8项发明专利，曾主导多个亿元级项目落地。
              </p>
            </div>

            {/* 谢英杰 - New */}
            <div className="bg-gradient-to-br from-slate-50 to-slate-100 rounded-2xl p-8">
              <div className="flex items-center gap-6 mb-6">
                <img
                  src="/xusv-image.png"
                  alt="谢英杰"
                  className="w-20 h-20 rounded-full object-cover border-2 border-blue-500"
                />
                <div>
                  <h3 className="text-2xl font-bold text-slate-900">谢英杰</h3>
                  <p className="text-blue-600">联合创始人</p>
                </div>
              </div>
              <p className="text-slate-600 text-sm">中科院背景，具备扎实的科研能力和学术资源，专注于AI算法和商业运营，负责技术落地与市场拓展，曾主导完成亿元级别ToC产品市场销售ToB端产品商业化</p>
            </div>
          </div>
        </div>
      </section>

      {/* Achievements */}
      <section className="py-12 bg-blue-600">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {achievements.map((item, idx) => (
              <div key={idx} className="text-center text-white">
                <div className="text-4xl md:text-5xl font-bold mb-2">{item.number}</div>
                <div className="text-blue-100">{item.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Skills */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-slate-900 mb-12 text-center">技术能力</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-5xl mx-auto">
            {skills.map((skill, idx) => (
              <div key={idx} className="bg-slate-50 rounded-2xl p-6">
                <h3 className="text-lg font-bold text-slate-900 mb-4">{skill.category}</h3>
                <ul className="space-y-2">
                  {skill.items.map((item, i) => (
                    <li key={i} className="flex items-center gap-2 text-slate-600">
                      <svg className="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Patents */}
      <section className="py-16 bg-slate-50">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-slate-900 mb-12 text-center">发明专利</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 max-w-4xl mx-auto">
            {[
              'CN201811281084.5',
              'CN201811281077.5',
              'CN201830610352.8',
              'CN201610781737.0',
              'CN201610737773.7',
              'CN201630180557.8',
              'CN201310133895.1',
              'CN201310134690.5'
            ].map((patent, idx) => (
              <div key={idx} className="bg-white rounded-lg p-4 text-center shadow-sm">
                <div className="text-sm font-mono text-slate-700">{patent}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Funding Section */}
      <section className="py-16 bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold mb-12 text-center">融资计划</h2>
          <div className="max-w-5xl mx-auto">
            {/* Funding Overview */}
            <div className="bg-white/10 backdrop-blur rounded-2xl p-8 mb-12">
              <div className="grid md:grid-cols-3 gap-8 text-center">
                <div>
                  <div className="text-4xl md:text-5xl font-bold text-cyan-400 mb-2">200万</div>
                  <div className="text-blue-200">融资金额</div>
                </div>
                <div>
                  <div className="text-4xl md:text-5xl font-bold text-cyan-400 mb-2">15%</div>
                  <div className="text-blue-200">出让股权</div>
                </div>
                <div>
                  <div className="text-4xl md:text-5xl font-bold text-cyan-400 mb-2">1,333万</div>
                  <div className="text-blue-200">投后估值</div>
                </div>
              </div>
            </div>

            {/* Investment Highlights */}
            <div className="mb-12">
              <h3 className="text-2xl font-bold mb-6 text-center">融资亮点</h3>
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-white/10 rounded-xl p-6">
                  <div className="text-cyan-400 font-bold mb-2">轻资产模式</div>
                  <div className="text-slate-300 text-sm">快速验证万亿级市场蓝海</div>
                </div>
                <div className="bg-white/10 rounded-xl p-6">
                  <div className="text-cyan-400 font-bold mb-2">技术壁垒高</div>
                  <div className="text-slate-300 text-sm">四大核心技术构建护城河</div>
                </div>
                <div className="bg-white/10 rounded-xl p-6">
                  <div className="text-cyan-400 font-bold mb-2">团队背景强</div>
                  <div className="text-slate-300 text-sm">10年+平均产业经验</div>
                </div>
                <div className="bg-white/10 rounded-xl p-6">
                  <div className="text-cyan-400 font-bold mb-2">商业化路径清晰</div>
                  <div className="text-slate-300 text-sm">硬件+载荷+服务+授权四维盈利</div>
                </div>
              </div>
            </div>

            {/* Fund Usage */}
            <div className="mb-12">
              <h3 className="text-2xl font-bold mb-6 text-center">资金用途</h3>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="bg-gradient-to-r from-blue-600 to-cyan-600 rounded-xl p-5">
                  <div className="text-2xl font-bold mb-1">60万</div>
                  <div className="text-blue-100">团队薪酬</div>
                  <div className="text-sm text-blue-200 mt-1">组建6-8人核心团队</div>
                </div>
                <div className="bg-gradient-to-r from-blue-600 to-cyan-600 rounded-xl p-5">
                  <div className="text-2xl font-bold mb-1">50万</div>
                  <div className="text-blue-100">样机开发</div>
                  <div className="text-sm text-blue-200 mt-1">设计、材料、外协加工</div>
                </div>
                <div className="bg-gradient-to-r from-blue-600 to-cyan-600 rounded-xl p-5">
                  <div className="text-2xl font-bold mb-1">30万</div>
                  <div className="text-blue-100">实测与认证</div>
                  <div className="text-sm text-blue-200 mt-1">海上实测、船级社认证</div>
                </div>
                <div className="bg-gradient-to-r from-blue-600 to-cyan-600 rounded-xl p-5">
                  <div className="text-2xl font-bold mb-1">30万</div>
                  <div className="text-blue-100">市场推广</div>
                  <div className="text-sm text-blue-200 mt-1">白皮书、展会、数字孪生平台</div>
                </div>
                <div className="bg-gradient-to-r from-blue-600 to-cyan-600 rounded-xl p-5">
                  <div className="text-2xl font-bold mb-1">15万</div>
                  <div className="text-blue-100">社区与运营</div>
                  <div className="text-sm text-blue-200 mt-1">开源社区建设</div>
                </div>
                <div className="bg-gradient-to-r from-blue-600 to-cyan-600 rounded-xl p-5">
                  <div className="text-2xl font-bold mb-1">15万</div>
                  <div className="text-blue-100">法务财务</div>
                  <div className="text-sm text-blue-200 mt-1">不可预见费</div>
                </div>
              </div>
            </div>

            {/* Market Opportunity */}
            <div className="bg-white/10 backdrop-blur rounded-2xl p-8">
              <h3 className="text-2xl font-bold mb-6 text-center">市场机遇</h3>
              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <div className="text-3xl font-bold text-cyan-400 mb-2">18.3亿美元</div>
                  <div className="text-blue-200 mb-4">2026年全球USV市场规模</div>
                  <div className="text-3xl font-bold text-cyan-400 mb-2">68.7亿美元</div>
                  <div className="text-blue-200">2035年预测市场规模</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-cyan-400 mb-2">15.2%</div>
                  <div className="text-blue-200 mb-4">年复合增长率(CAGR)</div>
                  <div className="text-3xl font-bold text-cyan-400 mb-2">3,500+</div>
                  <div className="text-blue-200">全球已部署作业单位</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-cyan-600 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-6">与我们合作</h2>
          <p className="text-xl text-blue-100 max-w-3xl mx-auto mb-8">
            无论是技术咨询、方案设计还是项目合作，我们都可以为您提供专业的支持
          </p>
          <Link
            to="/contact"
            className="inline-block px-8 py-4 bg-white text-blue-600 rounded-lg font-semibold hover:bg-blue-50 transition-all"
          >
            立即联系
          </Link>
        </div>
      </section>
    </div>
  );
}
