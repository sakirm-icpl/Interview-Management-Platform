import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/api/auth/token/refresh/`, {
            refresh: refreshToken,
          });

          const { access } = response.data;
          localStorage.setItem('access_token', access);

          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

export interface LoginResponse {
  access: string;
  refresh: string;
  user: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    role: string;
    is_verified: boolean;
  };
}

export interface RegisterData {
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  password: string;
  password_confirm: string;
  phone_number?: string;
  role?: string;
}

export const authService = {
  async login(email: string, password: string): Promise<LoginResponse> {
    const response = await api.post('/auth/login/', { email, password });
    return response.data;
  },

  async register(userData: RegisterData): Promise<void> {
    await api.post('/v1/users/users/register/', userData);
  },

  async getCurrentUser() {
    const response = await api.get('/v1/users/users/me/');
    return response.data;
  },

  async changePassword(oldPassword: string, newPassword: string, newPasswordConfirm: string) {
    await api.post('/v1/users/users/change_password/', {
      old_password: oldPassword,
      new_password: newPassword,
      new_password_confirm: newPasswordConfirm,
    });
  },

  async requestPasswordReset(email: string) {
    await api.post('/v1/users/users/request_password_reset/', { email });
  },

  async resetPassword(token: string, newPassword: string, newPasswordConfirm: string) {
    await api.post('/v1/users/users/reset_password/', {
      token,
      new_password: newPassword,
      new_password_confirm: newPasswordConfirm,
    });
  },

  async verifyEmail(token: string) {
    await api.post('/v1/users/users/verify_email/', { token });
  },

  async updateProfile(userData: Partial<any>) {
    const response = await api.patch('/v1/users/users/me/', userData);
    return response.data;
  },

  async refreshToken(refreshToken: string) {
    const response = await api.post('/auth/token/refresh/', { refresh: refreshToken });
    return response.data;
  },
};