'use client'

import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import rehypeRaw from 'rehype-raw'
import 'highlight.js/styles/github-dark.css'

interface MarkdownMessageProps {
  content: string
  className?: string
}

export default function MarkdownMessage({ content, className = '' }: MarkdownMessageProps) {
  return (
    <div className={`markdown-body ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight, rehypeRaw]}
        components={{
          // 标题样式
          h1: ({ node, ...props }) => (
            <h1 className="text-2xl font-bold mb-4 mt-6 pb-2 border-b-2 border-gray-300" {...props} />
          ),
          h2: ({ node, ...props }) => (
            <h2 className="text-xl font-bold mb-3 mt-5 pb-2 border-b border-gray-200" {...props} />
          ),
          h3: ({ node, ...props }) => (
            <h3 className="text-lg font-semibold mb-2 mt-4" {...props} />
          ),
          h4: ({ node, ...props }) => (
            <h4 className="text-base font-semibold mb-2 mt-3" {...props} />
          ),

          // 段落样式
          p: ({ node, ...props }) => (
            <p className="mb-3 leading-7 text-gray-700" {...props} />
          ),

          // 列表样式
          ul: ({ node, ...props }) => (
            <ul className="mb-4 ml-6 list-disc space-y-2" {...props} />
          ),
          ol: ({ node, ...props }) => (
            <ol className="mb-4 ml-6 list-decimal space-y-2" {...props} />
          ),
          li: ({ node, ...props }) => (
            <li className="text-gray-700 leading-7" {...props} />
          ),

          // 代码块样式
          code: ({ node, inline, className, children, ...props }: any) => {
            if (inline) {
              return (
                <code
                  className="px-1.5 py-0.5 bg-gray-100 text-red-600 rounded text-sm font-mono"
                  {...props}
                >
                  {children}
                </code>
              )
            }
            return (
              <code
                className={`block p-4 bg-gray-900 text-gray-100 rounded-lg overflow-x-auto text-sm font-mono ${className || ''}`}
                {...props}
              >
                {children}
              </code>
            )
          },
          pre: ({ node, ...props }) => (
            <pre className="mb-4 overflow-x-auto" {...props} />
          ),

          // 表格样式
          table: ({ node, ...props }) => (
            <div className="mb-4 overflow-x-auto">
              <table className="min-w-full border-collapse border border-gray-300" {...props} />
            </div>
          ),
          thead: ({ node, ...props }) => (
            <thead className="bg-gray-100" {...props} />
          ),
          tbody: ({ node, ...props }) => (
            <tbody className="divide-y divide-gray-200" {...props} />
          ),
          tr: ({ node, ...props }) => (
            <tr className="hover:bg-gray-50 transition-colors" {...props} />
          ),
          th: ({ node, ...props }) => (
            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700 border border-gray-300" {...props} />
          ),
          td: ({ node, ...props }) => (
            <td className="px-4 py-3 text-sm text-gray-700 border border-gray-300" {...props} />
          ),

          // 引用块样式
          blockquote: ({ node, ...props }) => (
            <blockquote className="mb-4 pl-4 border-l-4 border-blue-500 bg-blue-50 py-2 pr-4 italic text-gray-700" {...props} />
          ),

          // 链接样式
          a: ({ node, ...props }) => (
            <a className="text-blue-600 hover:text-blue-800 underline" target="_blank" rel="noopener noreferrer" {...props} />
          ),

          // 分割线样式
          hr: ({ node, ...props }) => (
            <hr className="my-6 border-t-2 border-gray-300" {...props} />
          ),

          // 强调样式
          strong: ({ node, ...props }) => (
            <strong className="font-bold text-gray-900" {...props} />
          ),
          em: ({ node, ...props }) => (
            <em className="italic text-gray-700" {...props} />
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}
