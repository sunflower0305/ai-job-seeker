'use client'

import { useState } from 'react'
import ResumeUploader from '@/components/ui/ResumeUploader'

export default function AIResumeOptimizePage() {
  const [resumeAnalysis, setResumeAnalysis] = useState<any>(null)
  const [resumeText, setResumeText] = useState<string>('')
  const [isOptimizing, setIsOptimizing] = useState(false)
  const [isExporting, setIsExporting] = useState(false)
  const [isExportingResume, setIsExportingResume] = useState(false)
  const [optimizationResult, setOptimizationResult] = useState<any>(null)

  const handleAnalysisComplete = (data: any) => {
    setResumeAnalysis(data.resume_analysis)
    setResumeText(data.resume_text || '')
  }

  const handleReset = () => {
    setResumeAnalysis(null)
    setResumeText('')
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
        alert('报告导出成功！')
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

  // 导出优化后的简历文档
  const handleExportOptimizedResume = async () => {
    if (!optimizationResult || !optimizationResult.optimized_resume) {
      alert('请先优化简历')
      return
    }

    setIsExportingResume(true)
    try {
      const response = await fetch('http://localhost:8000/api/jobs/export-resume/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          resume_data: optimizationResult.optimized_resume,
          format: 'word',
        }),
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = '优化后的简历.docx'
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
        alert('优化后的简历导出成功！')
      } else {
        alert('导出简历失败')
      }
    } catch (error) {
      console.error('导出简历时出错:', error)
      alert('导出简历时出现错误')
    } finally {
      setIsExportingResume(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* 页面标题 */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            AI 智能简历优化
          </h1>
          <p className="text-lg text-gray-600">
            上传您的简历，让AI为您提供专业的优化建议
          </p>
        </div>

        {/* 主要内容区域 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 左侧：简历上传和分析结果 */}
          <div className="space-y-6">
            {/* 简历上传卡片 */}
            <div className="bg-white rounded-xl shadow-xl p-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-6">
                上传简历
              </h2>
              <ResumeUploader onAnalysisComplete={handleAnalysisComplete} />

              {resumeAnalysis && (
                <button
                  onClick={handleReset}
                  className="mt-4 w-full px-4 py-2 text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors border border-blue-200"
                >
                  重新上传
                </button>
              )}
            </div>

            {/* 简历分析结果 */}
            {resumeAnalysis && (
              <div className="bg-white rounded-xl shadow-xl p-8">
                <h2 className="text-xl font-semibold text-gray-800 mb-6">
                  简历分析结果
                </h2>

                <div className="space-y-6">
                  {/* 技能 */}
                  {resumeAnalysis.skills && resumeAnalysis.skills.length > 0 && (
                    <div>
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
                  <div className="space-y-3">
                    <h3 className="text-sm font-semibold text-gray-800 mb-3 flex items-center">
                      <span className="w-1 h-4 bg-green-500 mr-2"></span>
                      基本信息
                    </h3>

                    {resumeAnalysis.experience_years !== undefined && (
                      <div className="flex justify-between items-center py-2 border-b border-gray-100">
                        <span className="text-sm text-gray-600">工作年限</span>
                        <span className="text-sm font-medium text-gray-900">
                          {resumeAnalysis.experience_years} 年
                        </span>
                      </div>
                    )}

                    {resumeAnalysis.education && (
                      <div className="flex justify-between items-center py-2 border-b border-gray-100">
                        <span className="text-sm text-gray-600">学历</span>
                        <span className="text-sm font-medium text-gray-900">
                          {resumeAnalysis.education}
                        </span>
                      </div>
                    )}

                    {resumeAnalysis.desired_position && (
                      <div className="flex justify-between items-center py-2 border-b border-gray-100">
                        <span className="text-sm text-gray-600">期望职位</span>
                        <span className="text-sm font-medium text-gray-900">
                          {resumeAnalysis.desired_position}
                        </span>
                      </div>
                    )}

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
                    <div>
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
                </div>
              </div>
            )}
          </div>

          {/* 右侧：优化功能 */}
          <div className="space-y-6">
            {resumeAnalysis ? (
              <>
                {/* 操作按钮卡片 */}
                <div className="bg-white rounded-xl shadow-xl p-8">
                  <h2 className="text-xl font-semibold text-gray-800 mb-6">
                    优化操作
                  </h2>
                  <div className="space-y-4">
                    <button
                      onClick={handleOptimizeResume}
                      disabled={isOptimizing}
                      className="w-full px-6 py-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white text-lg font-semibold rounded-lg hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
                    >
                      {isOptimizing ? (
                        <span className="flex items-center justify-center">
                          <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          正在优化...
                        </span>
                      ) : (
                        '🚀 AI 优化简历'
                      )}
                    </button>

                    <button
                      onClick={handleExportReport}
                      disabled={isExporting}
                      className="w-full px-6 py-4 bg-gradient-to-r from-blue-500 to-cyan-500 text-white text-lg font-semibold rounded-lg hover:from-blue-600 hover:to-cyan-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
                    >
                      {isExporting ? (
                        <span className="flex items-center justify-center">
                          <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          导出中...
                        </span>
                      ) : (
                        '📄 导出分析报告'
                      )}
                    </button>

                    {optimizationResult && (
                      <button
                        onClick={handleExportOptimizedResume}
                        disabled={isExportingResume}
                        className="w-full px-6 py-4 bg-gradient-to-r from-green-500 to-emerald-500 text-white text-lg font-semibold rounded-lg hover:from-green-600 hover:to-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
                      >
                        {isExportingResume ? (
                          <span className="flex items-center justify-center">
                            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            导出中...
                          </span>
                        ) : (
                          '💾 导出优化简历'
                        )}
                      </button>
                    )}
                  </div>
                </div>

                {/* 优化结果展示 */}
                {optimizationResult && (
                  <div className="bg-white rounded-xl shadow-xl p-8">
                    <h2 className="text-xl font-semibold text-gray-800 mb-6 flex items-center">
                      <span className="text-2xl mr-2">✨</span>
                      优化建议
                    </h2>

                    {/* 优化总结 */}
                    <div className="mb-6 p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border border-purple-200">
                      <h3 className="text-sm font-semibold text-purple-800 mb-2">
                        整体优化说明
                      </h3>
                      <p className="text-sm text-purple-700 leading-relaxed">
                        {optimizationResult.optimization_summary}
                      </p>
                    </div>

                    {/* 具体修改建议 */}
                    {optimizationResult.changes && optimizationResult.changes.length > 0 && (
                      <div>
                        <h3 className="text-sm font-semibold text-gray-800 mb-4">
                          具体修改建议
                        </h3>
                        <div className="space-y-3">
                          {optimizationResult.changes.map((change: any, index: number) => (
                            <div key={index} className="p-4 bg-gray-50 rounded-lg border border-gray-200 hover:border-purple-300 transition-colors">
                              <div className="flex items-start">
                                <span className="flex-shrink-0 w-6 h-6 bg-purple-500 text-white rounded-full flex items-center justify-center text-xs font-bold mr-3 mt-0.5">
                                  {index + 1}
                                </span>
                                <div className="flex-1">
                                  <h4 className="font-semibold text-purple-800 mb-1">
                                    {change.section}
                                  </h4>
                                  <p className="text-sm text-gray-700">
                                    {change.reason}
                                  </p>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* 优化后的简历内容预览 */}
                    {optimizationResult.optimized_resume && (
                      <div className="mt-6">
                        <h3 className="text-sm font-semibold text-gray-800 mb-3">
                          优化后的简历内容
                        </h3>
                        <div className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border border-blue-200 max-h-96 overflow-y-auto">
                          <div className="space-y-4 text-sm">
                            {optimizationResult.optimized_resume.skills && (
                              <div>
                                <p className="font-semibold text-gray-800">技能：</p>
                                <p className="text-gray-700">
                                  {optimizationResult.optimized_resume.skills.join('、')}
                                </p>
                              </div>
                            )}
                            {optimizationResult.optimized_resume.work_experience && (
                              <div>
                                <p className="font-semibold text-gray-800">工作经历：</p>
                                <div className="text-gray-700 whitespace-pre-wrap">
                                  {typeof optimizationResult.optimized_resume.work_experience === 'string'
                                    ? optimizationResult.optimized_resume.work_experience
                                    : Array.isArray(optimizationResult.optimized_resume.work_experience)
                                    ? optimizationResult.optimized_resume.work_experience.map((exp: any, idx: number) => (
                                        <div key={idx} className="mb-3 pb-3 border-b border-gray-200 last:border-0">
                                          {typeof exp === 'string' ? (
                                            <p>{exp}</p>
                                          ) : (
                                            <>
                                              <p className="font-medium">{exp.company || exp.position || ''}</p>
                                              {exp.position && exp.company && <p className="text-sm text-gray-600">{exp.position}</p>}
                                              {exp.time && <p className="text-sm text-gray-500">{exp.time}</p>}
                                              {exp.responsibilities && (
                                                <div className="mt-1">
                                                  {Array.isArray(exp.responsibilities) ? (
                                                    <ul className="list-disc list-inside text-sm">
                                                      {exp.responsibilities.map((resp: string, i: number) => (
                                                        <li key={i}>{resp}</li>
                                                      ))}
                                                    </ul>
                                                  ) : (
                                                    <p className="text-sm">{exp.responsibilities}</p>
                                                  )}
                                                </div>
                                              )}
                                            </>
                                          )}
                                        </div>
                                      ))
                                    : JSON.stringify(optimizationResult.optimized_resume.work_experience)
                                  }
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </>
            ) : (
              <div className="bg-white rounded-xl shadow-xl p-12 text-center">
                <div className="text-6xl mb-4">📝</div>
                <h3 className="text-xl font-semibold text-gray-800 mb-2">
                  尚未上传简历
                </h3>
                <p className="text-gray-600">
                  请先在左侧上传您的简历，AI将为您提供专业的优化建议
                </p>
              </div>
            )}
          </div>
        </div>

        {/* 帮助文本 */}
        <div className="mt-8 text-center text-sm text-gray-600 space-y-2">
          <p>
            AI 简历优化将根据行业最佳实践和招聘需求，为您的简历提供专业的改进建议
          </p>
          <p>
            您可以导出详细的分析报告，包含简历评分、优化建议和行业对比等信息
          </p>
        </div>
      </div>
    </div>
  )
}
