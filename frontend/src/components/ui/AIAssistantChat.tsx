'use client'

import { useState, useRef, useEffect } from 'react'
import MarkdownMessage from './MarkdownMessage'
import '@/styles/markdown.css'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

interface AIAssistantChatProps {
  sessionId?: string
  resumeContext?: any
  onSessionIdChange?: (sessionId: string) => void
}

export default function AIAssistantChat({
  sessionId: initialSessionId,
  resumeContext,
  onSessionIdChange
}: AIAssistantChatProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string | undefined>(initialSessionId)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage = inputMessage.trim()
    setInputMessage('')
    setIsLoading(true)

    // 添加用户消息到界面
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])

    try {
      const response = await fetch('http://localhost:8000/api/jobs/ai-assistant/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          session_id: sessionId,
          resume_context: resumeContext && !sessionId ? resumeContext : undefined,
        }),
      })

      const data = await response.json()

      if (data.success) {
        // 更新会话ID
        if (data.session_id && data.session_id !== sessionId) {
          setSessionId(data.session_id)
          onSessionIdChange?.(data.session_id)
        }

        // 添加AI响应到界面
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.response
        }])
      } else {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: `错误: ${data.error || '发送消息失败'}`
        }])
      }
    } catch (error) {
      console.error('发送消息失败:', error)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '抱歉，发送消息时出现错误，请稍后再试。'
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const resetConversation = async () => {
    if (!sessionId) return

    try {
      const response = await fetch('http://localhost:8000/api/jobs/ai-assistant/reset/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
        }),
      })

      const data = await response.json()

      if (data.success) {
        setMessages([])
      }
    } catch (error) {
      console.error('重置会话失败:', error)
    }
  }

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-gray-50 to-blue-50 rounded-lg shadow-xl overflow-hidden">
      {/* 聊天头部 */}
      <div className="flex items-center justify-between px-6 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <div>
          <h3 className="text-lg font-semibold flex items-center">
            <svg className="w-6 h-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            AI 职位推荐助手
          </h3>
          <p className="text-sm text-blue-100">为您推荐最合适的职位</p>
        </div>
        {sessionId && (
          <button
            onClick={resetConversation}
            className="px-4 py-2 text-sm bg-white/20 hover:bg-white/30 rounded-lg transition-all duration-200 flex items-center space-x-2"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span>重置对话</span>
          </button>
        )}
      </div>

      {/* 消息列表 */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6"
           style={{
             backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(59, 130, 246, 0.05) 1px, transparent 0)',
             backgroundSize: '40px 40px'
           }}>
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full text-gray-400">
            <div className="text-center bg-white rounded-2xl p-8 shadow-lg">
              <div className="mx-auto h-20 w-20 mb-4 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full flex items-center justify-center">
                <svg className="h-10 w-10 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <p className="text-xl font-semibold text-gray-700 mb-2">开始对话</p>
              <p className="text-sm text-gray-500">让AI为您推荐最合适的职位</p>
              <p className="text-xs text-gray-400 mt-3">您可以询问关于职位、薪资、技能等任何问题</p>
            </div>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg ${
                message.role === 'user'
                  ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white px-4 py-3'
                  : 'bg-white border border-gray-200 shadow-sm'
              }`}
            >
              {message.role === 'user' ? (
                <p className="whitespace-pre-wrap break-words">{message.content}</p>
              ) : (
                <div className="px-4 py-3">
                  <MarkdownMessage content={message.content} />
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-3">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* 输入框 */}
      <div className="px-6 py-4 bg-white border-t border-gray-200">
        <div className="flex space-x-4">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="输入您的问题... (Shift+Enter 换行)"
            className="flex-1 px-4 py-3 border-2 border-gray-200 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 hover:border-gray-300"
            rows={3}
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !inputMessage.trim()}
            className="px-8 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed transition-all duration-200 self-end font-medium shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 flex items-center space-x-2"
          >
            {isLoading ? (
              <>
                <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>发送中</span>
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
                <span>发送</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
