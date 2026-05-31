'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { apiUrl } from '@/lib/api';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface StatisticsData {
  skills_distribution: Array<{ skill: string; count: number }>;
}

export default function WordCloudAnalyticsPage() {
  const [data, setData] = useState<StatisticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(Date.now());

  useEffect(() => {
    fetchStatistics();
  }, []);

  const fetchStatistics = async () => {
    try {
      setLoading(true);
      const response = await fetch(apiUrl('/api/jobs/jobs/statistics/'));
      if (!response.ok) throw new Error('Failed to fetch statistics');
      const result = await response.json();
      setData(result);
    } catch (err) {
      console.error('Error fetching statistics:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    setRefreshKey(Date.now());
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 text-lg">数据加载失败</p>
          <button
            onClick={() => fetchStatistics()}
            className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            重新加载
          </button>
        </div>
      </div>
    );
  }

  const skillsData = data.skills_distribution.slice(0, 20).map(item => ({
    name: item.skill,
    需求数: item.count,
  }));

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 面包屑导航 */}
        <div className="mb-6 flex items-center text-sm text-gray-600">
          <Link href="/analytics" className="hover:text-blue-600">数据分析</Link>
          <span className="mx-2">/</span>
          <span className="text-gray-900">技能词云</span>
        </div>

        {/* 标题 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">技能需求词云</h1>
          <p className="mt-2 text-gray-600">市场热门技能可视化分析</p>
        </div>

        {/* 技能词云图 */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-bold text-gray-900">技能需求词云图</h2>
            <button
              onClick={handleRefresh}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              刷新词云
            </button>
          </div>
          <p className="text-sm text-gray-600 mb-6">
            词语大小代表技能需求数量，采用椭圆形布局，核心技能在中央
          </p>
          <div className="flex items-center justify-center rounded-lg overflow-hidden bg-white" style={{ minHeight: 600 }}>
            {data.skills_distribution.length > 0 ? (
              <img
                src={apiUrl(`/api/jobs/jobs/wordcloud/?width=1000&height=700&t=${refreshKey}`)}
                alt="技能需求词云图"
                className="max-w-full h-auto rounded-lg"
                style={{ maxHeight: '700px' }}
              />
            ) : (
              <div className="text-gray-500 text-center p-8">
                <p>暂无技能数据</p>
              </div>
            )}
          </div>
        </div>

        {/* 技能排行榜 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 柱状图 */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Top 20 热门技能</h2>
            <ResponsiveContainer width="100%" height={500}>
              <BarChart data={skillsData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" width={100} />
                <Tooltip />
                <Legend />
                <Bar dataKey="需求数" fill="#3B82F6" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* 排行榜列表 */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">技能需求排行</h2>
            <div className="space-y-3 max-h-[500px] overflow-y-auto">
              {data.skills_distribution.slice(0, 10).map((skill, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                      index === 0 ? 'bg-yellow-400 text-white' :
                      index === 1 ? 'bg-gray-300 text-gray-800' :
                      index === 2 ? 'bg-orange-400 text-white' :
                      'bg-blue-100 text-blue-700'
                    }`}>
                      {index + 1}
                    </div>
                    <span className="font-medium text-gray-900">{skill.skill}</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <div className="text-sm text-gray-500">需求数</div>
                      <div className="text-lg font-bold text-blue-600">{skill.count}</div>
                    </div>
                    <div className="w-24 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{
                          width: `${(skill.count / data.skills_distribution[0].count) * 100}%`
                        }}
                      ></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 技能分类洞察 */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">技能洞察</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="border-l-4 border-blue-500 pl-4">
              <h3 className="font-semibold text-gray-900">最热门技能</h3>
              <p className="text-gray-600 mt-1">
                {data.skills_distribution[0]?.skill || '-'} ({data.skills_distribution[0]?.count || 0}个职位)
              </p>
            </div>
            <div className="border-l-4 border-green-500 pl-4">
              <h3 className="font-semibold text-gray-900">技能种类</h3>
              <p className="text-gray-600 mt-1">
                共 {data.skills_distribution.length} 种技能
              </p>
            </div>
            <div className="border-l-4 border-purple-500 pl-4">
              <h3 className="font-semibold text-gray-900">技能集中度</h3>
              <p className="text-gray-600 mt-1">
                {(() => {
                  const top5Total = data.skills_distribution.slice(0, 5).reduce((sum, item) => sum + item.count, 0);
                  const totalCount = data.skills_distribution.reduce((sum, item) => sum + item.count, 0);
                  const concentration = ((top5Total / totalCount) * 100).toFixed(1);
                  return `Top 5 技能占比 ${concentration}%`;
                })()}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
