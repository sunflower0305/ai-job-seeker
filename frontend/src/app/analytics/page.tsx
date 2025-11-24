'use client';

import { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
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
  industry_distribution: Array<{ company__industry: string; count: number }>;
  skills_distribution: Array<{ skill: string; count: number }>;
  company_type_distribution: Array<{ company__company_type: string; count: number; avg_salary: number }>;
  company_size_distribution: Array<{ company__company_size: string; count: number; avg_salary: number }>;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658', '#FF6B9D', '#8DD1E1', '#D0ED57'];

export default function AnalyticsPage() {
  const [data, setData] = useState<StatisticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  useEffect(() => {
    fetchStatistics();
  }, []);

  const fetchStatistics = async (start = startDate, end = endDate) => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (start) params.append('start_date', start);
      if (end) params.append('end_date', end);
      const queryString = params.toString() ? `?${params.toString()}` : '';
      const url = `http://localhost:8000/api/jobs/jobs/statistics/${queryString}`;

      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch statistics');
      const result = await response.json();
      setData(result);
    } catch (err) {
      console.error('Error fetching statistics:', err);
      setError('无法加载统计数据');
    } finally {
      setLoading(false);
    }
  };

  const handleDateFilter = () => {
    fetchStatistics(startDate, endDate);
  };

  const handleResetFilter = () => {
    setStartDate('');
    setEndDate('');
    fetchStatistics('', '');
  };

  const exportToCSV = () => {
    if (!data) return;

    const csvData = [
      ['类别', '名称', '数量', '平均薪资'],
      ...data.city_distribution.map(item => ['城市', item.city, item.count, Math.round(item.avg_salary)]),
      ...data.education_distribution.map(item => ['学历', item.education, item.count, Math.round(item.avg_salary)]),
      ...data.experience_distribution.map(item => ['经验', item.experience, item.count, Math.round(item.avg_salary)]),
    ];

    const csv = csvData.map(row => row.join(',')).join('\n');
    const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `job_statistics_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 text-lg">{error || '数据加载失败'}</p>
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

  // 转换数据格式
  const salaryRangeData = Object.entries(data.salary_ranges).map(([range, count]) => ({
    range,
    count,
  }));

  const cityData = data.city_distribution.map(item => ({
    name: item.city,
    职位数: item.count,
    平均薪资: Math.round(item.avg_salary),
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

  const industryData = data.industry_distribution.map(item => ({
    name: item.company__industry || '未分类',
    value: item.count,
  }));

  const skillsData = data.skills_distribution.map(item => ({
    name: item.skill,
    需求数: item.count,
  }));

  const companyTypeData = data.company_type_distribution.map(item => ({
    name: item.company__company_type || '其他',
    职位数: item.count,
    平均薪资: Math.round(item.avg_salary),
  }));

  const companySizeData = data.company_size_distribution.map(item => ({
    name: item.company__company_size || '未知',
    职位数: item.count,
    平均薪资: Math.round(item.avg_salary),
  }));

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 标题和操作按钮 */}
        <div className="mb-8 flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">数据统计分析</h1>
            <p className="mt-2 text-gray-600">职位市场数据可视化与分析报告</p>
          </div>
          <button
            onClick={exportToCSV}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            导出数据
          </button>
        </div>

        {/* 日期筛选器 */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-lg font-bold text-gray-900 mb-4">数据筛选</h2>
          <div className="flex flex-wrap gap-4 items-end">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">开始日期</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">结束日期</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <button
              onClick={handleDateFilter}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              应用筛选
            </button>
            <button
              onClick={handleResetFilter}
              className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
            >
              重置
            </button>
          </div>
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

        {/* 图表区域 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 薪资区间分布 */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">薪资区间分布</h2>
            <ResponsiveContainer width="100%" height={300}>
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

          {/* 城市职位分布 */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">城市职位分布 Top 10</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={cityData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" width={60} />
                <Tooltip />
                <Legend />
                <Bar dataKey="职位数" fill="#10B981" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* 学历要求分布 */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">学历要求与薪资</h2>
            <ResponsiveContainer width="100%" height={300}>
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
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">工作经验与薪资关系</h2>
            <ResponsiveContainer width="100%" height={300}>
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

          {/* 行业分布饼图 */}
          <div className="bg-white rounded-lg shadow p-6 lg:col-span-2">
            <h2 className="text-lg font-bold text-gray-900 mb-4">行业分布 Top 10</h2>
            <ResponsiveContainer width="100%" height={400}>
              <PieChart>
                <Pie
                  data={industryData}
                  cx="50%"
                  cy="50%"
                  labelLine={true}
                  label={({ name, percent }) => `${name} (${percent ? (percent * 100).toFixed(0) : 0}%)`}
                  outerRadius={120}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {industryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* 城市平均薪资对比 */}
          <div className="bg-white rounded-lg shadow p-6 lg:col-span-2">
            <h2 className="text-lg font-bold text-gray-900 mb-4">各城市平均薪资对比</h2>
            <ResponsiveContainer width="100%" height={300}>
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

          {/* 技能需求统计 Top 20 */}
          <div className="bg-white rounded-lg shadow p-6 lg:col-span-2">
            <h2 className="text-lg font-bold text-gray-900 mb-4">技能需求 Top 20</h2>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={skillsData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" width={100} />
                <Tooltip />
                <Legend />
                <Bar dataKey="需求数" fill="#8B5CF6" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* 公司类型分布 */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">公司类型分布</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={companyTypeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis yAxisId="left" orientation="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Legend />
                <Bar yAxisId="left" dataKey="职位数" fill="#10B981" name="职位数" />
                <Bar yAxisId="right" dataKey="平均薪资" fill="#F59E0B" name="平均薪资(元)" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* 公司规模分布 */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">公司规模分布</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={companySizeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis yAxisId="left" orientation="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Legend />
                <Bar yAxisId="left" dataKey="职位数" fill="#3B82F6" name="职位数" />
                <Bar yAxisId="right" dataKey="平均薪资" fill="#EF4444" name="平均薪资(元)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 数据洞察 */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">数据洞察</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="border-l-4 border-blue-500 pl-4">
              <h3 className="font-semibold text-gray-900">最热门城市</h3>
              <p className="text-gray-600 mt-1">
                {cityData[0]?.name || '-'} ({cityData[0]?.职位数 || 0}个职位)
              </p>
            </div>
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
              <h3 className="font-semibold text-gray-900">主要行业</h3>
              <p className="text-gray-600 mt-1">
                {industryData[0]?.name || '-'} ({industryData[0]?.value || 0}个职位)
              </p>
            </div>
            <div className="border-l-4 border-yellow-500 pl-4">
              <h3 className="font-semibold text-gray-900">最热门技能</h3>
              <p className="text-gray-600 mt-1">
                {skillsData[0]?.name || '-'} ({skillsData[0]?.需求数 || 0}个职位)
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
