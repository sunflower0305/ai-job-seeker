'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { apiUrl } from '@/lib/api';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface StatisticsData {
  city_distribution: Array<{ city: string; count: number; avg_salary: number }>;
}

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'];

export default function CityAnalyticsPage() {
  const [data, setData] = useState<StatisticsData | null>(null);
  const [loading, setLoading] = useState(true);

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

  const cityJobsData = data.city_distribution.slice(0, 15).map(item => ({
    name: item.city,
    职位数: item.count,
  }));

  const citySalaryData = data.city_distribution.slice(0, 12).map(item => ({
    name: item.city,
    平均薪资: Math.round(item.avg_salary),
  }));

  const cityPieData = data.city_distribution.slice(0, 8).map(item => ({
    name: item.city,
    value: item.count,
  }));

  const totalJobs = data.city_distribution.reduce((sum, item) => sum + item.count, 0);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 面包屑导航 */}
        <div className="mb-6 flex items-center text-sm text-gray-600">
          <Link href="/analytics" className="hover:text-blue-600">数据分析</Link>
          <span className="mx-2">/</span>
          <span className="text-gray-900">城市分析</span>
        </div>

        {/* 标题 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">城市分析</h1>
          <p className="mt-2 text-gray-600">各城市职位分布与薪资水平分析</p>
        </div>

        {/* 统计卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-blue-100 rounded-lg p-3">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">覆盖城市</p>
                <p className="text-2xl font-bold text-gray-900">{data.city_distribution.length}个</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-green-100 rounded-lg p-3">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">职位最多城市</p>
                <p className="text-2xl font-bold text-gray-900">{data.city_distribution[0]?.city || '-'}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-yellow-100 rounded-lg p-3">
                <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">薪资最高城市</p>
                <p className="text-2xl font-bold text-gray-900">
                  {(() => {
                    const sortedCities = [...data.city_distribution].sort((a, b) => b.avg_salary - a.avg_salary);
                    return sortedCities[0]?.city || '-';
                  })()}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* 图表区域 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 城市职位数量分布 */}
          <div className="bg-white rounded-lg shadow p-6 lg:col-span-2">
            <h2 className="text-lg font-bold text-gray-900 mb-4">各城市职位数量 Top 15</h2>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={cityJobsData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="职位数" fill="#3B82F6" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* 城市平均薪资 */}
          <div className="bg-white rounded-lg shadow p-6 lg:col-span-2">
            <h2 className="text-lg font-bold text-gray-900 mb-4">各城市平均薪资对比 Top 12</h2>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={citySalaryData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="平均薪资" fill="#10B981" name="平均薪资(元)" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* 城市职位占比饼图 */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Top 8 城市职位占比</h2>
            <ResponsiveContainer width="100%" height={350}>
              <PieChart>
                <Pie
                  data={cityPieData}
                  cx="50%"
                  cy="50%"
                  labelLine={true}
                  label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(1)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {cityPieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* 城市排行榜 */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">城市综合排行</h2>
            <div className="space-y-3 max-h-[350px] overflow-y-auto">
              {data.city_distribution.slice(0, 10).map((city, index) => (
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
                    <span className="font-medium text-gray-900">{city.city}</span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-gray-500">职位: {city.count}</div>
                    <div className="text-sm text-green-600 font-medium">薪资: {Math.round(city.avg_salary)}元</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 城市洞察 */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">城市洞察</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="border-l-4 border-blue-500 pl-4">
              <h3 className="font-semibold text-gray-900">一线城市集中度</h3>
              <p className="text-gray-600 mt-1">
                {(() => {
                  const firstTierCities = ['北京', '上海', '广州', '深圳'];
                  const firstTierCount = data.city_distribution
                    .filter(c => firstTierCities.includes(c.city))
                    .reduce((sum, c) => sum + c.count, 0);
                  const percentage = ((firstTierCount / totalJobs) * 100).toFixed(1);
                  return `一线城市职位占比 ${percentage}%`;
                })()}
              </p>
            </div>
            <div className="border-l-4 border-green-500 pl-4">
              <h3 className="font-semibold text-gray-900">薪资最高城市</h3>
              <p className="text-gray-600 mt-1">
                {(() => {
                  const sortedCities = [...data.city_distribution].sort((a, b) => b.avg_salary - a.avg_salary);
                  return `${sortedCities[0]?.city || '-'} (${Math.round(sortedCities[0]?.avg_salary || 0)}元)`;
                })()}
              </p>
            </div>
            <div className="border-l-4 border-purple-500 pl-4">
              <h3 className="font-semibold text-gray-900">机会最多城市</h3>
              <p className="text-gray-600 mt-1">
                {data.city_distribution[0]?.city || '-'} ({data.city_distribution[0]?.count || 0}个职位)
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
