'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
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
  basic_stats: {
    total_companies: number;
    total_jobs: number;
  };
  company_type_distribution: Array<{ company__company_type: string | null; count: number; avg_salary: number }>;
  company_size_distribution: Array<{ company__company_size: string | null; count: number; avg_salary: number }>;
  industry_distribution: Array<{ company__industry: string | null; count: number }>;
}

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'];

export default function CompanyAnalyticsPage() {
  const [data, setData] = useState<StatisticsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStatistics();
  }, []);

  const fetchStatistics = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/jobs/jobs/statistics/');
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

  // 公司类型数据
  const companyTypeData = data.company_type_distribution
    .filter(item => item.company__company_type)
    .map(item => ({
      name: item.company__company_type || '未知',
      职位数: item.count,
      平均薪资: Math.round(item.avg_salary),
    }));

  // 公司规模数据
  const companySizeData = data.company_size_distribution
    .filter(item => item.company__company_size)
    .map(item => ({
      name: item.company__company_size || '未知',
      职位数: item.count,
      平均薪资: Math.round(item.avg_salary),
    }));

  // 行业分布数据
  const industryData = data.industry_distribution
    .filter(item => item.company__industry)
    .slice(0, 10)
    .map(item => ({
      name: item.company__industry || '未知',
      职位数: item.count,
    }));

  // 公司类型饼图数据
  const companyTypePieData = data.company_type_distribution
    .filter(item => item.company__company_type)
    .map(item => ({
      name: item.company__company_type || '未知',
      value: item.count,
    }));

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 面包屑导航 */}
        <div className="mb-6 flex items-center text-sm text-gray-600">
          <Link href="/analytics" className="hover:text-blue-600">数据分析</Link>
          <span className="mx-2">/</span>
          <span className="text-gray-900">公司分析</span>
        </div>

        {/* 标题 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">公司分析</h1>
          <p className="mt-2 text-gray-600">企业类型、规模与行业分布分析</p>
        </div>

        {/* 统计卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-blue-100 rounded-lg p-3">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
              <div className="flex-shrink-0 bg-green-100 rounded-lg p-3">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
              <div className="flex-shrink-0 bg-purple-100 rounded-lg p-3">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">行业类型</p>
                <p className="text-2xl font-bold text-gray-900">{data.industry_distribution.length}</p>
              </div>
            </div>
          </div>
        </div>

        {/* 图表区域 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 公司类型分布 */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">公司类型分布</h2>
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={companyTypeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis yAxisId="left" orientation="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Legend />
                <Bar yAxisId="left" dataKey="职位数" fill="#3B82F6" />
                <Bar yAxisId="right" dataKey="平均薪资" fill="#10B981" name="平均薪资(元)" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* 公司类型占比饼图 */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">公司类型职位占比</h2>
            <ResponsiveContainer width="100%" height={350}>
              <PieChart>
                <Pie
                  data={companyTypePieData}
                  cx="50%"
                  cy="50%"
                  labelLine={true}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(1)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {companyTypePieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* 公司规模分布 */}
          <div className="bg-white rounded-lg shadow p-6 lg:col-span-2">
            <h2 className="text-lg font-bold text-gray-900 mb-4">公司规模与薪资</h2>
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={companySizeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis yAxisId="left" orientation="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Legend />
                <Bar yAxisId="left" dataKey="职位数" fill="#8B5CF6" />
                <Bar yAxisId="right" dataKey="平均薪资" fill="#F59E0B" name="平均薪资(元)" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* 行业分布 Top 10 */}
          <div className="bg-white rounded-lg shadow p-6 lg:col-span-2">
            <h2 className="text-lg font-bold text-gray-900 mb-4">热门行业 Top 10</h2>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={industryData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" width={150} />
                <Tooltip />
                <Legend />
                <Bar dataKey="职位数" fill="#06B6D4" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* 公司类型排行 */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">公司类型排行</h2>
            <div className="space-y-3 max-h-[400px] overflow-y-auto">
              {data.company_type_distribution
                .filter(item => item.company__company_type)
                .map((item, index) => (
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
                      <span className="font-medium text-gray-900">{item.company__company_type}</span>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-gray-500">职位: {item.count}</div>
                      <div className="text-sm text-green-600 font-medium">薪资: {Math.round(item.avg_salary)}元</div>
                    </div>
                  </div>
                ))}
            </div>
          </div>

          {/* 公司规模排行 */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">公司规模排行</h2>
            <div className="space-y-3 max-h-[400px] overflow-y-auto">
              {data.company_size_distribution
                .filter(item => item.company__company_size)
                .map((item, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                    <div className="flex items-center gap-3">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                        index === 0 ? 'bg-yellow-400 text-white' :
                        index === 1 ? 'bg-gray-300 text-gray-800' :
                        index === 2 ? 'bg-orange-400 text-white' :
                        'bg-purple-100 text-purple-700'
                      }`}>
                        {index + 1}
                      </div>
                      <span className="font-medium text-gray-900">{item.company__company_size}</span>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-gray-500">职位: {item.count}</div>
                      <div className="text-sm text-green-600 font-medium">薪资: {Math.round(item.avg_salary)}元</div>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>

        {/* 公司洞察 */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">公司洞察</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="border-l-4 border-blue-500 pl-4">
              <h3 className="font-semibold text-gray-900">最活跃公司类型</h3>
              <p className="text-gray-600 mt-1">
                {(() => {
                  const mostActive = data.company_type_distribution
                    .filter(item => item.company__company_type)
                    .sort((a, b) => b.count - a.count)[0];
                  return mostActive ? `${mostActive.company__company_type} (${mostActive.count}个职位)` : '暂无数据';
                })()}
              </p>
            </div>
            <div className="border-l-4 border-green-500 pl-4">
              <h3 className="font-semibold text-gray-900">薪资最高规模</h3>
              <p className="text-gray-600 mt-1">
                {(() => {
                  const highestSalary = data.company_size_distribution
                    .filter(item => item.company__company_size)
                    .sort((a, b) => b.avg_salary - a.avg_salary)[0];
                  return highestSalary ? `${highestSalary.company__company_size} (${Math.round(highestSalary.avg_salary)}元)` : '暂无数据';
                })()}
              </p>
            </div>
            <div className="border-l-4 border-purple-500 pl-4">
              <h3 className="font-semibold text-gray-900">最热门行业</h3>
              <p className="text-gray-600 mt-1">
                {(() => {
                  const topIndustry = data.industry_distribution
                    .filter(item => item.company__industry)
                    .sort((a, b) => b.count - a.count)[0];
                  return topIndustry ? `${topIndustry.company__industry} (${topIndustry.count}个职位)` : '暂无数据';
                })()}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
