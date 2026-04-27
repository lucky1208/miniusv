// 方案库数据 - 基于卢继雄V6.0设计方案
export interface Solution {
  id: string;
  name: string;
  boatType: string;
  boatLength: number;
  batteryCapacity: number;
  voltage: number;
  speed: number;
  range: number;
  application: string;
  price: string;
  features: string[];
  bom: BOMItem[];
  description: string;
}

export interface BOMItem {
  category: string;
  items: {
    name: string;
    model: string;
    quantity: number;
    unit: string;
    price: number;
    function: string;
  }[];
}

export const solutions: Solution[] = [
  {
    id: 'usv-3m-patrol',
    name: '3米突击艇智能USV方案',
    boatType: '突击艇/冲锋艇',
    boatLength: 3,
    batteryCapacity: 60,
    voltage: 200,
    speed: 30,
    range: 50,
    application: '近海巡逻/目标拦截',
    price: '8-12万',
    features: [
      '双喷水推进，高机动转向',
      'AI智能感知（激光+毫米波+光电）',
      'L4级自主航行',
      '多模卫星通信（铱星/海事/星链）',
      'RTK厘米级定位',
      '支持蜂群协同'
    ],
    description: '针对3米级突击艇设计的模块化油改电方案，采用60kWh电池包，航速30节，续航50公里。适用于近海巡逻、目标拦截等军事/准军事场景。',
    bom: [
      {
        category: 'AI主控与计算',
        items: [
          { name: 'AI主控', model: 'Jetson Orin NX Edge AI模块', quantity: 1, unit: '套', price: 3000, function: '核心算法运行平台，视觉与雷达融合感知' },
          { name: '工控板', model: '工业载板', quantity: 1, unit: '块', price: 1000, function: '负责底层控制（CAN, PCIe, GbE）' }
        ]
      },
      {
        category: '动力与能源系统',
        items: [
          { name: '高压电池包', model: '63S1P (300Ah/3.2V)', quantity: 1, unit: '套', price: 30000, function: '系统电压201.6V，总能量59.85kWh' },
          { name: 'BMS', model: '工业级电池管理系统', quantity: 1, unit: '套', price: 2000, function: '实时单体监控与均衡' },
          { name: 'DC/DC转换器', model: 'Vicor / Delta', quantity: 2, unit: '个', price: 1200, function: '高效率电压转换' },
          { name: 'ESC控制器', model: '水冷无刷电机控制器', quantity: 2, unit: '个', price: 1600, function: '精确控制电机转速与扭矩' },
          { name: '驱动电机', model: '25kW BLDC 永磁同步电机', quantity: 2, unit: '个', price: 2500, function: '双发推进，单发25kW' },
          { name: '喷水推进器', model: 'Marine Jet 喷水泵', quantity: 2, unit: '套', price: 2000, function: '浅水适应，高机动转向' }
        ]
      },
      {
        category: '通信与传感器',
        items: [
          { name: '卫星通信模块', model: '铱星/天通多模', quantity: 1, unit: '套', price: 3000, function: '远海超视距应急指挥链路' },
          { name: '4G/5G路由器', model: '工业路由器', quantity: 1, unit: '个', price: 800, function: '近岸高带宽图像与数据传输' },
          { name: 'GPS/RTK定位', model: '双模定位模块', quantity: 1, unit: '套', price: 1000, function: '厘米级高精度定位' },
          { name: '惯导模块', model: 'MEMS惯导', quantity: 1, unit: '个', price: 500, function: 'GNSS失效时姿态感知' },
          { name: '毫米波雷达', model: '77GHz远距雷达', quantity: 1, unit: '个', price: 3000, function: '动态目标识别与全天候避障' },
          { name: '激光雷达', model: '360°固态激光雷达', quantity: 1, unit: '个', price: 6000, function: '高精度近程环境建模' }
        ]
      },
      {
        category: '船体与结构',
        items: [
          { name: '玻璃钢船体', model: 'FRP+泡沫夹芯结构', quantity: 1, unit: '套', price: 4000, function: '轻量化高强度船体' }
        ]
      }
    ]
  },
  {
    id: 'usv-5m-work',
    name: '5米作业艇智能USV方案',
    boatType: '作业艇/巡逻艇',
    boatLength: 5,
    batteryCapacity: 100,
    voltage: 350,
    speed: 25,
    range: 100,
    application: '海上作业/巡逻监测',
    price: '15-20万',
    features: [
      '100kWh大容量电池包',
      '增强型感知系统',
      '长时间作业能力',
      '多功能载荷接口',
      '船岸一体化通信',
      '数据回传与实时监控'
    ],
    description: '针对5米级作业艇设计，支持长时间海上作业任务。适用于海洋监测、水质采样、海上施工辅助等场景。',
    bom: [
      {
        category: 'AI主控与计算',
        items: [
          { name: 'AI主控', model: 'Jetson AGX Orin Edge AI模块', quantity: 1, unit: '套', price: 8000, function: '高性能计算平台，支持多传感器融合' },
          { name: '工控板', model: '工业载板', quantity: 1, unit: '块', price: 1500, function: '多路CAN/以太网接口' }
        ]
      },
      {
        category: '动力与能源系统',
        items: [
          { name: '高压电池包', model: '108S1P (300Ah/3.2V)', quantity: 1, unit: '套', price: 50000, function: '系统电压345.6V，总能量103.68kWh' },
          { name: 'BMS', model: '工业级电池管理系统', quantity: 1, unit: '套', price: 3000, function: '主动均衡，支持热管理' },
          { name: 'DC/DC转换器', model: 'Vicor 3kW', quantity: 2, unit: '个', price: 2000, function: '高效率电压转换' },
          { name: '推进电机', model: '40kW BLDC 永磁同步电机', quantity: 2, unit: '个', price: 6000, function: '双机推进，总功率80kW' },
          { name: '喷水推进器', model: '重型Marine Jet', quantity: 2, unit: '套', price: 5000, function: '大功率喷水推进' }
        ]
      },
      {
        category: '通信与传感器',
        items: [
          { name: '卫星通信模块', model: '多模卫星终端', quantity: 1, unit: '套', price: 8000, function: '支持铱星/海事/天通/星链' },
          { name: '4G/5G路由器', model: '双模工业路由器', quantity: 1, unit: '个', price: 1500, function: '高速数据传输' },
          { name: 'GPS/RTK定位', model: 'RTK定位套件', quantity: 1, unit: '套', price: 3000, function: '厘米级定位精度' },
          { name: '毫米波雷达', model: '77GHz远距雷达', quantity: 2, unit: '个', price: 6000, function: '360°目标检测' },
          { name: '激光雷达', model: '360°固态激光雷达', quantity: 1, unit: '个', price: 12000, function: '环境建模与避障' },
          { name: '光电吊舱', model: '可见光+红外摄像头', quantity: 1, unit: '套', price: 5000, function: '目标识别与跟踪' }
        ]
      },
      {
        category: '船体与结构',
        items: [
          { name: '玻璃钢船体', model: 'FRP+泡沫夹芯结构', quantity: 1, unit: '套', price: 8000, function: '5米双体船结构' }
        ]
      }
    ]
  },
  {
    id: 'usv-8m-survey',
    name: '8米测量艇智能USV方案',
    boatType: '测量艇/调查艇',
    boatLength: 8,
    batteryCapacity: 150,
    voltage: 400,
    speed: 20,
    range: 150,
    application: '海洋测绘/水文调查',
    price: '30-45万',
    features: [
      '150kWh超大容量电池',
      '专业测量载荷预留',
      '高精度定位定向',
      '长时间自主巡航',
      '多波束声呐支持',
      '数据实时处理'
    ],
    description: '针对8米级专业测量艇设计，支持多种测量设备载荷。适用于海洋地形测绘、水文水质调查、海底管道检测等高价值任务。',
    bom: [
      {
        category: 'AI主控与计算',
        items: [
          { name: 'AI主控', model: 'Jetson AGX Orin 64GB', quantity: 2, unit: '套', price: 20000, function: '双机冗余计算平台' },
          { name: '边缘计算单元', model: '工业GPU边缘服务器', quantity: 1, unit: '套', price: 15000, function: '实时数据处理' }
        ]
      },
      {
        category: '动力与能源系统',
        items: [
          { name: '高压电池包', model: '126S2P (280Ah/3.2V)', quantity: 1, unit: '套', price: 80000, function: '系统电压403.2V，总能量225.8kWh' },
          { name: 'BMS', model: '车规级BMS', quantity: 1, unit: '套', price: 8000, function: '全套热管理与均衡' },
          { name: 'DC/DC转换器', model: 'Vicor 5kW', quantity: 3, unit: '个', price: 4500, function: '多电压输出' },
          { name: '推进电机', model: '60kW BLDC 永磁同步电机', quantity: 2, unit: '个', price: 15000, function: '重载推进系统' },
          { name: '推进器', model: '全回转推进器', quantity: 2, unit: '套', price: 20000, function: '精确姿态控制' }
        ]
      },
      {
        category: '通信与传感器',
        items: [
          { name: '卫星通信模块', model: '多模卫星终端', quantity: 1, unit: '套', price: 15000, function: '全天候通信保障' },
          { name: 'Mesh自组网', model: '无线自组网模块', quantity: 1, unit: '套', price: 5000, function: '多艇协同通信' },
          { name: '高精度定位', model: 'RTK+INS组合导航', quantity: 1, unit: '套', price: 15000, function: '亚厘米级定位' },
          { name: '毫米波雷达', model: '4D成像雷达', quantity: 2, unit: '个', price: 16000, function: '复杂环境感知' },
          { name: '激光雷达', model: '128线激光雷达', quantity: 1, unit: '个', price: 80000, function: '高精度环境建模' },
          { name: '声呐系统', model: '多波束声呐', quantity: 1, unit: '套', price: 50000, function: '水下地形测量' }
        ]
      },
      {
        category: '船体与结构',
        items: [
          { name: '复合材料船体', model: '碳纤维+FRP混合结构', quantity: 1, unit: '套', price: 30000, function: '轻量化高强度船体' }
        ]
      }
    ]
  }
];

export const boatTypes = [
  { value: 'patrol', label: '巡逻艇', description: '近海巡逻、海上执法' },
  { value: 'work', label: '作业艇', description: '海上作业、设备运输' },
  { value: 'survey', label: '测量艇', description: '海洋测绘、水文调查' },
  { value: 'assault', label: '突击艇', description: '高速突击、目标拦截' },
  { value: 'fishing', label: '作业渔船', description: '海上养殖、捕捞作业' },
  { value: 'transport', label: '运输艇', description: '物资运输、人员接送' }
];

export const applications = [
  { value: 'patrol', label: '海上巡逻', icon: 'shield' },
  { value: 'monitor', label: '环境监测', icon: 'activity' },
  { value: 'survey', label: '海洋测绘', icon: 'map' },
  { value: 'rescue', label: '海上救援', icon: 'life-buoy' },
  { value: 'military', label: '军事应用', icon: 'crosshair' },
  { value: 'fishing', label: '渔业作业', icon: 'anchor' }
];
