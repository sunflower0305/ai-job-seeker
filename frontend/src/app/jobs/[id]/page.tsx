'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Job } from '@/types';

export default function JobDetailPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = params.id as string;
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [isCollected, setIsCollected] = useState(false);
  const [isApplied, setIsApplied] = useState(false);

  useEffect(() => {
    fetchJobDetail();
  }, [jobId]);

  const fetchJobDetail = async () => {
    try {
      setLoading(true);
      // TODO: 集成真实API
      await new Promise(resolve => setTimeout(resolve, 800));

      // 使用模拟数据
      const mockJob: Job = {
        id: parseInt(jobId),
        title: 'React前端工程师',
        company: '字节跳动',
        location: '北京-朝阳区',
        salary: '25k-40k',
        salary_min: 25000,
        salary_max: 40000,
        experience: '3-5年',
        education: '本科',
        job_type: '全职',
        description: '我们正在寻找一位富有激情的React前端工程师加入我们的团队。',
        requirements: `1. 精通React、TypeScript、Next.js等前端技术栈
2. 熟悉前端工程化、模块化开发
3. 熟悉常用的前端框架和库，如Redux、MobX等
4. 具有良好的代码习惯和团队协作精神
5. 有大型项目开发经验者优先`,
        responsibilities: `1. 负责公司核心产品的前端开发工作
2. 参与产品需求讨论，提供专业的技术方案
3. 优化前端性能，提升用户体验
4. 编写高质量、可维护的代码
5. 参与技术分享，提升团队整体技术水平`,
        benefits: `1. 五险一金，补充商业保险
2. 弹性工作时间，远程办公
3. 15天带薪年假，节日福利
4. 定期团建活动
5. 完善的培训体系和晋升通道
6. 免费三餐、下午茶、健身房
7. 年度体检`,
        publish_date: '2024-01-15',
      };

      setJob(mockJob);
    } catch (err) {
      console.error('获取职位详情失败:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCollect = () => {
    setIsCollected(!isCollected);
    // TODO: 调用收藏API
  };

  const handleApply = () => {
    setIsApplied(true);
    // TODO: 调用投递API
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
                <div className="text-3xl font-bold text-orange-600">{job.salary}</div>
                <div className="flex gap-3">
                  <button
                    onClick={handleCollect}
                    className={`px-6 py-3 border rounded-lg font-medium transition-all ${
                      isCollected
                        ? 'border-yellow-500 bg-yellow-50 text-yellow-700'
                        : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    {isCollected ? '已收藏' : '收藏'}
                  </button>
                  <button
                    onClick={handleApply}
                    disabled={isApplied}
                    className={`px-8 py-3 rounded-lg font-medium transition-all ${
                      isApplied
                        ? 'bg-green-600 text-white cursor-not-allowed'
                        : 'bg-blue-600 hover:bg-blue-700 text-white'
                    }`}
                  >
                    {isApplied ? '已投递' : '立即投递'}
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-gray-50 rounded-lg">
                <div>
                  <div className="text-sm text-gray-600 mb-1">工作经验</div>
                  <div className="font-medium text-gray-900">{job.experience}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600 mb-1">学历要求</div>
                  <div className="font-medium text-gray-900">{job.education}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600 mb-1">工作类型</div>
                  <div className="font-medium text-gray-900">{job.job_type}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600 mb-1">工作地点</div>
                  <div className="font-medium text-gray-900">{job.location}</div>
                </div>
              </div>
            </div>

            {/* Job Description */}
            <div className="bg-white rounded-lg shadow-md p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">职位描述</h2>
              <p className="text-gray-700 leading-relaxed whitespace-pre-line">
                {job.description}
              </p>
            </div>

            {/* Job Requirements */}
            <div className="bg-white rounded-lg shadow-md p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">任职要求</h2>
              <div className="text-gray-700 leading-relaxed whitespace-pre-line">
                {job.requirements}
              </div>
            </div>

            {/* Responsibilities */}
            <div className="bg-white rounded-lg shadow-md p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">岗位职责</h2>
              <div className="text-gray-700 leading-relaxed whitespace-pre-line">
                {job.responsibilities}
              </div>
            </div>

            {/* Benefits */}
            <div className="bg-white rounded-lg shadow-md p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">福利待遇</h2>
              <div className="text-gray-700 leading-relaxed whitespace-pre-line">
                {job.benefits}
              </div>
            </div>
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
                    <div className="font-medium text-gray-900">{job.company}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600 mb-1">行业</div>
                    <div className="font-medium text-gray-900">互联网</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600 mb-1">公司规模</div>
                    <div className="font-medium text-gray-900">10000人以上</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600 mb-1">融资阶段</div>
                    <div className="font-medium text-gray-900">已上市</div>
                  </div>
                </div>
                <button className="mt-4 w-full py-2 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors">
                  查看公司主页
                </button>
              </div>

              {/* Similar Jobs */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-xl font-bold text-gray-900 mb-4">相似职位</h3>
                <div className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <Link
                      key={i}
                      href={`/jobs/${parseInt(jobId) + i}`}
                      className="block p-3 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition-all"
                    >
                      <h4 className="font-medium text-gray-900 mb-1">前端开发工程师</h4>
                      <p className="text-sm text-gray-600">腾讯 · 20k-35k</p>
                    </Link>
                  ))}
                </div>
              </div>

              {/* Tips */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h3 className="text-lg font-bold text-blue-900 mb-3">投递小贴士</h3>
                <ul className="text-sm text-blue-800 space-y-2">
                  <li>• 完善个人简历，提高匹配度</li>
                  <li>• 突出相关项目经验</li>
                  <li>• 展示技术栈与岗位的契合度</li>
                  <li>• 及时关注投递进度</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
