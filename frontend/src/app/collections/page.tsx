'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Job } from '@/types';

export default function CollectionsPage() {
  const [collections, setCollections] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCollections();
  }, []);

  const fetchCollections = async () => {
    try {
      setLoading(true);
      // TODO: 集成真实API
      await new Promise(resolve => setTimeout(resolve, 800));

      // 使用模拟数据
      setCollections([
        {
          id: 201,
          title: 'Vue.js前端工程师',
          company: '美团',
          location: '北京-海淀区',
          salary: '22k-38k',
          experience: '3-5年',
          education: '本科',
          description: '负责美团外卖前端开发',
        },
        {
          id: 202,
          title: 'Node.js后端工程师',
          company: '京东',
          location: '北京-亦庄',
          salary: '28k-45k',
          experience: '3-5年',
          education: '本科',
          description: '负责京东商城后端服务',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = (id: number) => {
    setCollections(collections.filter(job => job.id !== id));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">我的收藏</h1>
          <p className="mt-2 text-gray-600">
            您收藏了 {collections.length} 个职位
          </p>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : collections.length > 0 ? (
          <div className="grid gap-4">
            {collections.map((job) => (
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
                    <p className="text-gray-600 mt-1">{job.company}</p>

                    <div className="mt-3 flex flex-wrap gap-4 text-sm text-gray-600">
                      <span className="flex items-center">
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        </svg>
                        {job.location}
                      </span>
                      <span className="flex items-center">
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                        {job.experience}
                      </span>
                      <span className="flex items-center">
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                        </svg>
                        {job.education}
                      </span>
                    </div>

                    <p className="mt-3 text-gray-600">{job.description}</p>
                  </div>

                  <div className="ml-6 text-right">
                    <div className="text-2xl font-bold text-orange-600 mb-4">{job.salary}</div>
                    <div className="flex flex-col gap-2">
                      <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">
                        投递简历
                      </button>
                      <button
                        onClick={() => handleRemove(job.id)}
                        className="px-4 py-2 border border-red-300 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      >
                        取消收藏
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-20 bg-white rounded-lg">
            <svg className="w-20 h-20 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
            <h3 className="text-xl font-medium text-gray-900 mb-2">暂无收藏职位</h3>
            <p className="text-gray-600 mb-6">浏览职位并收藏您感兴趣的机会</p>
            <Link
              href="/jobs"
              className="inline-block px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
            >
              去看看职位
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
