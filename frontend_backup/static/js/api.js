/**
 * API客户端
 * 与Django后端API通信
 */

const API_BASE_URL = 'http://localhost:8000/api';

class APIClient {
    constructor() {
        this.token = localStorage.getItem('authToken');
    }

    // 通用请求方法
    async request(url, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.token) {
            headers['Authorization'] = `Token ${this.token}`;
        }

        try {
            const response = await fetch(`${API_BASE_URL}${url}`, {
                ...options,
                headers
            });

            if (response.status === 401) {
                this.logout();
                throw new Error('请先登录');
            }

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || error.detail || '请求失败');
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // GET请求
    get(url, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const fullUrl = queryString ? `${url}?${queryString}` : url;
        return this.request(fullUrl);
    }

    // POST请求
    post(url, data) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // PUT请求
    put(url, data) {
        return this.request(url, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    // DELETE请求
    delete(url) {
        return this.request(url, {
            method: 'DELETE'
        });
    }

    // ===== 用户相关 =====

    // 注册
    async register(userData) {
        const response = await this.post('/users/register/', userData);
        this.token = response.token;
        localStorage.setItem('authToken', this.token);
        localStorage.setItem('user', JSON.stringify(response.user));
        return response;
    }

    // 登录
    async login(username, password) {
        const response = await this.post('/users/login/', { username, password });
        this.token = response.token;
        localStorage.setItem('authToken', this.token);
        localStorage.setItem('user', JSON.stringify(response.user));
        return response;
    }

    // 登出
    logout() {
        this.token = null;
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
        window.location.href = '/frontend/templates/login.html';
    }

    // 获取当前用户
    getCurrentUser() {
        return this.get('/users/me/');
    }

    // 获取用户档案
    getUserProfile() {
        return this.get('/users/me/profile/');
    }

    // 更新用户档案
    updateUserProfile(profileData) {
        return this.put('/users/me/profile/', profileData);
    }

    // ===== 职位相关 =====

    // 获取职位列表
    getJobs(filters = {}) {
        return this.get('/jobs/jobs/', filters);
    }

    // 获取职位详情
    getJobDetail(jobId) {
        return this.get(`/jobs/jobs/${jobId}/`);
    }

    // 申请职位
    applyJob(jobId, coverLetter = '') {
        return this.post(`/jobs/jobs/${jobId}/apply/`, { cover_letter: coverLetter });
    }

    // 收藏职位
    collectJob(jobId) {
        return this.post(`/jobs/jobs/${jobId}/collect/`);
    }

    // 取消收藏
    uncollectJob(jobId) {
        return this.delete(`/jobs/jobs/${jobId}/collect/`);
    }

    // 获取我的申请
    getMyApplications() {
        return this.get('/jobs/applications/');
    }

    // 获取我的收藏
    getMyCollections() {
        return this.get('/jobs/collections/');
    }

    // ===== 机器学习相关 =====

    // 职位推荐
    recommendJobs(userProfile) {
        return this.post('/ml/recommend/', userProfile);
    }

    // 薪资预测
    predictSalary(jobFeatures) {
        return this.post('/ml/predict-salary/', jobFeatures);
    }

    // 获取模型状态
    getModelStatus() {
        return this.get('/ml/model-status/');
    }

    // 获取推荐历史
    getRecommendationHistory() {
        return this.get('/ml/recommendation-history/');
    }

    // 获取预测历史
    getPredictionHistory() {
        return this.get('/ml/prediction-history/');
    }

    // ===== 工具方法 =====

    // 检查是否已登录
    isAuthenticated() {
        return !!this.token;
    }

    // 获取存储的用户信息
    getStoredUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    }
}

// 创建全局API实例
const api = new APIClient();

// 工具函数：显示提示信息
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;

    const container = document.querySelector('.container') || document.body;
    container.insertBefore(alertDiv, container.firstChild);

    setTimeout(() => alertDiv.remove(), 5000);
}

// 工具函数：显示加载状态
function showLoading(element) {
    element.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
}

// 工具函数：格式化薪资
function formatSalary(min, max) {
    if (min >= 10000 && max >= 10000) {
        return `${(min / 1000).toFixed(0)}-${(max / 1000).toFixed(0)}K`;
    }
    return `${min}-${max}元`;
}

// 工具函数：格式化日期
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) return '今天';
    if (days === 1) return '昨天';
    if (days < 7) return `${days}天前`;
    if (days < 30) return `${Math.floor(days / 7)}周前`;
    return date.toLocaleDateString('zh-CN');
}

// 检查登录状态
function checkAuth() {
    if (!api.isAuthenticated()) {
        window.location.href = '/frontend/templates/login.html';
        return false;
    }
    return true;
}

// 更新导航栏用户信息
function updateNavbar() {
    const user = api.getStoredUser();
    const navbarUser = document.querySelector('.navbar-user');

    if (user && navbarUser) {
        navbarUser.innerHTML = `
            <span>欢迎, ${user.username}</span>
            <button class="btn btn-outline btn-small" onclick="api.logout()">登出</button>
        `;
    }
}
