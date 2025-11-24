// 职位相关类型
export interface Job {
  id: number;
  title: string;
  company: string | Company;
  company_id?: number;
  location: string;
  city?: string;
  district?: string;
  salary_min?: number;
  salary_max?: number;
  salary: string;
  experience: string;
  education: string;
  job_type?: string;
  description?: string;
  requirements?: string;
  responsibilities?: string;
  benefits?: string;
  welfare?: string;
  tags?: string[];
  created_at?: string;
  updated_at?: string;
  publish_date?: string;
  url?: string;
}

// 公司类型
export interface Company {
  id: number;
  name: string;
  industry?: string;
  scale?: string;
  company_type?: string;
  company_size?: string;
  description?: string;
  location?: string;
  website?: string;
}

// 用户类型
export interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  avatar?: string;
}

// 推荐类型
export interface Recommendation {
  id: number;
  user_id: number;
  job: Job;
  score: number;
  reason?: string;
  created_at: string;
}

// 收藏类型
export interface Collection {
  id: number;
  user_id: number;
  job_id: number;
  job?: Job;
  created_at: string;
}

// 申请类型
export interface Application {
  id: number;
  user_id: number;
  job_id: number;
  job?: Job;
  status: 'pending' | 'accepted' | 'rejected';
  applied_at: string;
  updated_at?: string;
}

// API响应类型
export interface ApiResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// 搜索过滤参数
export interface JobFilters {
  search?: string;
  location?: string;
  salary_min?: number;
  salary_max?: number;
  experience?: string;
  education?: string;
  job_type?: string;
  company?: string;
}
