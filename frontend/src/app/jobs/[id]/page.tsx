'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Job } from '@/types';
import { apiUrl } from '@/lib/api';

export default function JobDetailPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = params.id as string;
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [isCollected, setIsCollected] = useState(false);
  const [similarJobs, setSimilarJobs] = useState<Job[]>([]);
  const [similarJobsLoading, setSimilarJobsLoading] = useState(false);

  useEffect(() => {
    fetchJobDetail();
    fetchSimilarJobs();
  }, [jobId]);

  const fetchJobDetail = async () => {
    try {
      setLoading(true);
      const response = await fetch(apiUrl(`/api/jobs/jobs/${jobId}/`));

      if (response.ok) {
        const data = await response.json();
        setJob(data);

        // 检查是否已收藏（需要登录）
        const token = localStorage.getItem('token');
        if (token) {
          const collectResponse = await fetch(apiUrl(`/api/jobs/collections/?job=${jobId}`), {
            headers: {
              'Authorization': `Token ${token}`,
            },
          });
          if (collectResponse.ok) {
            const collectData = await collectResponse.json();
            setIsCollected(collectData.results && collectData.results.length > 0);
          }
        }
      } else {
        console.error('获取职位详情失败');
      }
    } catch (err) {
      console.error('获取职位详情失败:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchSimilarJobs = async () => {
    try {
      setSimilarJobsLoading(true);
      const response = await fetch(apiUrl(`/api/jobs/jobs/${jobId}/similar/?top_n=3`));

      if (response.ok) {
        const data = await response.json();
        setSimilarJobs(data.results || []);
      } else {
        console.error('获取相似职位失败');
      }
    } catch (err) {
      console.error('获取相似职位失败:', err);
    } finally {
      setSimilarJobsLoading(false);
    }
  };

  const handleCollect = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      alert('请先登录');
      router.push('/login');
      return;
    }

    try {
      const method = isCollected ? 'DELETE' : 'POST';
      const response = await fetch(apiUrl(`/api/jobs/jobs/${jobId}/collect/`), {
        method: method,
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        setIsCollected(!isCollected);
        const data = await response.json();
        alert(data.message);
      } else {
        alert('操作失败，请重试');
      }
    } catch (error) {
      console.error('收藏操作失败:', error);
      alert('操作失败，请重试');
    }
  };


  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">职位不存在</h2>
          <Link href="/jobs" className="text-blue-600 hover:text-blue-700">
            返回职位列表
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <Link href="/jobs" className="text-blue-600 hover:text-blue-700 flex items-center">
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              返回列表
            </Link>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Job Header */}
            <div className="bg-white rounded-lg shadow-md p-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-4">{job.title}</h1>
              <div className="flex items-center justify-between mb-6">
                <div className="text-3xl font-bold text-orange-600">
                  {job.salary_min && job.salary_max
                    ? `${(job.salary_min / 1000).toFixed(0)}k-${(job.salary_max / 1000).toFixed(0)}k`
                    : '薪资面议'}
                </div>
                <button
                  onClick={handleCollect}
                  className={`flex items-center gap-2 px-6 py-3 border-2 rounded-lg font-medium transition-all ${
                    isCollected
                      ? 'border-yellow-500 bg-yellow-50 text-yellow-700 hover:bg-yellow-100'
                      : 'border-gray-300 text-gray-700 hover:border-yellow-500 hover:bg-yellow-50'
                  }`}
                >
                  <svg className="w-5 h-5" fill={isCollected ? "currentColor" : "none"} stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                  </svg>
                  {isCollected ? '已收藏' : '收藏职位'}
                </button>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-gray-50 rounded-lg">
                <div>
                  <div className="text-sm text-gray-600 mb-1">工作经验</div>
                  <div className="font-medium text-gray-900">{job.experience || '不限'}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600 mb-1">学历要求</div>
                  <div className="font-medium text-gray-900">{job.education || '不限'}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600 mb-1">工作地点</div>
                  <div className="font-medium text-gray-900">{job.city || job.location || '不限'}</div>
                </div>
                {job.district && (
                  <div>
                    <div className="text-sm text-gray-600 mb-1">区域</div>
                    <div className="font-medium text-gray-900">{job.district}</div>
                  </div>
                )}
              </div>
            </div>

            {/* Job Description */}
            {job.description && (
              <div className="bg-white rounded-lg shadow-md p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">职位描述</h2>
                <p className="text-gray-700 leading-relaxed whitespace-pre-line">
                  {job.description}
                </p>
              </div>
            )}

            {/* Job Requirements */}
            {job.requirements && (
              <div className="bg-white rounded-lg shadow-md p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">任职要求</h2>
                <div className="text-gray-700 leading-relaxed whitespace-pre-line">
                  {job.requirements}
                </div>
              </div>
            )}

            {/* Welfare */}
            {job.welfare && (
              <div className="bg-white rounded-lg shadow-md p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">福利待遇</h2>
                <div className="text-gray-700 leading-relaxed whitespace-pre-line">
                  {job.welfare}
                </div>
              </div>
            )}

            {/* Tags */}
            {job.tags && job.tags.length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">技能标签</h2>
                <div className="flex flex-wrap gap-2">
                  {job.tags.map((tag, index) => (
                    <span key={index} className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="sticky top-24 space-y-6">
              {/* Company Info */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-xl font-bold text-gray-900 mb-4">公司信息</h3>
                <div className="space-y-4">
                  <div>
                    <div className="text-sm text-gray-600 mb-1">公司名称</div>
                    <div className="font-medium text-gray-900">
                      {typeof job.company === 'object' ? job.company.name : job.company}
                    </div>
                  </div>
                  {job.company && typeof job.company === 'object' && (
                    <>
                      {job.company.industry && (
                        <div>
                          <div className="text-sm text-gray-600 mb-1">行业</div>
                          <div className="font-medium text-gray-900">{job.company.industry}</div>
                        </div>
                      )}
                      {job.company.company_type && (
                        <div>
                          <div className="text-sm text-gray-600 mb-1">公司类型</div>
                          <div className="font-medium text-gray-900">{job.company.company_type}</div>
                        </div>
                      )}
                      {job.company.company_size && (
                        <div>
                          <div className="text-sm text-gray-600 mb-1">公司规模</div>
                          <div className="font-medium text-gray-900">{job.company.company_size}</div>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>

              {/* Similar Jobs */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-xl font-bold text-gray-900 mb-4">相似职位</h3>
                {similarJobsLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  </div>
                ) : similarJobs.length > 0 ? (
                  <div className="space-y-4">
                    {similarJobs.map((similarJob) => (
                      <Link
                        key={similarJob.id}
                        href={`/jobs/${similarJob.id}`}
                        className="block p-3 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition-all"
                      >
                        <h4 className="font-medium text-gray-900 mb-1">{similarJob.title}</h4>
                        <p className="text-sm text-gray-600">
                          {typeof similarJob.company === 'object' ? similarJob.company.name : similarJob.company}
                          {' · '}
                          {similarJob.salary_min && similarJob.salary_max
                            ? `${(similarJob.salary_min / 1000).toFixed(0)}k-${(similarJob.salary_max / 1000).toFixed(0)}k`
                            : '薪资面议'}
                        </p>
                      </Link>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">暂无相似职位</p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
