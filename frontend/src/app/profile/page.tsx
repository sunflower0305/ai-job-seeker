'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Job, Application } from '@/types';

export default function ProfilePage() {
  const [activeTab, setActiveTab] = useState<'info' | 'resume' | 'applications' | 'collections'>('info');

  // 模拟用户数据
  const user = {
    username: 'user_demo',
    email: 'demo@example.com',
    first_name: '张',
    last_name: '三',
    avatar: '',
    joinDate: '2024-01-01',
  };

  const applications: Application[] = [
    {
      id: 1,
      user_id: 1,
      job_id: 1,
      status: 'pending',
      applied_at: '2024-01-15',
      job: {
        id: 1,
        title: 'React前端工程师',
        company: '字节跳动',
        location: '北京',
        salary: '25k-40k',
        experience: '3-5年',
        education: '本科',
      },
    },
  ];

  const collections: Job[] = [
    {
      id: 201,
      title: 'Vue.js前端工程师',
      company: '美团',
      location: '北京-海淀区',
      salary: '22k-38k',
      experience: '3-5年',
      education: '本科',
    },
  ];

  const stats = [
    { label: '投递职位', value: applications.length, icon: '📄', color: 'blue' },
    { label: '收藏职位', value: collections.length, icon: '⭐', color: 'yellow' },
    { label: '简历浏览', value: 23, icon: '👁️', color: 'green' },
    { label: '获得面试', value: 0, icon: '🎯', color: 'purple' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center">
            <div className="w-24 h-24 bg-white rounded-full flex items-center justify-center text-4xl font-bold text-blue-600">
              {user.first_name}
            </div>
            <div className="ml-6">
              <h1 className="text-3xl font-bold">{user.last_name}{user.first_name}</h1>
              <p className="text-blue-100 mt-1">@{user.username}</p>
              <p className="text-sm text-blue-100 mt-1">加入于 {user.joinDate}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {stats.map((stat, index) => (
            <div key={index} className="bg-white rounded-lg shadow-md p-6 text-center">
              <div className="text-4xl mb-2">{stat.icon}</div>
              <div className="text-3xl font-bold text-gray-900 mb-1">{stat.value}</div>
              <div className="text-gray-600">{stat.label}</div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="p-4">
                <h3 className="text-lg font-bold text-gray-900 mb-4">个人中心</h3>
                <nav className="space-y-1">
                  <button
                    onClick={() => setActiveTab('info')}
                    className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
                      activeTab === 'info'
                        ? 'bg-blue-50 text-blue-700 font-medium'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    基本信息
                  </button>
                  <button
                    onClick={() => setActiveTab('resume')}
                    className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
                      activeTab === 'resume'
                        ? 'bg-blue-50 text-blue-700 font-medium'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    我的简历
                  </button>
                  <button
                    onClick={() => setActiveTab('applications')}
                    className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
                      activeTab === 'applications'
                        ? 'bg-blue-50 text-blue-700 font-medium'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    投递记录
                  </button>
                  <button
                    onClick={() => setActiveTab('collections')}
                    className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
                      activeTab === 'collections'
                        ? 'bg-blue-50 text-blue-700 font-medium'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    我的收藏
                  </button>
                </nav>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            {/* Basic Info Tab */}
            {activeTab === 'info' && (
              <div className="bg-white rounded-lg shadow-md p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">基本信息</h2>
                <form className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        用户名
                      </label>
                      <input
                        type="text"
                        value={user.username}
                        disabled
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        邮箱
                      </label>
                      <input
                        type="email"
                        value={user.email}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        姓
                      </label>
                      <input
                        type="text"
                        value={user.last_name}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        名
                      </label>
                      <input
                        type="text"
                        value={user.first_name}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      个人简介
                    </label>
                    <textarea
                      rows={4}
                      placeholder="请输入个人简介..."
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    ></textarea>
                  </div>
                  <button
                    type="submit"
                    className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
                  >
                    保存修改
                  </button>
                </form>
              </div>
            )}

            {/* Resume Tab */}
            {activeTab === 'resume' && (
              <div className="bg-white rounded-lg shadow-md p-8">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-bold text-gray-900">我的简历</h2>
                  <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg">
                    上传简历
                  </button>
                </div>
                <div className="text-center py-12 border-2 border-dashed border-gray-300 rounded-lg">
                  <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p className="text-gray-600 mb-2">暂未上传简历</p>
                  <p className="text-sm text-gray-500">支持PDF、Word格式，不超过5MB</p>
                </div>
              </div>
            )}

            {/* Applications Tab */}
            {activeTab === 'applications' && (
              <div className="bg-white rounded-lg shadow-md p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">投递记录</h2>
                {applications.length > 0 ? (
                  <div className="space-y-4">
                    {applications.map((app) => (
                      <div key={app.id} className="border border-gray-200 rounded-lg p-6">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <Link href={`/jobs/${app.job_id}`}>
                              <h3 className="text-lg font-bold text-gray-900 hover:text-blue-600 cursor-pointer">
                                {app.job?.title}
                              </h3>
                            </Link>
                            <p className="text-gray-600 mt-1">{app.job?.company}</p>
                            <div className="mt-2 flex gap-4 text-sm text-gray-500">
                              <span>{app.job?.location}</span>
                              <span>{app.job?.salary}</span>
                            </div>
                            <p className="text-sm text-gray-500 mt-2">投递时间: {app.applied_at}</p>
                          </div>
                          <div>
                            <span className={`px-4 py-2 rounded-full text-sm font-medium ${
                              app.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                              app.status === 'accepted' ? 'bg-green-100 text-green-800' :
                              'bg-red-100 text-red-800'
                            }`}>
                              {app.status === 'pending' ? '待处理' :
                               app.status === 'accepted' ? '已通过' : '未通过'}
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <p className="text-gray-500">暂无投递记录</p>
                  </div>
                )}
              </div>
            )}

            {/* Collections Tab */}
            {activeTab === 'collections' && (
              <div className="bg-white rounded-lg shadow-md p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">我的收藏</h2>
                {collections.length > 0 ? (
                  <div className="space-y-4">
                    {collections.map((job) => (
                      <div key={job.id} className="border border-gray-200 rounded-lg p-6">
                        <Link href={`/jobs/${job.id}`}>
                          <h3 className="text-lg font-bold text-gray-900 hover:text-blue-600 cursor-pointer">
                            {job.title}
                          </h3>
                        </Link>
                        <p className="text-gray-600 mt-1">{job.company}</p>
                        <div className="mt-2 flex gap-4 text-sm text-gray-500">
                          <span>{job.location}</span>
                          <span className="text-orange-600 font-medium">{job.salary}</span>
                        </div>
                        <div className="mt-4 flex gap-2">
                          <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg">
                            投递简历
                          </button>
                          <button className="px-4 py-2 border border-gray-300 text-gray-700 hover:bg-gray-50 rounded-lg">
                            取消收藏
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <p className="text-gray-500">暂无收藏职位</p>
                    <Link href="/jobs" className="text-blue-600 hover:text-blue-700 mt-2 inline-block">
                      去看看职位
                    </Link>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
