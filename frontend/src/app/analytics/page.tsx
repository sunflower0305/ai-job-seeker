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
  basic_stats: {
    total_jobs: number;
    total_companies: number;
  };
  salary_stats: {
    average: number;
    min: number;
    max: number;
  };
  salary_ranges: Record<string, number>;
  city_distribution: Array<{ city: string; count: number; avg_salary: number }>;
  education_distribution: Array<{ education: string; count: number; avg_salary: number }>;
  experience_distribution: Array<{ experience: string; count: number; avg_salary: number }>;
  industry_distribution: Array<{ company__industry: string | null; count: number }>;
  skills_distribution: Array<{ skill: string; count: number }>;
  company_type_distribution: Array<{ company__company_type: string | null; count: number; avg_salary: number }>;
  company_size_distribution: Array<{ company__company_size: string | null; count: number; avg_salary: number }>;
}

export default function AnalyticsPage() {
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

  const cityData = data.city_distribution.slice(0, 8).map(item => ({
    name: item.city,
    职位数: item.count,
  }));

  const skillsData = data.skills_distribution.slice(0, 10).map(item => ({
    name: item.skill,
    需求数: item.count,
  }));

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 标题 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">数据分析概览</h1>
          <p className="mt-2 text-gray-600">职位市场数据统计与趋势分析</p>
        </div>

        {/* 基础统计卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-blue-100 rounded-lg p-3">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">职位总数</p>
                <p className="text-2xl font-bold text-gray-900">{data.basic_stats.total_jobs}</p>
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
                <p className="text-sm font-medium text-gray-600">公司总数</p>
                <p className="text-2xl font-bold text-gray-900">{data.basic_stats.total_companies}</p>
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
                <p className="text-sm font-medium text-gray-600">平均薪资</p>
                <p className="text-2xl font-bold text-gray-900">{Math.round(data.salary_stats.average)}元</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-purple-100 rounded-lg p-3">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">薪资范围</p>
                <p className="text-xl font-bold text-gray-900">
                  {Math.round(data.salary_stats.min / 1000)}k-{Math.round(data.salary_stats.max / 1000)}k
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* 分析模块导航卡片 */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">详细分析</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* 薪资分析 */}
            <Link href="/analytics/salary" className="group">
              <div className="bg-white rounded-lg shadow hover:shadow-xl transition-all p-6 h-full border-2 border-transparent hover:border-blue-500">
                <div className="flex items-center justify-between mb-4">
                  <div className="bg-yellow-100 rounded-lg p-3">
                    <svg className="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <svg className="w-5 h-5 text-gray-400 group-hover:text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">薪资分析</h3>
                <p className="text-gray-600 text-sm">薪资区间、学历要求、经验与薪资关系等深度分析</p>
              </div>
            </Link>

            {/* 技能词云 */}
            <Link href="/analytics/wordcloud" className="group">
              <div className="bg-white rounded-lg shadow hover:shadow-xl transition-all p-6 h-full border-2 border-transparent hover:border-blue-500">
                <div className="flex items-center justify-between mb-4">
                  <div className="bg-blue-100 rounded-lg p-3">
                    <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                    </svg>
                  </div>
                  <svg className="w-5 h-5 text-gray-400 group-hover:text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">技能词云</h3>
                <p className="text-gray-600 text-sm">热门技能需求词云图、技能排行榜与技能分布</p>
              </div>
            </Link>

            {/* 城市分析 */}
            <Link href="/analytics/city" className="group">
              <div className="bg-white rounded-lg shadow hover:shadow-xl transition-all p-6 h-full border-2 border-transparent hover:border-blue-500">
                <div className="flex items-center justify-between mb-4">
                  <div className="bg-green-100 rounded-lg p-3">
                    <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  </div>
                  <svg className="w-5 h-5 text-gray-400 group-hover:text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">城市分析</h3>
                <p className="text-gray-600 text-sm">各城市职位分布、薪资水平与就业机会分析</p>
              </div>
            </Link>

            {/* 公司分析 */}
            <Link href="/analytics/company" className="group">
              <div className="bg-white rounded-lg shadow hover:shadow-xl transition-all p-6 h-full border-2 border-transparent hover:border-blue-500">
                <div className="flex items-center justify-between mb-4">
                  <div className="bg-purple-100 rounded-lg p-3">
                    <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                  </div>
                  <svg className="w-5 h-5 text-gray-400 group-hover:text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">公司分析</h3>
                <p className="text-gray-600 text-sm">企业类型、规模、行业分布与薪资水平分析</p>
              </div>
            </Link>
          </div>
        </div>

        {/* 快速概览图表 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 城市职位分布预览 */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-bold text-gray-900">城市职位分布 Top 8</h2>
              <Link href="/analytics/city" className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                查看详情 →
              </Link>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={cityData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="职位数" fill="#10B981" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* 热门技能预览 */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-bold text-gray-900">热门技能 Top 10</h2>
              <Link href="/analytics/wordcloud" className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                查看详情 →
              </Link>
            </div>
            <ResponsiveContainer width="100%" height={300}>
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
        </div>

        {/* 数据洞察 */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">核心数据洞察</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="border-l-4 border-blue-500 pl-4">
              <h3 className="font-semibold text-gray-900">最热门城市</h3>
              <p className="text-gray-600 mt-1">
                {data.city_distribution[0]?.city || '-'} ({data.city_distribution[0]?.count || 0}个职位)
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
              <h3 className="font-semibold text-gray-900">主要行业</h3>
              <p className="text-gray-600 mt-1">
                {(() => {
                  const topIndustry = data.industry_distribution
                    .filter(item => item.company__industry)
                    .sort((a, b) => b.count - a.count)[0];
                  return topIndustry ? `${topIndustry.company__industry} (${topIndustry.count}个职位)` : '暂无数据';
                })()}
              </p>
            </div>
            <div className="border-l-4 border-yellow-500 pl-4">
              <h3 className="font-semibold text-gray-900">最热门技能</h3>
              <p className="text-gray-600 mt-1">
                {data.skills_distribution[0]?.skill || '-'} ({data.skills_distribution[0]?.count || 0}个职位)
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
