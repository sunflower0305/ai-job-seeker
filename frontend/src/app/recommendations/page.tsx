'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Job } from '@/types';

export default function RecommendationsPage() {
  const [recommendations, setRecommendations] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      // TODO: 集成真实推荐API
      await new Promise(resolve => setTimeout(resolve, 1000));

      // 使用模拟推荐数据
      setRecommendations([
        {
          id: 101,
          title: 'React高级前端工程师',
          company: '字节跳动',
          location: '北京-朝阳区',
          salary: '30k-50k',
          experience: '3-5年',
          education: '本科',
          description: '负责抖音前端架构设计与开发',
        },
        {
          id: 102,
          title: 'TypeScript开发专家',
          company: '腾讯',
          location: '深圳-南山区',
          salary: '35k-60k',
          experience: '5-10年',
          education: '本科',
          description: '负责微信小程序开发框架',
        },
        {
          id: 103,
          title: '全栈工程师',
          company: '阿里巴巴',
          location: '杭州-西湖区',
          salary: '40k-70k',
          experience: '5-10年',
          education: '本科',
          description: '负责淘宝核心业务系统开发',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold mb-4">智能职位推荐</h1>
            <p className="text-xl text-purple-100">
              基于AI算法，为您精准匹配最合适的职位机会
            </p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        {/* Info Banner */}
        <div className="mb-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg className="h-6 w-6 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-lg font-medium text-blue-900">推荐说明</h3>
              <div className="mt-2 text-sm text-blue-700">
                <p>我们的AI系统会根据以下因素为您推荐职位：</p>
                <ul className="list-disc list-inside mt-2 space-y-1">
                  <li>您的技能和工作经验</li>
                  <li>期望的薪资范围和工作地点</li>
                  <li>行业偏好和职业发展方向</li>
                  <li>与职位要求的匹配度</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-purple-100 rounded-lg p-3">
                <svg className="h-6 w-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-2xl font-bold text-gray-900">95%</p>
                <p className="text-gray-600">匹配准确率</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-green-100 rounded-lg p-3">
                <svg className="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-2xl font-bold text-gray-900">{recommendations.length}</p>
                <p className="text-gray-600">推荐职位</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-blue-100 rounded-lg p-3">
                <svg className="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-2xl font-bold text-gray-900">24小时</p>
                <p className="text-gray-600">实时更新</p>
              </div>
            </div>
          </div>
        </div>

        {/* Recommendations List */}
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">为您推荐</h2>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
          </div>
        ) : (
          <div className="grid gap-6">
            {recommendations.map((job, index) => (
              <div
                key={job.id}
                className="bg-white rounded-lg shadow-md hover:shadow-xl transition-all p-6 border-l-4 border-purple-600"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <span className="bg-purple-100 text-purple-800 text-xs font-medium px-3 py-1 rounded-full">
                        推荐度: {95 - index * 3}%
                      </span>
                    </div>
                    <Link href={`/jobs/${job.id}`}>
                      <h3 className="text-2xl font-bold text-gray-900 hover:text-purple-600 cursor-pointer mb-2">
                        {job.title}
                      </h3>
                    </Link>
                    <p className="text-lg text-gray-700 mb-4">{job.company}</p>

                    <div className="flex flex-wrap gap-4 mb-4">
                      <span className="flex items-center text-gray-600">
                        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        </svg>
                        {job.location}
                      </span>
                      <span className="flex items-center text-gray-600">
                        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                        {job.experience}
                      </span>
                      <span className="flex items-center text-gray-600">
                        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                        </svg>
                        {job.education}
                      </span>
                    </div>

                    <p className="text-gray-600">{job.description}</p>

                    <div className="mt-4 flex items-center gap-2">
                      <span className="bg-green-100 text-green-800 text-sm px-3 py-1 rounded-full">匹配您的技能</span>
                      <span className="bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full">符合期望薪资</span>
                    </div>
                  </div>

                  <div className="ml-6 text-right">
                    <div className="text-3xl font-bold text-orange-600 mb-6">{job.salary}</div>
                    <div className="space-y-2">
                      <button className="w-full px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg transition-colors">
                        立即投递
                      </button>
                      <button className="w-full px-6 py-2 border border-gray-300 text-gray-700 hover:bg-gray-50 font-medium rounded-lg transition-colors">
                        收藏
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
