'use client';

import { useEffect, useState, useRef, useMemo } from 'react';
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
  const mapInstanceRef = useRef<any>(null);

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

  // 使用 useMemo 缓存地图配置 - 显示城市分布
  const getChinaMapOption = useMemo(() => {
    if (!data || !mapRegistered) return {};

    // 城市坐标映射（主要城市的经纬度）
    const cityCoordinates: { [key: string]: [number, number] } = {
      '北京': [116.4074, 39.9042],
      '上海': [121.4737, 31.2304],
      '天津': [117.2010, 39.0842],
      '重庆': [106.5516, 29.5630],
      '深圳': [114.0579, 22.5431],
      '广州': [113.2644, 23.1291],
      '杭州': [120.1551, 30.2741],
      '南京': [118.7969, 32.0603],
      '苏州': [120.5954, 31.2989],
      '成都': [104.0665, 30.5723],
      '武汉': [114.3054, 30.5931],
      '西安': [108.9398, 34.3416],
      '郑州': [113.6254, 34.7466],
      '长沙': [112.9388, 28.2282],
      '青岛': [120.3826, 36.0671],
      '济南': [117.1205, 36.6519],
      '大连': [121.6147, 38.9140],
      '沈阳': [123.4328, 41.8045],
      '福州': [119.2965, 26.0745],
      '厦门': [118.0894, 24.4798],
      '合肥': [117.2272, 31.8206],
      '南昌': [115.8581, 28.6832],
      '南宁': [108.3661, 22.8172],
      '昆明': [102.8329, 24.8801],
      '贵阳': [106.7135, 26.5783],
      '石家庄': [114.5149, 38.0428],
      '太原': [112.5489, 37.8706],
      '哈尔滨': [126.5348, 45.8038],
      '长春': [125.3245, 43.8171],
      '兰州': [103.8343, 36.0611],
      '乌鲁木齐': [87.6168, 43.8256],
      '银川': [106.2586, 38.4680],
      '西宁': [101.7782, 36.6171],
      '海口': [110.3312, 20.0311],
      '拉萨': [91.1320, 29.6625],
      '呼和浩特': [111.6708, 40.8183],
    };

    // 准备散点数据
    const scatterData = data.city_distribution
      .filter(city => cityCoordinates[city.name])
      .map(city => ({
        name: city.name,
        value: [...cityCoordinates[city.name], city.value],
      }));

    // 获取最大值用于散点大小映射
    const maxValue = Math.max(...data.city_distribution.map(item => item.value), 1);

    return {
      backgroundColor: 'transparent',
      title: {
        text: '全国职位分布地图（城市）',
        left: 'center',
        top: 10,
        textStyle: {
          color: '#fff',
          fontSize: 22,
          fontWeight: 'bold',
        },
      },
      tooltip: {
        trigger: 'item',
        formatter: function(params: any) {
          if (params.seriesType === 'scatter') {
            return `${params.name}<br/>职位数量: ${params.value[2]}`;
          }
          return params.name;
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
          symbolSize: [10, 50], // 散点大小范围
          color: ['#ffffcc', '#ffeda0', '#fed976', '#feb24c', '#fd8d3c', '#fc4e2a', '#e31a1c', '#bd0026', '#800026'],
        },
        textStyle: {
          color: '#fff',
        },
        left: 'left',
        bottom: '8%',
      },
      geo: {
        map: 'china',
        roam: true,
        zoom: 1.2, // 放大地图
        itemStyle: {
          areaColor: '#1e3a8a',
          borderColor: '#4a5568',
          borderWidth: 1,
        },
        emphasis: {
          itemStyle: {
            areaColor: '#2563eb',
          },
        },
        label: {
          show: false, // 隐藏省份标签，突出城市
        },
      },
      series: [
        {
          name: '职位数量',
          type: 'scatter',
          coordinateSystem: 'geo',
          data: scatterData,
          symbolSize: function (val: any) {
            // 根据职位数量动态调整散点大小
            return Math.sqrt(val[2]) * 3 + 8;
          },
          label: {
            show: true,
            formatter: '{b}',
            position: 'right',
            color: '#fff',
            fontSize: 11,
            fontWeight: 'bold',
            textShadowColor: '#000',
            textShadowBlur: 3,
          },
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(255, 178, 72, 0.5)',
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 14,
            },
            itemStyle: {
              borderColor: '#fff',
              borderWidth: 2,
            },
          },
        },
        {
          name: '涟漪效果',
          type: 'effectScatter',
          coordinateSystem: 'geo',
          data: scatterData.slice(0, 5), // 只对TOP5城市添加动画效果
          symbolSize: function (val: any) {
            return Math.sqrt(val[2]) * 3 + 8;
          },
          showEffectOn: 'render',
          rippleEffect: {
            brushType: 'stroke',
            scale: 3,
            period: 4,
          },
          label: {
            show: false,
          },
          itemStyle: {
            color: '#ffd700',
            shadowBlur: 10,
            shadowColor: '#ffd700',
          },
          zlevel: 1,
        },
      ],
    };
  }, [data, mapRegistered]);

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
          radius: '60%',
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
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 p-4">
      {/* 顶部标题栏 */}
      <div className="mb-3">
        <div className="flex items-center justify-center relative">
          <h1 className="text-4xl font-bold text-white">智能招聘数据大屏</h1>
          <div className="absolute right-0 text-white text-xl font-mono">
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

      {/* 主要图表区域 - 新布局 */}
      <div className="grid grid-cols-4 gap-4 mb-3">
        {/* 左侧列 - 玫瑰图和学历分布 */}
        <div className="space-y-4">
          {/* 行业分布玫瑰图 */}
          <div className="bg-gray-800 bg-opacity-50 backdrop-blur rounded-lg shadow-xl p-3">
            <ReactECharts option={getRoseChartOption()} style={{ height: '220px' }} />
          </div>

          {/* 学历要求分布 */}
          <div className="bg-gray-800 bg-opacity-50 backdrop-blur rounded-lg shadow-xl p-3">
            <ReactECharts option={getEducationPieOption()} style={{ height: '220px' }} />
          </div>
        </div>

        {/* 中间大地图 - 占2列 */}
        <div className="col-span-2 bg-gray-800 bg-opacity-50 backdrop-blur rounded-lg shadow-xl p-3">
          <ReactECharts
            option={getChinaMapOption}
            style={{ height: '464px' }}
            notMerge={true}
            lazyUpdate={true}
            opts={{ renderer: 'canvas' }}
            onChartReady={(instance) => {
              mapInstanceRef.current = instance;
            }}
          />
        </div>

        {/* 右侧列 - 薪资分布 */}
        <div className="bg-gray-800 bg-opacity-50 backdrop-blur rounded-lg shadow-xl p-3">
          <ReactECharts option={getSalaryBarOption()} style={{ height: '464px' }} />
        </div>
      </div>

      {/* 下方排行榜区域 */}
      <div className="grid grid-cols-2 gap-4">
        {/* TOP公司排行榜 - 自动滚动 */}
        <div className="bg-gray-800 bg-opacity-50 backdrop-blur rounded-lg shadow-xl p-4">
          <h3 className="text-white text-lg font-bold mb-4 flex items-center gap-2">
            <span className="text-yellow-500">🏆</span> TOP公司招聘排行
          </h3>
          <div className="h-[200px] overflow-hidden relative">
            <div
              className="space-y-3 animate-scroll-up"
              style={{
                animation: 'scrollUp 20s linear infinite',
              }}
            >
              {/* 复制两份数据实现无缝滚动 */}
              {[...data.top_companies, ...data.top_companies].map((company, index) => (
                <div key={index} className="flex items-center justify-between bg-gray-700 bg-opacity-50 rounded-lg p-3">
                  <div className="flex items-center gap-3 flex-1">
                    <span className={`text-lg font-bold ${
                      (index % data.top_companies.length) === 0 ? 'text-yellow-400' :
                      (index % data.top_companies.length) === 1 ? 'text-gray-300' :
                      (index % data.top_companies.length) === 2 ? 'text-orange-400' : 'text-blue-400'
                    }`}>
                      {(index % data.top_companies.length) + 1}
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
        </div>

        {/* 热门技能TOP - 自动滚动 */}
        <div className="bg-gray-800 bg-opacity-50 backdrop-blur rounded-lg shadow-xl p-4">
          <h3 className="text-white text-lg font-bold mb-4 flex items-center gap-2">
            <span className="text-blue-500">🔥</span> 热门技能TOP10
          </h3>
          <div className="h-[200px] overflow-hidden relative">
            <div
              className="space-y-2 animate-scroll-up"
              style={{
                animation: 'scrollUp 25s linear infinite',
              }}
            >
              {/* 复制两份数据实现无缝滚动 */}
              {[...data.top_skills, ...data.top_skills].map((skill, index) => (
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

      {/* CSS动画 */}
      <style jsx>{`
        @keyframes scrollUp {
          0% {
            transform: translateY(0);
          }
          100% {
            transform: translateY(-50%);
          }
        }
      `}</style>
    </div>
  );
}
