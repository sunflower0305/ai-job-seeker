'use client'

import { useState } from 'react'
import ResumeUploader from '@/components/ui/ResumeUploader'
import AIAssistantChat from '@/components/ui/AIAssistantChat'

export default function AIRecommendPage() {
  const [step, setStep] = useState<'upload' | 'chat'>('upload')
  const [resumeAnalysis, setResumeAnalysis] = useState<any>(null)
  const [sessionId, setSessionId] = useState<string | undefined>()

  const handleAnalysisComplete = (analysis: any) => {
    setResumeAnalysis(analysis)
    setStep('chat')
  }

  const handleReset = () => {
    setStep('upload')
    setResumeAnalysis(null)
    setSessionId(undefined)
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
              <div className="lg:w-1/3 border-r border-gray-200 p-6 overflow-y-auto">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-semibold text-gray-800">
                    简历分析结果
                  </h2>
                  <button
                    onClick={handleReset}
                    className="text-sm text-blue-500 hover:text-blue-600"
                  >
                    重新上传
                  </button>
                </div>

                {resumeAnalysis && (
                  <div className="space-y-4">
                    {/* 技能 */}
                    {resumeAnalysis.skills && resumeAnalysis.skills.length > 0 && (
                      <div>
                        <h3 className="text-sm font-medium text-gray-700 mb-2">
                          技能
                        </h3>
                        <div className="flex flex-wrap gap-2">
                          {resumeAnalysis.skills.map((skill: string, index: number) => (
                            <span
                              key={index}
                              className="px-3 py-1 bg-blue-100 text-blue-700 text-sm rounded-full"
                            >
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* 工作年限 */}
                    {resumeAnalysis.experience_years !== undefined && (
                      <div>
                        <h3 className="text-sm font-medium text-gray-700 mb-2">
                          工作年限
                        </h3>
                        <p className="text-gray-600">
                          {resumeAnalysis.experience_years} 年
                        </p>
                      </div>
                    )}

                    {/* 学历 */}
                    {resumeAnalysis.education && (
                      <div>
                        <h3 className="text-sm font-medium text-gray-700 mb-2">
                          学历
                        </h3>
                        <p className="text-gray-600">{resumeAnalysis.education}</p>
                      </div>
                    )}

                    {/* 期望职位 */}
                    {resumeAnalysis.desired_position && (
                      <div>
                        <h3 className="text-sm font-medium text-gray-700 mb-2">
                          期望职位
                        </h3>
                        <p className="text-gray-600">
                          {resumeAnalysis.desired_position}
                        </p>
                      </div>
                    )}

                    {/* 期望薪资 */}
                    {resumeAnalysis.desired_salary && (
                      <div>
                        <h3 className="text-sm font-medium text-gray-700 mb-2">
                          期望薪资
                        </h3>
                        <p className="text-gray-600">
                          {resumeAnalysis.desired_salary}
                        </p>
                      </div>
                    )}

                    {/* 核心优势 */}
                    {resumeAnalysis.key_strengths && resumeAnalysis.key_strengths.length > 0 && (
                      <div>
                        <h3 className="text-sm font-medium text-gray-700 mb-2">
                          核心优势
                        </h3>
                        <ul className="list-disc list-inside space-y-1">
                          {resumeAnalysis.key_strengths.map((strength: string, index: number) => (
                            <li key={index} className="text-gray-600 text-sm">
                              {strength}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* 工作经历摘要 */}
                    {resumeAnalysis.work_experience && (
                      <div>
                        <h3 className="text-sm font-medium text-gray-700 mb-2">
                          工作经历
                        </h3>
                        <p className="text-gray-600 text-sm whitespace-pre-wrap">
                          {resumeAnalysis.work_experience}
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* 右侧：AI 对话 */}
              <div className="lg:w-2/3 flex flex-col">
                <AIAssistantChat
                  sessionId={sessionId}
                  resumeContext={resumeAnalysis}
                  onSessionIdChange={setSessionId}
                />
              </div>
            </div>
          )}
        </div>

        {/* 帮助文本 */}
        <div className="mt-8 text-center text-sm text-gray-600">
          <p>
            上传简历后，AI 将自动分析您的技能和经验，并为您推荐最合适的职位
          </p>
          <p className="mt-2">
            您还可以在对话中询问任何关于职位的问题，AI 助手将为您详细解答
          </p>
        </div>
      </div>
    </div>
  )
}
