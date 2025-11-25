'use client';

import { useState } from 'react';

interface PredictionResult {
  predicted_salary: number;
  salary_min: number;
  salary_max: number;
  annual_salary: number;
  confidence: number;
}

export default function SalaryPredictionPage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [formData, setFormData] = useState({
    city: '北京',
    education: '本科',
    experience: '3-5年',
    industry: '互联网',
    company_size: '100-499人',
    company_type: '民营公司',
    salary_months: 13,
    skills: [] as string[],
    skillInput: '',
  });

  const cityOptions = ['北京', '上海', '深圳', '广州', '杭州', '成都', '武汉', '西安', '南京', '苏州'];
  const educationOptions = ['高中', '大专', '本科', '硕士', '博士'];
  const experienceOptions = ['应届生', '1年以下', '1-3年', '3-5年', '5-10年', '10年以上'];
  const industryOptions = ['互联网', '金融', '教育', '医疗', '制造业', '房地产', '零售', '其他'];
  const companySizeOptions = ['0-20人', '20-99人', '100-499人', '500-999人', '1000-9999人', '10000人以上'];
  const companyTypeOptions = ['民营公司', '外资企业', '国企', '合资', '上市公司', '创业公司'];

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleAddSkill = () => {
    if (formData.skillInput.trim() && !formData.skills.includes(formData.skillInput.trim())) {
      setFormData(prev => ({
        ...prev,
        skills: [...prev.skills, prev.skillInput.trim()],
        skillInput: '',
      }));
    }
  };

  const handleRemoveSkill = (skill: string) => {
    setFormData(prev => ({
      ...prev,
      skills: prev.skills.filter(s => s !== skill),
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/ml/predict-salary/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          city: formData.city,
          education: formData.education,
          experience: formData.experience,
          industry: formData.industry,
          company_size: formData.company_size,
          company_type: formData.company_type,
          salary_months: formData.salary_months,
          skills: formData.skills,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setResult(data);
      } else {
        const error = await response.json();
        alert(`预测失败: ${error.error || '未知错误'}`);
      }
    } catch (error) {
      console.error('预测失败:', error);
      alert('预测失败，请检查网络连接或稍后重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold mb-4">机器学习薪资预测</h1>
            <p className="text-xl text-blue-100">
              基于随机森林算法，智能分析职位特征，精准预测薪资范围
            </p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 左侧表单 */}
          <div className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">输入职位信息</h2>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* 城市 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  工作城市 <span className="text-red-500">*</span>
                </label>
                <select
                  value={formData.city}
                  onChange={(e) => handleInputChange('city', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  {cityOptions.map(city => (
                    <option key={city} value={city}>{city}</option>
                  ))}
                </select>
              </div>

              {/* 学历 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  学历要求 <span className="text-red-500">*</span>
                </label>
                <select
                  value={formData.education}
                  onChange={(e) => handleInputChange('education', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  {educationOptions.map(edu => (
                    <option key={edu} value={edu}>{edu}</option>
                  ))}
                </select>
              </div>

              {/* 工作经验 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  工作经验 <span className="text-red-500">*</span>
                </label>
                <select
                  value={formData.experience}
                  onChange={(e) => handleInputChange('experience', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  {experienceOptions.map(exp => (
                    <option key={exp} value={exp}>{exp}</option>
                  ))}
                </select>
              </div>

              {/* 行业 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  所属行业 <span className="text-red-500">*</span>
                </label>
                <select
                  value={formData.industry}
                  onChange={(e) => handleInputChange('industry', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  {industryOptions.map(ind => (
                    <option key={ind} value={ind}>{ind}</option>
                  ))}
                </select>
              </div>

              {/* 公司规模 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  公司规模
                </label>
                <select
                  value={formData.company_size}
                  onChange={(e) => handleInputChange('company_size', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  {companySizeOptions.map(size => (
                    <option key={size} value={size}>{size}</option>
                  ))}
                </select>
              </div>

              {/* 公司类型 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  公司类型
                </label>
                <select
                  value={formData.company_type}
                  onChange={(e) => handleInputChange('company_type', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  {companyTypeOptions.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>

              {/* 薪资月数 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  薪资月数（年薪计算用）
                </label>
                <input
                  type="number"
                  value={formData.salary_months}
                  onChange={(e) => handleInputChange('salary_months', parseInt(e.target.value))}
                  min="12"
                  max="24"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              {/* 技能标签 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  技能标签
                </label>
                <div className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={formData.skillInput}
                    onChange={(e) => handleInputChange('skillInput', e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddSkill())}
                    placeholder="输入技能后按回车添加"
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                  <button
                    type="button"
                    onClick={handleAddSkill}
                    className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg transition-colors"
                  >
                    添加
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.skills.map(skill => (
                    <span
                      key={skill}
                      className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                    >
                      {skill}
                      <button
                        type="button"
                        onClick={() => handleRemoveSkill(skill)}
                        className="hover:text-blue-600"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              {/* 提交按钮 */}
              <button
                type="submit"
                disabled={loading}
                className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-bold rounded-lg transition-colors"
              >
                {loading ? '预测中...' : '开始预测薪资'}
              </button>
            </form>
          </div>

          {/* 右侧结果 */}
          <div className="space-y-6">
            {/* 说明卡片 */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <div className="flex items-start">
                <svg className="h-6 w-6 text-blue-600 mt-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                <div className="ml-3">
                  <h3 className="text-lg font-medium text-blue-900">预测说明</h3>
                  <div className="mt-2 text-sm text-blue-700">
                    <p className="mb-2">我们的机器学习模型基于随机森林算法，综合分析以下因素：</p>
                    <ul className="list-disc list-inside space-y-1">
                      <li>工作地点的薪资水平</li>
                      <li>学历和工作经验要求</li>
                      <li>所属行业和公司规模</li>
                      <li>技能标签的市场价值</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            {/* 预测结果 */}
            {result && (
              <div className="bg-white rounded-lg shadow-lg p-8">
                <h3 className="text-2xl font-bold text-gray-900 mb-6">预测结果</h3>

                <div className="space-y-6">
                  {/* 月薪预测 */}
                  <div className="text-center p-6 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg">
                    <div className="text-sm text-gray-600 mb-2">预测月薪</div>
                    <div className="text-5xl font-bold text-blue-600 mb-2">
                      {Math.round(result.predicted_salary / 1000)}k
                    </div>
                    <div className="text-sm text-gray-600">
                      约 {result.predicted_salary.toLocaleString()} 元/月
                    </div>
                  </div>

                  {/* 薪资范围 */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-gray-50 rounded-lg text-center">
                      <div className="text-sm text-gray-600 mb-1">最低薪资</div>
                      <div className="text-2xl font-bold text-gray-700">
                        {Math.round(result.salary_min / 1000)}k
                      </div>
                    </div>
                    <div className="p-4 bg-gray-50 rounded-lg text-center">
                      <div className="text-sm text-gray-600 mb-1">最高薪资</div>
                      <div className="text-2xl font-bold text-gray-700">
                        {Math.round(result.salary_max / 1000)}k
                      </div>
                    </div>
                  </div>

                  {/* 年薪 */}
                  <div className="p-4 bg-purple-50 rounded-lg">
                    <div className="flex justify-between items-center">
                      <div className="text-sm text-gray-700">预估年薪</div>
                      <div className="text-2xl font-bold text-purple-600">
                        {result.annual_salary} 万元
                      </div>
                    </div>
                  </div>

                  {/* 置信度 */}
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm text-gray-700">预测置信度</span>
                      <span className="text-sm font-medium text-gray-900">
                        {(result.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-green-500 h-2 rounded-full transition-all"
                        style={{ width: `${result.confidence * 100}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* 提示 */}
                  <div className="text-xs text-gray-500 text-center">
                    * 预测结果仅供参考，实际薪资可能因公司和岗位而异
                  </div>
                </div>
              </div>
            )}

            {/* 加载状态 */}
            {loading && (
              <div className="bg-white rounded-lg shadow-lg p-8 flex flex-col items-center justify-center">
                <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mb-4"></div>
                <p className="text-gray-600">正在分析数据，预测薪资中...</p>
              </div>
            )}

            {/* 初始提示 */}
            {!result && !loading && (
              <div className="bg-white rounded-lg shadow-lg p-8 text-center">
                <svg className="h-24 w-24 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
                <p className="text-gray-500">
                  填写左侧表单，点击预测按钮，即可获得薪资预测结果
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
