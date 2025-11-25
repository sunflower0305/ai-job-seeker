'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Job, ApiResponse } from '@/types';
import { api } from '@/lib/api';
import Pagination from '@/components/Pagination';

export default function JobsPage() {
  const searchParams = useSearchParams();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchKeyword, setSearchKeyword] = useState(searchParams.get('search') || '');
  const [sortBy, setSortBy] = useState<'default' | 'latest'>('default');
  const [filters, setFilters] = useState({
    location: '',
    experience: '',
    education: '',
  });

  useEffect(() => {
    fetchJobs();
  }, [currentPage, pageSize, sortBy]);

  const fetchJobs = async () => {
    try {
      setLoading(true);
      setError('');

      const params: Record<string, string> = {
        page: currentPage.toString(),
        page_size: pageSize.toString(),
      };
      if (searchKeyword) params.search = searchKeyword;
      if (filters.location) params.city = filters.location; // 修改为city参数
      if (filters.experience) params.experience = filters.experience;
      if (filters.education) params.education = filters.education;

      // 添加排序参数
      if (sortBy === 'latest') {
        params.ordering = '-created_at'; // 按创建时间倒序
      } else {
        params.ordering = '-salary_max'; // 综合排序：按最高薪资倒序
      }

      const data = await api.jobs.list(params) as ApiResponse<Job>;

      // 直接使用API返回的数据
      setJobs(data.results || []);
      setTotalCount(data.count || 0);

      // 如果没有数据，显示提示信息
      if (!data.results || data.results.length === 0) {
        setError('暂无符合条件的职位，请尝试修改筛选条件');
      }
    } catch (err) {
      console.error('获取职位失败:', err);
      setError('获取职位数据失败，请检查网络连接或稍后重试');
      setJobs([]);
      setTotalCount(0);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1); // 重置到第一页
    fetchJobs();
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handlePageSizeChange = (newPageSize: number) => {
    setPageSize(newPageSize);
    setCurrentPage(1); // 重置到第一页
  };

  const handleSortChange = (newSortBy: 'default' | 'latest') => {
    setSortBy(newSortBy);
    setCurrentPage(1); // 重置到第一页
  };

  const totalPages = Math.ceil(totalCount / pageSize);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 搜索和筛选区域 */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <form onSubmit={handleSearch} className="space-y-4">
            {/* 搜索框 */}
            <div className="flex gap-4">
              <input
                type="text"
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
                placeholder="搜索职位名称或公司..."
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                type="submit"
                className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
              >
                搜索
              </button>
            </div>

            {/* 筛选条件 */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <select
                value={filters.location}
                onChange={(e) => setFilters({ ...filters, location: e.target.value })}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">所有地区</option>
                <option value="重庆">重庆</option>
                <option value="上海">上海</option>
                <option value="北京">北京</option>
                <option value="成都">成都</option>
                <option value="南京">南京</option>
                <option value="深圳">深圳</option>
                <option value="广州">广州</option>
                <option value="西安">西安</option>
                <option value="武汉">武汉</option>
                <option value="杭州">杭州</option>
              </select>

              <select
                value={filters.experience}
                onChange={(e) => setFilters({ ...filters, experience: e.target.value })}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">工作经验</option>
                <option value="不限">不限</option>
                <option value="1-3年">1-3年</option>
                <option value="3-5年">3-5年</option>
                <option value="5-10年">5-10年</option>
                <option value="10年以上">10年以上</option>
              </select>

              <select
                value={filters.education}
                onChange={(e) => setFilters({ ...filters, education: e.target.value })}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">学历要求</option>
                <option value="不限">不限</option>
                <option value="大专">大专</option>
                <option value="本科">本科</option>
                <option value="硕士">硕士</option>
                <option value="博士">博士</option>
              </select>
            </div>
          </form>

          {error && (
            <div className={`mt-4 p-3 border rounded-lg flex items-start ${
              error.includes('失败') || error.includes('网络')
                ? 'bg-red-50 border-red-200'
                : 'bg-yellow-50 border-yellow-200'
            }`}>
              <svg className={`w-5 h-5 mr-2 mt-0.5 ${
                error.includes('失败') || error.includes('网络')
                  ? 'text-red-600'
                  : 'text-yellow-600'
              }`} fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
              <div>
                <p className={`font-medium ${
                  error.includes('失败') || error.includes('网络')
                    ? 'text-red-800'
                    : 'text-yellow-800'
                }`}>{error}</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 职位列表 */}
      <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">
            {loading ? '加载中...' : `共找到 ${totalCount} 个职位`}
          </h2>
          <div className="flex gap-2">
            <button
              onClick={() => handleSortChange('default')}
              className={`px-4 py-2 text-sm border rounded-lg transition-colors ${
                sortBy === 'default'
                  ? 'border-blue-500 bg-blue-50 text-blue-700 font-medium'
                  : 'border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              综合排序
            </button>
            <button
              onClick={() => handleSortChange('latest')}
              className={`px-4 py-2 text-sm border rounded-lg transition-colors ${
                sortBy === 'latest'
                  ? 'border-blue-500 bg-blue-50 text-blue-700 font-medium'
                  : 'border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              最新发布
            </button>
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : jobs.length > 0 ? (
          <div className="grid gap-4">
            {jobs.map((job) => (
              <div
                key={job.id}
                className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <Link href={`/jobs/${job.id}`}>
                      <h3 className="text-xl font-bold text-gray-900 hover:text-blue-600 cursor-pointer">
                        {job.title}
                      </h3>
                    </Link>
                    <div className="mt-2 flex flex-wrap gap-4 text-sm text-gray-600">
                      <span className="flex items-center">
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                        </svg>
                        {job.company_name || (typeof job.company === 'object' ? job.company.name : job.company) || '未知公司'}
                      </span>
                      <span className="flex items-center">
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                        {job.city || job.location || '未知地点'}
                      </span>
                      <span className="flex items-center">
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                        {job.experience || '经验不限'}
                      </span>
                      <span className="flex items-center">
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                        </svg>
                        {job.education || '学历不限'}
                      </span>
                    </div>
                    {job.description && (
                      <p className="mt-3 text-gray-600 line-clamp-2">{job.description}</p>
                    )}
                  </div>
                  <div className="ml-6 text-right">
                    <div className="text-2xl font-bold text-orange-600">
                      {job.salary ||
                        (job.salary_min && job.salary_max
                          ? `${(job.salary_min / 1000).toFixed(0)}k-${(job.salary_max / 1000).toFixed(0)}k`
                          : '薪资面议')}
                    </div>
                    <div className="mt-4 flex gap-2">
                      <button className="px-4 py-2 text-sm text-gray-700 border border-gray-300 rounded hover:bg-gray-50">
                        收藏
                      </button>
                      <button className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700">
                        投递
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 bg-white rounded-lg">
            <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M12 12h.01M12 12h.01M12 12h.01M12 12h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-gray-500 text-lg">暂无符合条件的职位</p>
            <p className="text-gray-400 mt-2">试试修改筛选条件或搜索关键词</p>
          </div>
        )}

        {/* 分页控制 */}
        {!loading && jobs.length > 0 && totalCount > 0 && (
          <div className="mt-8">
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              totalCount={totalCount}
              pageSize={pageSize}
              onPageChange={handlePageChange}
              onPageSizeChange={handlePageSizeChange}
            />
          </div>
        )}
      </div>
    </div>
  );
}
