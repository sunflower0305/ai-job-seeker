'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface Statistics {
  users: {
    total: number;
    normal_users: number;
    admins: number;
  };
  jobs: {
    total: number;
    active: number;
  };
  companies: {
    total: number;
  };
  applications: {
    total: number;
  };
  recent_users: Array<{
    id: number;
    username: string;
    email: string;
    role: string;
    created_at: string;
  }>;
}

interface AnalyticsData {
  access_trend: Array<{ date: string; count: number }>;
  ai_call_trend: Array<{ date: string; count: number }>;
  ai_type_distribution: Array<{ type: string; name: string; count: number }>;
  token_stats: {
    total_prompt_tokens: number;
    total_completion_tokens: number;
    total_tokens: number;
    total_calls: number;
    success_calls: number;
  };
  user_register_trend: Array<{ date: string; count: number }>;
  top_active_users: Array<{ username: string; access_count: number }>;
  top_ai_users: Array<{ username: string; call_count: number; total_tokens: number }>;
  response_time_trend: Array<{ date: string; avg_time: number }>;
  date_range: {
    start: string;
    end: string;
    days: number;
  };
}

interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  phone: string;
  created_at: string;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82ca9d'];

export default function AdminDashboard() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [currentView, setCurrentView] = useState<'dashboard' | 'users' | 'analytics'>('dashboard');
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [dayRange, setDayRange] = useState(30);

  // 检查用户权限
  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('token');
      const userStr = localStorage.getItem('user');

      if (!token || !userStr) {
        router.push('/login');
        return false;
      }

      const user = JSON.parse(userStr);
      if (user.role !== 'admin') {
        alert('您没有权限访问此页面');
        router.push('/');
        return false;
      }

      return true;
    };

    if (checkAuth()) {
      fetchStatistics();
      fetchAnalytics();
    }
  }, [router]);

  // 获取统计数据
  const fetchStatistics = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/users/admin/statistics/', {
        headers: {
          'Authorization': `Token ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setStatistics(data);
      }
    } catch (error) {
      console.error('获取统计数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 获取分析数据
  const fetchAnalytics = async (days = 30) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/users/admin/analytics/?days=${days}`, {
        headers: {
          'Authorization': `Token ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      }
    } catch (error) {
      console.error('获取分析数据失败:', error);
    }
  };

  // 获取用户列表
  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem('token');
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      if (roleFilter) params.append('role', roleFilter);

      const response = await fetch(`http://localhost:8000/api/users/admin/users/?${params}`, {
        headers: {
          'Authorization': `Token ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUsers(data.users);
      }
    } catch (error) {
      console.error('获取用户列表失败:', error);
    }
  };

  // 删除用户
  const handleDeleteUser = async (userId: number) => {
    if (!confirm('确定要删除此用户吗？')) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/users/admin/users/', {
        method: 'DELETE',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: userId }),
      });

      if (response.ok) {
        alert('用户删除成功');
        fetchUsers();
        fetchStatistics();
      } else {
        const error = await response.json();
        alert(error.error || '删除失败');
      }
    } catch (error) {
      console.error('删除用户失败:', error);
      alert('删除用户失败');
    }
  };

  useEffect(() => {
    if (currentView === 'users') {
      fetchUsers();
    }
  }, [currentView, searchTerm, roleFilter]);

  useEffect(() => {
    if (currentView === 'analytics') {
      fetchAnalytics(dayRange);
    }
  }, [dayRange]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">加载中...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 页面标题栏 */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">管理员后台</h1>
              <p className="mt-1 text-sm text-gray-500">系统管理和数据统计</p>
            </div>
            <div className="flex space-x-4">
              <button
                onClick={() => setCurrentView('dashboard')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  currentView === 'dashboard'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                统计概览
              </button>
              <button
                onClick={() => setCurrentView('analytics')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  currentView === 'analytics'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                数据分析
              </button>
              <button
                onClick={() => setCurrentView('users')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  currentView === 'users'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                用户管理
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* 统计概览 */}
        {currentView === 'dashboard' && statistics && (
          <div>
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <svg className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                      </svg>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">总用户数</dt>
                        <dd className="text-lg font-medium text-gray-900">{statistics.users.total}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <svg className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">职位总数</dt>
                        <dd className="text-lg font-medium text-gray-900">{statistics.jobs.total}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <svg className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                      </svg>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">公司数量</dt>
                        <dd className="text-lg font-medium text-gray-900">{statistics.companies.total}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <svg className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">申请总数</dt>
                        <dd className="text-lg font-medium text-gray-900">{statistics.applications.total}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* 最近注册用户 */}
            <div className="mt-8 bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:px-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900">最近注册用户</h3>
              </div>
              <div className="border-t border-gray-200">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">用户名</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">邮箱</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">角色</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">注册时间</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {statistics.recent_users.map((user) => (
                      <tr key={user.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{user.username}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{user.email}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            user.role === 'admin' ? 'bg-purple-100 text-purple-800' : 'bg-green-100 text-green-800'
                          }`}>
                            {user.role === 'admin' ? '管理员' : '用户'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(user.created_at).toLocaleString('zh-CN')}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* 数据分析 */}
        {currentView === 'analytics' && analytics && (
          <div className="space-y-6">
            {/* 时间范围选择 */}
            <div className="bg-white shadow rounded-lg p-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900">数据分析</h3>
                <div className="flex items-center gap-4">
                  <span className="text-sm text-gray-500">时间范围:</span>
                  <select
                    value={dayRange}
                    onChange={(e) => setDayRange(Number(e.target.value))}
                    className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value={7}>最近7天</option>
                    <option value={30}>最近30天</option>
                    <option value={90}>最近90天</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Token使用统计卡片 */}
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
              <div className="bg-white overflow-hidden shadow rounded-lg p-5">
                <div className="text-sm font-medium text-gray-500">AI调用总数</div>
                <div className="mt-2 text-3xl font-bold text-blue-600">
                  {analytics.token_stats.total_calls || 0}
                </div>
              </div>
              <div className="bg-white overflow-hidden shadow rounded-lg p-5">
                <div className="text-sm font-medium text-gray-500">成功调用</div>
                <div className="mt-2 text-3xl font-bold text-green-600">
                  {analytics.token_stats.success_calls || 0}
                </div>
              </div>
              <div className="bg-white overflow-hidden shadow rounded-lg p-5">
                <div className="text-sm font-medium text-gray-500">总Token数</div>
                <div className="mt-2 text-3xl font-bold text-purple-600">
                  {(analytics.token_stats.total_tokens || 0).toLocaleString()}
                </div>
              </div>
              <div className="bg-white overflow-hidden shadow rounded-lg p-5">
                <div className="text-sm font-medium text-gray-500">成功率</div>
                <div className="mt-2 text-3xl font-bold text-orange-600">
                  {analytics.token_stats.total_calls
                    ? ((analytics.token_stats.success_calls / analytics.token_stats.total_calls) * 100).toFixed(1)
                    : 0}%
                </div>
              </div>
            </div>

            {/* 用户访问趋势 */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">用户访问趋势</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={analytics.access_trend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="count" name="访问次数" stroke="#8884d8" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* AI调用趋势 */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">AI调用趋势</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={analytics.ai_call_trend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="count" name="调用次数" stroke="#82ca9d" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* 用户注册趋势 */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">用户注册趋势</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={analytics.user_register_trend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="count" name="注册人数" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* AI调用类型分布 和 响应时间趋势 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">AI调用类型分布</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={analytics.ai_type_distribution}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="count"
                    >
                      {analytics.ai_type_distribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">平均响应时间趋势</h3>
                {analytics.response_time_trend.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={analytics.response_time_trend}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="avg_time" name="响应时间(秒)" stroke="#ff7300" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-[300px] text-gray-500">
                    暂无数据
                  </div>
                )}
              </div>
            </div>

            {/* 最活跃用户 和 AI调用最多的用户 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">最活跃用户（访问次数）</h3>
                <div className="space-y-3">
                  {analytics.top_active_users.length > 0 ? (
                    analytics.top_active_users.map((user, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center gap-3">
                          <span className="text-lg font-bold text-gray-400">#{index + 1}</span>
                          <span className="font-medium text-gray-900">{user.username}</span>
                        </div>
                        <span className="text-blue-600 font-semibold">{user.access_count} 次</span>
                      </div>
                    ))
                  ) : (
                    <div className="text-center text-gray-500 py-8">暂无数据</div>
                  )}
                </div>
              </div>

              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">AI调用最多的用户</h3>
                <div className="space-y-3">
                  {analytics.top_ai_users.length > 0 ? (
                    analytics.top_ai_users.map((user, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center gap-3">
                          <span className="text-lg font-bold text-gray-400">#{index + 1}</span>
                          <span className="font-medium text-gray-900">{user.username}</span>
                        </div>
                        <div className="text-right">
                          <div className="text-green-600 font-semibold">{user.call_count} 次</div>
                          <div className="text-xs text-gray-500">{user.total_tokens.toLocaleString()} tokens</div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center text-gray-500 py-8">暂无数据</div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 用户管理 */}
        {currentView === 'users' && (
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:px-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900">用户管理</h3>

              {/* 搜索和筛选 */}
              <div className="mt-4 flex gap-4">
                <input
                  type="text"
                  placeholder="搜索用户名、邮箱或手机号"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <select
                  value={roleFilter}
                  onChange={(e) => setRoleFilter(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">全部角色</option>
                  <option value="user">用户</option>
                  <option value="admin">管理员</option>
                </select>
              </div>
            </div>

            <div className="border-t border-gray-200">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">用户名</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">邮箱</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">角色</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">注册时间</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {users.map((user) => (
                    <tr key={user.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{user.id}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{user.username}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{user.email}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          user.role === 'admin' ? 'bg-purple-100 text-purple-800' : 'bg-green-100 text-green-800'
                        }`}>
                          {user.role === 'admin' ? '管理员' : '用户'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(user.created_at).toLocaleString('zh-CN')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        {user.role !== 'admin' && (
                          <button
                            onClick={() => handleDeleteUser(user.id)}
                            className="text-red-600 hover:text-red-900"
                          >
                            删除
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
