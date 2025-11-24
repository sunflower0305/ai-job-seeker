'use client';

import { useEffect, useState, useRef } from 'react';
import ReactECharts from 'echarts-for-react';
import * as echarts from 'echarts';

interface DashboardData {
  city_distribution: Array<{ name: string; value: number }>;
  industry_distribution: Array<{ name: string; value: number }>;
  salary_distribution: Array<{ name: string; value: number }>;
  top_companies: Array<{ name: string; value: number; industry: string }>;
  top_skills: Array<{ name: string; value: number }>;
  statistics: {
    total_jobs: number;
    total_companies: number;
    total_applications: number;
    avg_salary: number;
  };
  education_distribution: Array<{ name: string; value: number }>;
  experience_distribution: Array<{ name: string; value: number }>;
}

export default function DashboardScreen() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [mapRegistered, setMapRegistered] = useState(false);
  const scrollIndexRef = useRef(0);

  // 注册中国地图
  useEffect(() => {
    const loadMap = async () => {
      try {
        const response = await fetch('/maps/china.json');
        const geoJson = await response.json();
        echarts.registerMap('china', geoJson);
        setMapRegistered(true);
      } catch (error) {
        console.error('加载地图数据失败:', error);
      }
    };
    loadMap();
  }, []);

  // 获取数据
  const fetchData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/jobs/dashboard-screen/');
      if (response.ok) {
        const result = await response.json();
        setData(result);
      }
    } catch (error) {
      console.error('获取数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // 每30秒刷新一次数据
    const dataInterval = setInterval(fetchData, 30000);

    // 更新时间
    const timeInterval = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => {
      clearInterval(dataInterval);
      clearInterval(timeInterval);
    };
  }, []);

  // 城市职位分布地图配置
  const getChinaMapOption = () => {
    if (!data || !mapRegistered) return {};

    // 处理城市数据，添加省份映射
    const cityToProvince: { [key: string]: string } = {
      '北京': '北京市',
      '上海': '上海市',
      '天津': '天津市',
      '重庆': '重庆市',
      '深圳': '广东省',
      '广州': '广东省',
      '杭州': '浙江省',
      '南京': '江苏省',
      '苏州': '江苏省',
      '成都': '四川省',
      '武汉': '湖北省',
      '西安': '陕西省',
      '郑州': '河南省',
      '长沙': '湖南省',
      '青岛': '山东省',
      '济南': '山东省',
      '大连': '辽宁省',
      '沈阳': '辽宁省',
      '福州': '福建省',
      '厦门': '福建省',
      '合肥': '安徽省',
      '南昌': '江西省',
      '南宁': '广西壮族自治区',
      '昆明': '云南省',
      '贵阳': '贵州省',
      '石家庄': '河北省',
      '太原': '山西省',
      '哈尔滨': '黑龙江省',
      '长春': '吉林省',
      '兰州': '甘肃省',
      '乌鲁木齐': '新疆维吾尔自治区',
      '银川': '宁夏回族自治区',
      '西宁': '青海省',
      '海口': '海南省',
      '拉萨': '西藏自治区',
      '呼和浩特': '内蒙古自治区',
    };

    // 聚合省份数据
    const provinceData: { [key: string]: number } = {};
    data.city_distribution.forEach(city => {
      const province = cityToProvince[city.name] || city.name;
      provinceData[province] = (provinceData[province] || 0) + city.value;
    });

    const mapData = Object.entries(provinceData).map(([name, value]) => ({
      name,
      value,
    }));

    // 获取最大值和最小值用于视觉映射
    const values = mapData.map(item => item.value);
    const maxValue = Math.max(...values);
    const minValue = Math.min(...values);

    console.log('地图数据:', mapData);
    console.log('最大值:', maxValue, '最小值:', minValue);

    return {
      backgroundColor: 'transparent',
      title: {
        text: '全国职位分布地图',
        left: 'center',
        top: 10,
        textStyle: {
          color: '#fff',
          fontSize: 20,
          fontWeight: 'bold',
        },
      },
      tooltip: {
        trigger: 'item',
        formatter: function(params: any) {
          if (params.value) {
            return `${params.name}<br/>职位数量: ${params.value}`;
          }
          return `${params.name}<br/>暂无数据`;
        },
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        borderColor: '#4a90e2',
        borderWidth: 1,
        textStyle: {
          color: '#fff',
        },
      },
      visualMap: {
        min: 0,
        max: maxValue,
        text: ['高', '低'],
        realtime: true,
        calculable: true,
        inRange: {
          // 使用更明显的颜色渐变：浅黄色 -> 橙色 -> 红色
          color: ['#ffffcc', '#ffeda0', '#fed976', '#feb24c', '#fd8d3c', '#fc4e2a', '#e31a1c', '#bd0026', '#800026'],
        },
        textStyle: {
          color: '#fff',
        },
        left: 'left',
        bottom: '10%',
      },
      series: [
        {
          name: '职位数量',
          type: 'map',
          map: 'china',
          roam: true,
          emphasis: {
            label: {
              show: true,
              color: '#fff',
              fontSize: 12,
              fontWeight: 'bold',
            },
            itemStyle: {
              areaColor: '#ffd700',
              borderColor: '#fff',
              borderWidth: 2,
              shadowBlur: 10,
              shadowColor: 'rgba(255, 215, 0, 0.5)',
            },
          },
          itemStyle: {
            // 移除固定颜色，让visualMap生效
            borderColor: '#2d3748',
            borderWidth: 1.5,
            shadowBlur: 3,
            shadowColor: 'rgba(0, 0, 0, 0.3)',
          },
          label: {
            show: true,
            color: '#fff',
            fontSize: 9,
          },
          data: mapData,
        },
      ],
    };
  };

  // 行业分布玫瑰图配置
  const getRoseChartOption = () => {
    if (!data) return {};

    return {
      backgroundColor: 'transparent',
      title: {
        text: '行业分布',
        left: 'center',
        top: 10,
        textStyle: {
          color: '#fff',
          fontSize: 18,
          fontWeight: 'bold',
        },
      },
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)',
      },
      legend: {
        show: false,
      },
      series: [
        {
          name: '行业分布',
          type: 'pie',
          radius: ['30%', '70%'],
          center: ['50%', '55%'],
          roseType: 'area',
          itemStyle: {
            borderRadius: 8,
          },
          label: {
            color: '#fff',
            fontSize: 12,
          },
          data: data.industry_distribution,
        },
      ],
      color: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#5ab1ef'],
    };
  };

  // 薪资分布滚动柱状图配置
  const getSalaryBarOption = () => {
    if (!data) return {};

    const displayCount = 5;
    const startIndex = scrollIndexRef.current % data.salary_distribution.length;
    const displayData = [
      ...data.salary_distribution.slice(startIndex, startIndex + displayCount),
      ...data.salary_distribution.slice(0, Math.max(0, startIndex + displayCount - data.salary_distribution.length))
    ].slice(0, displayCount);

    return {
      backgroundColor: 'transparent',
      title: {
        text: '薪资区间分布',
        left: 'center',
        top: 10,
        textStyle: {
          color: '#fff',
          fontSize: 18,
          fontWeight: 'bold',
        },
      },
      grid: {
        left: '10%',
        right: '10%',
        bottom: '15%',
        top: '20%',
        containLabel: true,
      },
      xAxis: {
        type: 'category',
        data: displayData.map(item => item.name),
        axisLine: {
          lineStyle: {
            color: '#4a5568',
          },
        },
        axisLabel: {
          color: '#a0aec0',
          fontSize: 12,
        },
      },
      yAxis: {
        type: 'value',
        axisLine: {
          lineStyle: {
            color: '#4a5568',
          },
        },
        splitLine: {
          lineStyle: {
            color: '#2d3748',
          },
        },
        axisLabel: {
          color: '#a0aec0',
        },
      },
      series: [
        {
          name: '职位数量',
          type: 'bar',
          data: displayData.map(item => item.value),
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#83bff6' },
              { offset: 0.5, color: '#188df0' },
              { offset: 1, color: '#188df0' },
            ]),
            borderRadius: [5, 5, 0, 0],
          },
          label: {
            show: true,
            position: 'top',
            color: '#fff',
            fontSize: 12,
          },
          barWidth: '50%',
        },
      ],
    };
  };

  // 学历要求分布配置
  const getEducationPieOption = () => {
    if (!data) return {};

    return {
      backgroundColor: 'transparent',
      title: {
        text: '学历要求分布',
        left: 'center',
        top: 10,
        textStyle: {
          color: '#fff',
          fontSize: 18,
          fontWeight: 'bold',
        },
      },
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)',
      },
      legend: {
        orient: 'vertical',
        right: 10,
        top: 'center',
        textStyle: {
          color: '#fff',
        },
      },
      series: [
        {
          name: '学历要求',
          type: 'pie',
          radius: ['40%', '60%'],
          center: ['40%', '55%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#1a202c',
            borderWidth: 2,
          },
          label: {
            show: true,
            color: '#fff',
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 14,
              fontWeight: 'bold',
            },
          },
          data: data.education_distribution,
        },
      ],
      color: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'],
    };
  };

  // 滚动效果
  useEffect(() => {
    if (!data) return;

    const scrollInterval = setInterval(() => {
      scrollIndexRef.current = (scrollIndexRef.current + 1) % data.salary_distribution.length;
    }, 3000);

    return () => clearInterval(scrollInterval);
  }, [data]);

  if (loading || !mapRegistered) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 flex items-center justify-center">
        <div className="text-white text-2xl">数据加载中...</div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 flex items-center justify-center">
        <div className="text-white text-2xl">暂无数据</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 p-6">
      {/* 顶部标题栏 */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-2 h-12 bg-blue-500 rounded"></div>
            <h1 className="text-4xl font-bold text-white">智能招聘数据大屏</h1>
          </div>
          <div className="text-white text-xl font-mono">
            {currentTime.toLocaleString('zh-CN', {
              year: 'numeric',
              month: '2-digit',
              day: '2-digit',
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit',
            })}
          </div>
        </div>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-4 gap-6 mb-6">
        <div className="bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg p-6 shadow-xl">
          <div className="text-blue-200 text-sm mb-2">总职位数</div>
          <div className="text-white text-4xl font-bold">{data.statistics.total_jobs.toLocaleString()}</div>
          <div className="text-blue-300 text-xs mt-2">↑ 实时更新</div>
        </div>
        <div className="bg-gradient-to-br from-green-600 to-green-800 rounded-lg p-6 shadow-xl">
          <div className="text-green-200 text-sm mb-2">合作企业</div>
          <div className="text-white text-4xl font-bold">{data.statistics.total_companies.toLocaleString()}</div>
          <div className="text-green-300 text-xs mt-2">↑ 持续增长</div>
        </div>
        <div className="bg-gradient-to-br from-purple-600 to-purple-800 rounded-lg p-6 shadow-xl">
          <div className="text-purple-200 text-sm mb-2">简历投递</div>
          <div className="text-white text-4xl font-bold">{data.statistics.total_applications.toLocaleString()}</div>
          <div className="text-purple-300 text-xs mt-2">↑ 火热进行</div>
        </div>
        <div className="bg-gradient-to-br from-orange-600 to-orange-800 rounded-lg p-6 shadow-xl">
          <div className="text-orange-200 text-sm mb-2">平均薪资</div>
          <div className="text-white text-4xl font-bold">{(data.statistics.avg_salary / 1000).toFixed(1)}k</div>
          <div className="text-orange-300 text-xs mt-2">↑ 薪资水平</div>
        </div>
      </div>

      {/* 图表区域 */}
      <div className="grid grid-cols-3 gap-6 mb-6">
        {/* 左侧 - 行业分布玫瑰图 */}
        <div className="bg-gray-800 bg-opacity-50 backdrop-blur rounded-lg shadow-xl p-4">
          <ReactECharts option={getRoseChartOption()} style={{ height: '400px' }} />
        </div>

        {/* 中间 - 中国地图 */}
        <div className="bg-gray-800 bg-opacity-50 backdrop-blur rounded-lg shadow-xl p-4">
          <ReactECharts
            option={getChinaMapOption()}
            style={{ height: '400px' }}
            notMerge={true}
            lazyUpdate={true}
          />
        </div>

        {/* 右侧 - 学历要求分布 */}
        <div className="bg-gray-800 bg-opacity-50 backdrop-blur rounded-lg shadow-xl p-4">
          <ReactECharts option={getEducationPieOption()} style={{ height: '400px' }} />
        </div>
      </div>

      {/* 下方区域 */}
      <div className="grid grid-cols-3 gap-6">
        {/* 薪资分布滚动柱状图 */}
        <div className="bg-gray-800 bg-opacity-50 backdrop-blur rounded-lg shadow-xl p-4">
          <ReactECharts option={getSalaryBarOption()} style={{ height: '350px' }} />
        </div>

        {/* TOP公司排行榜 */}
        <div className="bg-gray-800 bg-opacity-50 backdrop-blur rounded-lg shadow-xl p-6">
          <h3 className="text-white text-lg font-bold mb-4 flex items-center gap-2">
            <span className="text-yellow-500">🏆</span> TOP公司招聘排行
          </h3>
          <div className="space-y-3">
            {data.top_companies.slice(0, 8).map((company, index) => (
              <div key={index} className="flex items-center justify-between bg-gray-700 bg-opacity-50 rounded-lg p-3">
                <div className="flex items-center gap-3 flex-1">
                  <span className={`text-lg font-bold ${
                    index === 0 ? 'text-yellow-400' :
                    index === 1 ? 'text-gray-300' :
                    index === 2 ? 'text-orange-400' : 'text-blue-400'
                  }`}>
                    {index + 1}
                  </span>
                  <div className="flex-1">
                    <div className="text-white font-medium truncate">{company.name}</div>
                    <div className="text-gray-400 text-xs">{company.industry}</div>
                  </div>
                </div>
                <span className="text-green-400 font-bold text-lg">{company.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* 热门技能TOP */}
        <div className="bg-gray-800 bg-opacity-50 backdrop-blur rounded-lg shadow-xl p-6">
          <h3 className="text-white text-lg font-bold mb-4 flex items-center gap-2">
            <span className="text-blue-500">🔥</span> 热门技能TOP10
          </h3>
          <div className="space-y-2">
            {data.top_skills.map((skill, index) => (
              <div key={index} className="bg-gray-700 bg-opacity-50 rounded-lg p-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-white font-medium">{skill.name}</span>
                  <span className="text-blue-400 font-bold">{skill.value}</span>
                </div>
                <div className="w-full bg-gray-600 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${(skill.value / data.top_skills[0].value) * 100}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
