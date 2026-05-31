'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { apiUrl } from '@/lib/api';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface StatisticsData {
  basic_stats: {
    total_jobs: number;
  };
  salary_stats: {
    average: number;
    min: number;
    max: number;
  };
  salary_ranges: Record<string, number>;
  education_distribution: Array<{ education: string; count: number; avg_salary: number }>;
  experience_distribution: Array<{ experience: string; count: number; avg_salary: number }>;
  city_distribution: Array<{ city: string; count: number; avg_salary: number }>;
}

export default function SalaryAnalyticsPage() {
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

  const salaryRangeData = Object.entries(data.salary_ranges).map(([range, count]) => ({
    range,
    count,
  }));

  const educationData = data.education_distribution.map(item => ({
    name: item.education,
    职位数: item.count,
    平均薪资: Math.round(item.avg_salary),
  }));

  const experienceData = data.experience_distribution.map(item => ({
    name: item.experience,
    职位数: item.count,
    平均薪资: Math.round(item.avg_salary),
  }));

  const cityData = data.city_distribution.map(item => ({
    name: item.city,
    平均薪资: Math.round(item.avg_salary),
  }));

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 面包屑导航 */}
        <div className="mb-6 flex items-center text-sm text-gray-600">
          <Link href="/analytics" className="hover:text-blue-600">数据分析</Link>
          <span className="mx-2">/</span>
          <span className="text-gray-900">薪资分析</span>
        </div>

        {/* 标题 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">薪资分析</h1>
          <p className="mt-2 text-gray-600">职位薪资数据统计与趋势分析</p>
        </div>

        {/* 统计卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-yellow-100 rounded-lg p-3">
                <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">平均薪资</p>
                <p className="text-2xl font-bold text-gray-900">{Math.round(data.salary_stats.average)}元</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-green-100 rounded-lg p-3">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">最高薪资</p>
                <p className="text-2xl font-bold text-gray-900">{Math.round(data.salary_stats.max / 1000)}k</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-blue-100 rounded-lg p-3">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">最低薪资</p>
                <p className="text-2xl font-bold text-gray-900">{Math.round(data.salary_stats.min / 1000)}k</p>
              </div>
            </div>
          </div>
        </div>

        {/* 图表区域 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 薪资区间分布 */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">薪资区间分布</h2>
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={salaryRangeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="range" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#3B82F6" name="职位数" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* 学历与薪资 */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">学历要求与薪资</h2>
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={educationData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis yAxisId="left" orientation="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Legend />
                <Bar yAxisId="left" dataKey="职位数" fill="#8B5CF6" name="职位数" />
                <Bar yAxisId="right" dataKey="平均薪资" fill="#F59E0B" name="平均薪资(元)" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* 工作经验与薪资 */}
          <div className="bg-white rounded-lg shadow p-6 lg:col-span-2">
            <h2 className="text-lg font-bold text-gray-900 mb-4">工作经验与薪资关系</h2>
            <ResponsiveContainer width="100%" height={350}>
              <LineChart data={experienceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis yAxisId="left" orientation="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Legend />
                <Line yAxisId="left" type="monotone" dataKey="职位数" stroke="#3B82F6" strokeWidth={2} name="职位数" />
                <Line yAxisId="right" type="monotone" dataKey="平均薪资" stroke="#EF4444" strokeWidth={2} name="平均薪资(元)" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* 城市薪资对比 */}
          <div className="bg-white rounded-lg shadow p-6 lg:col-span-2">
            <h2 className="text-lg font-bold text-gray-900 mb-4">各城市平均薪资对比 Top 10</h2>
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={cityData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="平均薪资" fill="#06B6D4" name="平均薪资(元)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 数据洞察 */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">薪资洞察</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="border-l-4 border-green-500 pl-4">
              <h3 className="font-semibold text-gray-900">薪资最高城市</h3>
              <p className="text-gray-600 mt-1">
                {(() => {
                  const sortedCities = [...cityData].sort((a, b) => b.平均薪资 - a.平均薪资);
                  return `${sortedCities[0]?.name || '-'} (${sortedCities[0]?.平均薪资 || 0}元)`;
                })()}
              </p>
            </div>
            <div className="border-l-4 border-purple-500 pl-4">
              <h3 className="font-semibold text-gray-900">经验薪资涨幅</h3>
              <p className="text-gray-600 mt-1">
                {(() => {
                  if (experienceData.length >= 2) {
                    const lowest = experienceData[0]?.平均薪资 || 0;
                    const highest = experienceData[experienceData.length - 1]?.平均薪资 || 0;
                    const increase = ((highest - lowest) / lowest * 100).toFixed(1);
                    return `从入门到资深薪资涨幅约 ${increase}%`;
                  }
                  return '数据不足';
                })()}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
