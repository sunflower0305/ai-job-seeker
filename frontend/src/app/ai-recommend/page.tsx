'use client'

import { useState } from 'react'
import ResumeUploader from '@/components/ui/ResumeUploader'
import AIAssistantChat from '@/components/ui/AIAssistantChat'

export default function AIRecommendPage() {
  const [step, setStep] = useState<'upload' | 'chat'>('upload')
  const [resumeAnalysis, setResumeAnalysis] = useState<any>(null)
  const [resumeText, setResumeText] = useState<string>('')
  const [sessionId, setSessionId] = useState<string | undefined>()
  const [isOptimizing, setIsOptimizing] = useState(false)
  const [isExporting, setIsExporting] = useState(false)
  const [optimizationResult, setOptimizationResult] = useState<any>(null)

  const handleAnalysisComplete = (data: any) => {
    setResumeAnalysis(data.resume_analysis)
    setResumeText(data.resume_text || '')
    setStep('chat')
  }

  const handleReset = () => {
    setStep('upload')
    setResumeAnalysis(null)
    setResumeText('')
    setSessionId(undefined)
    setOptimizationResult(null)
  }

  // 优化简历
  const handleOptimizeResume = async () => {
    if (!resumeText || !resumeAnalysis) {
      alert('缺少简历数据')
      return
    }

    setIsOptimizing(true)
    try {
      const response = await fetch('http://localhost:8000/api/jobs/resume-optimize/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          resume_text: resumeText,
          analysis_data: resumeAnalysis,
          target_position: resumeAnalysis.desired_position,
        }),
      })

      const result = await response.json()

      if (result.success) {
        setOptimizationResult(result)
        alert('简历优化完成！查看下方的优化建议')
      } else {
        alert(`优化失败: ${result.error}`)
      }
    } catch (error) {
      console.error('优化简历时出错:', error)
      alert('优化简历时出现错误')
    } finally {
      setIsOptimizing(false)
    }
  }

  // 导出分析报告
  const handleExportReport = async () => {
    if (!resumeAnalysis) {
      alert('缺少分析数据')
      return
    }

    setIsExporting(true)
    try {
      const response = await fetch('http://localhost:8000/api/jobs/export-report/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          analysis_data: resumeAnalysis,
          format: 'word',
        }),
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = '简历分析报告.docx'
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
      } else {
        alert('导出报告失败')
      }
    } catch (error) {
      console.error('导出报告时出错:', error)
      alert('导出报告时出现错误')
    } finally {
      setIsExporting(false)
    }
  }

  // 导出简历文档
  const handleExportResume = async (useOptimized: boolean = false) => {
    const dataToExport = useOptimized && optimizationResult
      ? optimizationResult.optimized_resume
      : resumeAnalysis

    if (!dataToExport) {
      alert('缺少简历数据')
      return
    }

    setIsExporting(true)
    try {
      const response = await fetch('http://localhost:8000/api/jobs/export-resume/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          resume_data: dataToExport,
          format: 'word',
        }),
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = useOptimized ? '优化后的简历.docx' : '简历.docx'
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
      } else {
        alert('导出简历失败')
      }
    } catch (error) {
      console.error('导出简历时出错:', error)
      alert('导出简历时出现错误')
    } finally {
      setIsExporting(false)
    }
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

                {/* 操作按钮区域 */}
                <div className="mb-6 space-y-2">
                  <button
                    onClick={handleOptimizeResume}
                    disabled={isOptimizing}
                    className="w-full px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    {isOptimizing ? '正在优化...' : '🚀 AI 优化简历'}
                  </button>

                  <button
                    onClick={handleExportReport}
                    disabled={isExporting}
                    className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    {isExporting ? '导出中...' : '📄 导出分析报告'}
                  </button>

                  <button
                    onClick={() => handleExportResume(false)}
                    disabled={isExporting}
                    className="w-full px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    {isExporting ? '导出中...' : '💾 导出简历文档'}
                  </button>

                  {optimizationResult && (
                    <button
                      onClick={() => handleExportResume(true)}
                      disabled={isExporting}
                      className="w-full px-4 py-2 bg-gradient-to-r from-green-500 to-teal-500 text-white rounded-lg hover:from-green-600 hover:to-teal-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                    >
                      {isExporting ? '导出中...' : '✨ 导出优化后简历'}
                    </button>
                  )}
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

                    {/* 优化结果展示 */}
                    {optimizationResult && (
                      <div className="mt-6 p-4 bg-purple-50 rounded-lg border border-purple-200">
                        <h3 className="text-sm font-medium text-purple-800 mb-2">
                          ✨ 优化建议
                        </h3>
                        <p className="text-sm text-purple-700 mb-3">
                          {optimizationResult.optimization_summary}
                        </p>
                        <div className="space-y-2">
                          {optimizationResult.changes && optimizationResult.changes.slice(0, 3).map((change: any, index: number) => (
                            <div key={index} className="text-xs">
                              <span className="font-medium text-purple-800">{change.section}:</span>
                              <span className="text-purple-600 ml-1">{change.reason}</span>
                            </div>
                          ))}
                        </div>
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
