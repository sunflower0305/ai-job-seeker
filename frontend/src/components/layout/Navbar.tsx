'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isAnalyticsOpen, setIsAnalyticsOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userRole, setUserRole] = useState<'user' | 'admin' | null>(null);
  const [username, setUsername] = useState('');

  // 检查登录状态
  useEffect(() => {
    const token = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');

    if (token && userStr) {
      try {
        const user = JSON.parse(userStr);
        setIsLoggedIn(true);
        setUserRole(user.role);
        setUsername(user.username);
      } catch (error) {
        console.error('解析用户信息失败:', error);
      }
    }
  }, []);

  // 退出登录
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setIsLoggedIn(false);
    setUserRole(null);
    setUsername('');
    router.push('/');
  };

  const navItems = [
    { name: '首页', path: '/' },
    { name: '职位列表', path: '/jobs' },
    { name: '薪资预测', path: '/recommendations' },
    { name: 'AI推荐', path: '/ai-recommend' },
    { name: '我的收藏', path: '/collections' },
  ];

  const analyticsItems = [
    { name: '数据分析概览', path: '/analytics' },
    { name: '数据大屏', path: '/dashboard-screen' },
    { name: '薪资分析', path: '/analytics/salary' },
    { name: '技能词云', path: '/analytics/wordcloud' },
    { name: '城市分析', path: '/analytics/city' },
    { name: '公司分析', path: '/analytics/company' },
  ];

  return (
    <nav className="bg-white shadow-lg sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo 和主导航 */}
          <div className="flex">
            <Link href="/" className="flex items-center">
              <div className="flex-shrink-0 flex items-center">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-xl">职</span>
                </div>
                <span className="ml-3 text-xl font-bold text-gray-900">
                  职位推荐平台
                </span>
              </div>
            </Link>

            {/* 桌面端导航 */}
            <div className="hidden md:ml-10 md:flex md:space-x-8">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  href={item.path}
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors ${
                    pathname === item.path
                      ? 'border-blue-500 text-gray-900'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                  }`}
                >
                  {item.name}
                </Link>
              ))}
              {/* 数据分析下拉菜单 */}
              <div className="relative inline-flex items-center"
                onMouseEnter={() => setIsAnalyticsOpen(true)}
                onMouseLeave={() => setIsAnalyticsOpen(false)}
              >
                <button
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors h-16 ${
                    pathname.startsWith('/analytics') || pathname.startsWith('/dashboard-screen')
                      ? 'border-blue-500 text-gray-900'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                  }`}
                >
                  数据分析
                  <svg className="ml-1 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                {isAnalyticsOpen && (
                  <div className="absolute left-0 top-full mt-0 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5">
                    <div className="py-1">
                      {analyticsItems.map((item) => (
                        <Link
                          key={item.path}
                          href={item.path}
                          className={`block px-4 py-2 text-sm transition-colors ${
                            pathname === item.path
                              ? 'bg-blue-50 text-blue-700 font-medium'
                              : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                          }`}
                        >
                          {item.name}
                        </Link>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* 右侧按钮 */}
          <div className="hidden md:flex md:items-center md:space-x-4">
            {isLoggedIn ? (
              <>
                <span className="text-gray-700 text-sm">
                  欢迎, {username}
                  {userRole === 'admin' && (
                    <span className="ml-2 px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded-full">
                      管理员
                    </span>
                  )}
                </span>
                {userRole === 'admin' && (
                  <Link
                    href="/admin"
                    className="text-purple-700 hover:text-purple-900 px-3 py-2 rounded-md text-sm font-medium"
                  >
                    管理后台
                  </Link>
                )}
                <Link
                  href="/profile"
                  className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                >
                  个人中心
                </Link>
                <button
                  onClick={handleLogout}
                  className="bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                >
                  退出登录
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                >
                  登录
                </Link>
                <Link
                  href="/register"
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                >
                  注册
                </Link>
              </>
            )}
          </div>

          {/* 移动端菜单按钮 */}
          <div className="flex items-center md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
            >
              <svg
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                {isMenuOpen ? (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                ) : (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                )}
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* 移动端菜单 */}
      {isMenuOpen && (
        <div className="md:hidden border-t border-gray-200">
          <div className="pt-2 pb-3 space-y-1">
            {navItems.map((item) => (
              <Link
                key={item.path}
                href={item.path}
                className={`block pl-3 pr-4 py-2 border-l-4 text-base font-medium ${
                  pathname === item.path
                    ? 'bg-blue-50 border-blue-500 text-blue-700'
                    : 'border-transparent text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800'
                }`}
                onClick={() => setIsMenuOpen(false)}
              >
                {item.name}
              </Link>
            ))}
            {/* 数据分析下拉菜单 - 移动端 */}
            <div>
              <button
                onClick={() => setIsAnalyticsOpen(!isAnalyticsOpen)}
                className={`w-full flex justify-between items-center pl-3 pr-4 py-2 border-l-4 text-base font-medium ${
                  pathname.startsWith('/analytics')
                    ? 'bg-blue-50 border-blue-500 text-blue-700'
                    : 'border-transparent text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800'
                }`}
              >
                数据分析
                <svg className={`w-5 h-5 transition-transform ${isAnalyticsOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              {isAnalyticsOpen && (
                <div className="bg-gray-50">
                  {analyticsItems.map((item) => (
                    <Link
                      key={item.path}
                      href={item.path}
                      className={`block pl-8 pr-4 py-2 text-sm ${
                        pathname === item.path
                          ? 'text-blue-700 font-medium bg-blue-50'
                          : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
                      }`}
                      onClick={() => {
                        setIsMenuOpen(false);
                        setIsAnalyticsOpen(false);
                      }}
                    >
                      {item.name}
                    </Link>
                  ))}
                </div>
              )}
            </div>
          </div>
          <div className="pt-4 pb-3 border-t border-gray-200">
            {isLoggedIn ? (
              <div className="space-y-1">
                <div className="px-4 py-2 text-base font-medium text-gray-800">
                  {username}
                  {userRole === 'admin' && (
                    <span className="ml-2 px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded-full">
                      管理员
                    </span>
                  )}
                </div>
                {userRole === 'admin' && (
                  <Link
                    href="/admin"
                    className="block px-4 py-2 text-base font-medium text-purple-700 hover:text-purple-900 hover:bg-gray-100"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    管理后台
                  </Link>
                )}
                <Link
                  href="/profile"
                  className="block px-4 py-2 text-base font-medium text-gray-600 hover:text-gray-800 hover:bg-gray-100"
                  onClick={() => setIsMenuOpen(false)}
                >
                  个人中心
                </Link>
                <button
                  onClick={() => {
                    handleLogout();
                    setIsMenuOpen(false);
                  }}
                  className="block w-full text-left px-4 py-2 text-base font-medium text-gray-600 hover:text-gray-800 hover:bg-gray-100"
                >
                  退出登录
                </button>
              </div>
            ) : (
              <div className="space-y-1 px-4">
                <Link
                  href="/login"
                  className="block px-4 py-2 text-center text-gray-700 hover:text-gray-900 border border-gray-300 rounded-lg"
                  onClick={() => setIsMenuOpen(false)}
                >
                  登录
                </Link>
                <Link
                  href="/register"
                  className="block px-4 py-2 text-center bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
                  onClick={() => setIsMenuOpen(false)}
                >
                  注册
                </Link>
              </div>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}
