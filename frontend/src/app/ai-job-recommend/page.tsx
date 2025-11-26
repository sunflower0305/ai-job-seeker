'use client'

import { useState, useEffect } from 'react'
import ResumeUploader from '@/components/ui/ResumeUploader'
import AIAssistantChat from '@/components/ui/AIAssistantChat'
import Link from 'next/link'

interface RecommendedJob {
  job_id: number
  job_title: string
  company_name: string
  city: string
  salary_min: number
  salary_max: number
  education: string
  experience: string
  similarity_score: number
  tags: string[]
}

export default function AIJobRecommendPage() {
  const [step, setStep] = useState<'upload' | 'chat'>('upload')
  const [resumeAnalysis, setResumeAnalysis] = useState<any>(null)
  const [sessionId, setSessionId] = useState<string | undefined>()
  const [recommendedJobs, setRecommendedJobs] = useState<RecommendedJob[]>([])
  const [isLoadingJobs, setIsLoadingJobs] = useState(false)

  const handleAnalysisComplete = (data: any) => {
    setResumeAnalysis(data.resume_analysis)
    setStep('chat')
  }

  // 获取推荐职位
  const fetchRecommendedJobs = async (analysis: any) => {
    if (!analysis) return

    setIsLoadingJobs(true)
    try {
      // 将工作年限转换为经验格式
      let experience = '不限'
      if (analysis.experience_years !== undefined) {
        const years = analysis.experience_years
        if (years === 0) {
          experience = '应届生'
        } else if (years <= 1) {
          experience = '1年以下'
        } else if (years <= 3) {
          experience = '1-3年'
        } else if (years <= 5) {
          experience = '3-5年'
        } else if (years <= 10) {
          experience = '5-10年'
        } else {
          experience = '10年以上'
        }
      }

      const response = await fetch('http://localhost:8000/api/ml/recommend/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          skills: analysis.skills || [],
          experience: experience,
          education: analysis.education || '不限',
          preferred_city: '', // 不限制城市
          preferred_industry: '', // 不限制行业
          top_n: 10,
        }),
      })

      const result = await response.json()

      if (result.recommendations) {
        setRecommendedJobs(result.recommendations)
      }
    } catch (error) {
      console.error('获取推荐职位失败:', error)
    } finally {
      setIsLoadingJobs(false)
    }
  }

  // 当简历分析完成后，自动获取推荐职位
  useEffect(() => {
    if (resumeAnalysis && step === 'chat') {
      fetchRecommendedJobs(resumeAnalysis)
    }
  }, [resumeAnalysis, step])

  const handleReset = () => {
    setStep('upload')
    setResumeAnalysis(null)
    setSessionId(undefined)
    setRecommendedJobs([])
  }

  // 格式化薪资显示
  const formatSalary = (min: number, max: number) => {
    if (min === 0 && max === 0) return '面议'
    if (min === max) return `${min / 1000}K`
    return `${min / 1000}K-${max / 1000}K`
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* 页面标题 */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            AI 智能职位推荐
          </h1>
          <p className="text-lg text-gray-600">
            上传您的简历，让AI为您推荐最合适的职位
          </p>
        </div>

        {/* 进度指示器 */}
        <div className="mb-8">
          <div className="flex items-center justify-center space-x-4">
            <div className="flex items-center">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold ${
                  step === 'upload' ? 'bg-blue-500' : 'bg-green-500'
                }`}
              >
                {step === 'chat' ? '✓' : '1'}
              </div>
              <span className="ml-2 text-sm font-medium text-gray-700">
                上传简历
              </span>
            </div>

            <div className="w-20 h-1 bg-gray-300">
              <div
                className={`h-full transition-all duration-500 ${
                  step === 'chat' ? 'w-full bg-blue-500' : 'w-0'
                }`}
              />
            </div>

            <div className="flex items-center">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold ${
                  step === 'chat' ? 'bg-blue-500' : 'bg-gray-300'
                }`}
              >
                2
              </div>
              <span className="ml-2 text-sm font-medium text-gray-700">
                AI 对话推荐
              </span>
            </div>
          </div>
        </div>

        {/* 主要内容区域 */}
        <div className="bg-white rounded-xl shadow-xl overflow-hidden">
          {step === 'upload' ? (
            <div className="p-8">
              <div className="max-w-2xl mx-auto">
                <h2 className="text-2xl font-semibold text-gray-800 mb-6">
                  第一步：上传您的简历
                </h2>
                <ResumeUploader onAnalysisComplete={handleAnalysisComplete} />
              </div>
            </div>
          ) : (
            <div className="flex flex-col lg:flex-row h-[700px]">
              {/* 左侧：简历分析结果 */}
              <div className="lg:w-2/5 border-r border-gray-200 p-6 overflow-y-auto bg-gray-50">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-semibold text-gray-800">
                    简历分析结果
                  </h2>
                  <button
                    onClick={handleReset}
                    className="text-sm px-4 py-2 text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors"
                  >
                    重新上传
                  </button>
                </div>

                {resumeAnalysis && (
                  <div className="space-y-6">
                    {/* 技能 */}
                    {resumeAnalysis.skills && resumeAnalysis.skills.length > 0 && (
                      <div className="bg-white p-4 rounded-lg shadow-sm">
                        <h3 className="text-sm font-semibold text-gray-800 mb-3 flex items-center">
                          <span className="w-1 h-4 bg-blue-500 mr-2"></span>
                          技能
                        </h3>
                        <div className="flex flex-wrap gap-2">
                          {resumeAnalysis.skills.map((skill: string, index: number) => (
                            <span
                              key={index}
                              className="px-3 py-1.5 bg-blue-100 text-blue-700 text-sm rounded-full font-medium"
                            >
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* 基本信息 */}
                    <div className="bg-white p-4 rounded-lg shadow-sm space-y-3">
                      <h3 className="text-sm font-semibold text-gray-800 mb-3 flex items-center">
                        <span className="w-1 h-4 bg-green-500 mr-2"></span>
                        基本信息
                      </h3>

                      {/* 工作年限 */}
                      {resumeAnalysis.experience_years !== undefined && (
                        <div className="flex justify-between items-center py-2 border-b border-gray-100">
                          <span className="text-sm text-gray-600">工作年限</span>
                          <span className="text-sm font-medium text-gray-900">
                            {resumeAnalysis.experience_years} 年
                          </span>
                        </div>
                      )}

                      {/* 学历 */}
                      {resumeAnalysis.education && (
                        <div className="flex justify-between items-center py-2 border-b border-gray-100">
                          <span className="text-sm text-gray-600">学历</span>
                          <span className="text-sm font-medium text-gray-900">
                            {resumeAnalysis.education}
                          </span>
                        </div>
                      )}

                      {/* 期望职位 */}
                      {resumeAnalysis.desired_position && (
                        <div className="flex justify-between items-center py-2 border-b border-gray-100">
                          <span className="text-sm text-gray-600">期望职位</span>
                          <span className="text-sm font-medium text-gray-900">
                            {resumeAnalysis.desired_position}
                          </span>
                        </div>
                      )}

                      {/* 期望薪资 */}
                      {resumeAnalysis.desired_salary && (
                        <div className="flex justify-between items-center py-2">
                          <span className="text-sm text-gray-600">期望薪资</span>
                          <span className="text-sm font-medium text-green-600">
                            {resumeAnalysis.desired_salary}
                          </span>
                        </div>
                      )}
                    </div>

                    {/* 核心优势 */}
                    {resumeAnalysis.key_strengths && resumeAnalysis.key_strengths.length > 0 && (
                      <div className="bg-white p-4 rounded-lg shadow-sm">
                        <h3 className="text-sm font-semibold text-gray-800 mb-3 flex items-center">
                          <span className="w-1 h-4 bg-purple-500 mr-2"></span>
                          核心优势
                        </h3>
                        <ul className="space-y-2">
                          {resumeAnalysis.key_strengths.map((strength: string, index: number) => (
                            <li key={index} className="flex items-start">
                              <span className="text-purple-500 mr-2 mt-0.5">•</span>
                              <span className="text-sm text-gray-700 flex-1">
                                {strength}
                              </span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* 工作经历摘要 */}
                    {resumeAnalysis.work_experience && (
                      <div className="bg-white p-4 rounded-lg shadow-sm">
                        <h3 className="text-sm font-semibold text-gray-800 mb-3 flex items-center">
                          <span className="w-1 h-4 bg-orange-500 mr-2"></span>
                          工作经历
                        </h3>
                        <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
                          {resumeAnalysis.work_experience}
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* 右侧：AI 对话 */}
              <div className="lg:w-3/5 flex flex-col">
                <AIAssistantChat
                  sessionId={sessionId}
                  resumeContext={resumeAnalysis}
                  onSessionIdChange={setSessionId}
                />
              </div>
            </div>
          )}
        </div>

        {/* 推荐职位列表 */}
        {step === 'chat' && (
          <div className="mt-8">
            <div className="bg-white rounded-xl shadow-xl p-8">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">
                  为您推荐的职位
                </h2>
                {recommendedJobs.length > 0 && (
                  <span className="text-sm text-gray-600">
                    共找到 {recommendedJobs.length} 个匹配职位
                  </span>
                )}
              </div>

              {isLoadingJobs ? (
                <div className="flex flex-col items-center justify-center py-12">
                  <svg className="animate-spin h-12 w-12 text-blue-500 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <p className="text-gray-600">正在为您匹配合适的职位...</p>
                </div>
              ) : recommendedJobs.length > 0 ? (
                <div className="grid gap-4">
                  {recommendedJobs.map((job) => (
                    <div
                      key={job.job_id}
                      className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6 border-l-4 border-blue-500 relative"
                    >
                      {/* 匹配度标签 - 右上角 */}
                      <div className="absolute top-4 right-4">
                        <div className="flex items-center bg-gradient-to-r from-blue-500 to-purple-500 text-white px-3 py-1.5 rounded-full text-xs font-semibold shadow-lg">
                          <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                          </svg>
                          匹配度 {(job.similarity_score * 100).toFixed(0)}%
                        </div>
                      </div>

                      <div className="flex justify-between items-start pr-32">
                        <div className="flex-1">
                          <Link href={`/jobs/${job.job_id}`}>
                            <h3 className="text-xl font-bold text-gray-900 hover:text-blue-600 cursor-pointer transition-colors">
                              {job.job_title}
                            </h3>
                          </Link>
                          <div className="mt-2 flex flex-wrap gap-4 text-sm text-gray-600">
                            <span className="flex items-center">
                              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                              </svg>
                              {job.company_name}
                            </span>
                            <span className="flex items-center">
                              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                              </svg>
                              {job.city}
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
                          {job.tags && job.tags.length > 0 && (
                            <div className="mt-3 flex flex-wrap gap-2">
                              {job.tags.slice(0, 5).map((tag, index) => (
                                <span key={index} className="px-2 py-1 text-xs bg-blue-50 text-blue-700 rounded">
                                  {tag}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                        <div className="ml-6 text-right">
                          <div className="text-2xl font-bold text-orange-600">
                            {formatSalary(job.salary_min, job.salary_max)}
                          </div>
                          <div className="mt-4 flex gap-2">
                            <button
                              onClick={(e) => {
                                e.preventDefault();
                                alert('收藏功能开发中');
                              }}
                              className="px-4 py-2 text-sm text-gray-700 border border-gray-300 rounded hover:bg-gray-50 transition-colors"
                            >
                              收藏
                            </button>
                            <Link href={`/jobs/${job.job_id}`}>
                              <button className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors">
                                查看详情
                              </button>
                            </Link>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">🔍</div>
                  <h3 className="text-xl font-semibold text-gray-800 mb-2">
                    暂无推荐职位
                  </h3>
                  <p className="text-gray-600">
                    请尝试更新您的简历或调整期望条件
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* 帮助文本 */}
        <div className="mt-8 text-center text-sm text-gray-600 space-y-2">
          <p>
            上传简历后，AI 将自动分析您的技能和经验，并为您推荐最合适的职位
          </p>
          <p>
            您还可以在对话中询问任何关于职位的问题，AI 助手将为您详细解答
          </p>
        </div>
      </div>
    </div>
  )
}
