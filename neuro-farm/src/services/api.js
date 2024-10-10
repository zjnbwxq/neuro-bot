import axios from 'axios';

const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:3000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const setAuthToken = (token) => {
  if (token) {
    api.defaults.headers.common['x-auth-token'] = token;
  } else {
    delete api.defaults.headers.common['x-auth-token'];
  }
};

export default {
  async register(email, password) {
    try {
      const response = await api.post('/auth/register', { email, password });
      return response.data;
    } catch (error) {
      throw error.response ? error.response.data : { message: '注册失败' };
    }
  },

  async login(email, password) {
    try {
      const response = await api.post('/auth/login', { email, password });
      if (response && response.data && response.data.token) {
        setAuthToken(response.data.token);
        localStorage.setItem('token', response.data.token);
        return response.data;
      } else {
        throw new Error('登录响应中没有token');
      }
    } catch (error) {
      console.error('API login error:', error); // 添加详细的错误日志
      throw error.response ? error.response.data : { message: '登录失败' };
    }
  },

  async getUserProfile() {
    try {
      const response = await api.get('/user/profile');
      return response.data;
    } catch (error) {
      throw error.response.data;
    }
  },

  // 可以在这里添加更多 API 调用函数
};

// 删除这些重复的导出
// export const register = ...
// export const login = ...
// export const getUserProfile = ...
