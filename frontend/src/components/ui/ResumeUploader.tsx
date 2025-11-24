'use client'

import { useState } from 'react'

interface ResumeUploaderProps {
  onAnalysisComplete: (analysis: any) => void
}

export default function ResumeUploader({ onAnalysisComplete }: ResumeUploaderProps) {
  const [file, setFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [dragActive, setDragActive] = useState(false)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0])
      setError(null)
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setError(null)
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError('请选择文件')
      return
    }

    // 验证文件类型
    const allowedTypes = ['.pdf', '.docx', '.doc', '.txt']
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()
    if (!allowedTypes.includes(fileExtension)) {
      setError(`不支持的文件类型。支持的格式: ${allowedTypes.join(', ')}`)
      return
    }

    // 验证文件大小（10MB）
    if (file.size > 10 * 1024 * 1024) {
      setError('文件大小不能超过10MB')
      return
    }

    setIsUploading(true)
    setError(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('http://localhost:8000/api/jobs/resume-analysis/analyze/', {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (data.success) {
        onAnalysisComplete(data.resume_analysis)
      } else {
        setError(data.error || '分析失败')
      }
    } catch (error) {
      console.error('上传失败:', error)
      setError('上传文件时出现错误，请稍后再试')
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="w-full">
      <div
        className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="file-upload"
          className="hidden"
          onChange={handleFileChange}
          accept=".pdf,.docx,.doc,.txt"
          disabled={isUploading}
        />

        <div className="space-y-4">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            stroke="currentColor"
            fill="none"
            viewBox="0 0 48 48"
            aria-hidden="true"
          >
            <path
              d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>

          {file ? (
            <div>
              <p className="text-sm text-gray-600">已选择文件:</p>
              <p className="text-base font-medium text-gray-900">{file.name}</p>
              <p className="text-sm text-gray-500">
                {(file.size / 1024).toFixed(2)} KB
              </p>
            </div>
          ) : (
            <div>
              <p className="text-base text-gray-600">
                拖拽文件到此处，或
                <label
                  htmlFor="file-upload"
                  className="text-blue-500 hover:text-blue-600 cursor-pointer mx-1"
                >
                  点击选择
                </label>
              </p>
              <p className="text-sm text-gray-500 mt-2">
                支持 PDF、Word、TXT 格式，最大 10MB
              </p>
            </div>
          )}

          {error && (
            <div className="text-sm text-red-500 bg-red-50 rounded-lg px-4 py-2">
              {error}
            </div>
          )}

          <div className="flex justify-center space-x-4">
            {file && (
              <button
                onClick={() => {
                  setFile(null)
                  setError(null)
                }}
                className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
                disabled={isUploading}
              >
                清除
              </button>
            )}
            <button
              onClick={handleUpload}
              disabled={!file || isUploading}
              className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              {isUploading ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  分析中...
                </span>
              ) : (
                '上传并分析'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
