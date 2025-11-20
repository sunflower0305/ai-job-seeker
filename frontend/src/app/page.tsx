'use client';

import Link from 'next/link';
import { useState } from 'react';

export default function Home() {
  const [searchKeyword, setSearchKeyword] = useState('');

  const features = [
    {
      icon: '🤖',
      title: '智能推荐',
      description: '基于机器学习算法，分析您的技能、经验和偏好，为您精准推荐最匹配的职位',
      color: 'from-blue-500 to-cyan-500',
    },
    {
      icon: '📊',
      title: '数据可视化',
      description: '直观展示职位市场趋势、薪资分布和行业动态，帮助您做出明智的职业决策',
      color: 'from-green-500 to-emerald-500',
    },
    {
      icon: '⚡',
      title: '实时更新',
      description: '从智联招聘实时获取最新职位信息，第一时间掌握优质工作机会',
      color: 'from-purple-500 to-pink-500',
    },
    {
      icon: '🎯',
      title: '精准匹配',
      description: '多维度职位匹配系统，考虑地点、薪资、经验等多个因素，找到最适合您的工作',
      color: 'from-orange-500 to-red-500',
    },
  ];

  const stats = [
    { value: '10,000+', label: '职位数量' },
    { value: '5,000+', label: '合作企业' },
    { value: '50,000+', label: '用户数量' },
    { value: '95%', label: '匹配准确率' },
  ];

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchKeyword.trim()) {
      window.location.href = `/jobs?search=${encodeURIComponent(searchKeyword)}`;
    }
  };

  return (
    <div className="bg-gray-50">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-800 text-white overflow-hidden">
        <div className="absolute inset-0 bg-grid-pattern opacity-10"></div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-32 relative z-10">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6 animate-fade-in">
              找到您的理想工作
            </h1>
            <p className="text-xl md:text-2xl mb-8 text-blue-100">
              智能推荐 · 精准匹配 · 高效求职
            </p>

            {/* 搜索框 */}
            <form onSubmit={handleSearch} className="max-w-3xl mx-auto mb-12">
              <div className="flex flex-col md:flex-row gap-4">
                <input
                  type="text"
                  value={searchKeyword}
                  onChange={(e) => setSearchKeyword(e.target.value)}
                  placeholder="搜索职位名称、公司或关键词..."
                  className="flex-1 px-6 py-4 rounded-lg text-gray-900 text-lg focus:outline-none focus:ring-4 focus:ring-blue-300"
                />
                <button
                  type="submit"
                  className="px-8 py-4 bg-orange-500 hover:bg-orange-600 text-white font-bold rounded-lg transition-all transform hover:scale-105 active:scale-95"
                >
                  搜索职位
                </button>
              </div>
            </form>

            {/* CTA 按钮 */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link
                href="/jobs"
                className="px-8 py-4 bg-white text-blue-600 font-bold rounded-lg hover:bg-gray-100 transition-all transform hover:scale-105 active:scale-95 shadow-lg"
              >
                浏览所有职位
              </Link>
              <Link
                href="/recommendations"
                className="px-8 py-4 bg-blue-500 hover:bg-blue-400 text-white font-bold rounded-lg transition-all transform hover:scale-105 active:scale-95 shadow-lg border-2 border-white"
              >
                获取智能推荐
              </Link>
            </div>
          </div>
        </div>

        {/* 波浪装饰 */}
        <div className="absolute bottom-0 left-0 right-0">
          <svg viewBox="0 0 1440 120" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path
              d="M0 120L60 105C120 90 240 60 360 45C480 30 600 30 720 37.5C840 45 960 60 1080 67.5C1200 75 1320 75 1380 75L1440 75V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0Z"
              fill="#F9FAFB"
            />
          </svg>
        </div>
      </section>

      {/* 数据统计 */}
      <section className="py-12 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-4xl font-bold text-blue-600 mb-2">{stat.value}</div>
                <div className="text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 核心功能 */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              为什么选择我们
            </h2>
            <p className="text-xl text-gray-600">
              先进的技术，贴心的服务，助您找到完美工作
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all transform hover:-translate-y-2 duration-300"
              >
                <div
                  className={`w-16 h-16 bg-gradient-to-br ${feature.color} rounded-xl flex items-center justify-center text-3xl mb-6 shadow-lg`}
                >
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 工作流程 */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              简单三步，开启求职之旅
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            <div className="text-center">
              <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center text-3xl font-bold text-blue-600 mx-auto mb-6">
                1
              </div>
              <h3 className="text-xl font-bold mb-3">注册账号</h3>
              <p className="text-gray-600">
                快速注册，填写您的技能和期望，让系统了解您
              </p>
            </div>

            <div className="text-center">
              <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center text-3xl font-bold text-green-600 mx-auto mb-6">
                2
              </div>
              <h3 className="text-xl font-bold mb-3">获取推荐</h3>
              <p className="text-gray-600">
                AI智能分析，为您推荐最匹配的职位机会
              </p>
            </div>

            <div className="text-center">
              <div className="w-20 h-20 bg-purple-100 rounded-full flex items-center justify-center text-3xl font-bold text-purple-600 mx-auto mb-6">
                3
              </div>
              <h3 className="text-xl font-bold mb-3">投递简历</h3>
              <p className="text-gray-600">
                一键投递，实时跟踪申请进度，把握每个机会
              </p>
            </div>
          </div>

          <div className="text-center mt-12">
            <Link
              href="/register"
              className="inline-block px-10 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold rounded-lg transition-all transform hover:scale-105 active:scale-95 shadow-lg"
            >
              立即开始
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            准备好找到您的理想工作了吗？
          </h2>
          <p className="text-xl mb-8 text-blue-100">
            立即加入，让AI帮您匹配最合适的职位
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/register"
              className="px-8 py-4 bg-white text-blue-600 font-bold rounded-lg hover:bg-gray-100 transition-all transform hover:scale-105 active:scale-95 shadow-lg"
            >
              免费注册
            </Link>
            <Link
              href="/jobs"
              className="px-8 py-4 bg-blue-500 hover:bg-blue-400 text-white font-bold rounded-lg transition-all transform hover:scale-105 active:scale-95 shadow-lg border-2 border-white"
            >
              浏览职位
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
