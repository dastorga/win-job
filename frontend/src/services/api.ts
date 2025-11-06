import axios from 'axios';
import { 
  Job, 
  JobSearchParams, 
  JobStats, 
  LoginCredentials, 
  RegisterData, 
  AuthResponse, 
  User,
  ScrapeResponse 
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  register: async (userData: RegisterData): Promise<User> => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/users/me');
    return response.data;
  },
};

// Jobs API
export const jobsAPI = {
  getJobs: async (params: {
    skip?: number;
    limit?: number;
    search?: string;
    no_english?: boolean;
    company?: string;
    location?: string;
  } = {}): Promise<Job[]> => {
    const response = await api.get('/jobs/', { params });
    return response.data;
  },

  getJob: async (jobId: number): Promise<Job> => {
    const response = await api.get(`/jobs/${jobId}`);
    return response.data;
  },

  getJobStats: async (): Promise<JobStats> => {
    const response = await api.get('/jobs/stats/summary');
    return response.data;
  },

  scrapeJobs: async (params: JobSearchParams): Promise<ScrapeResponse> => {
    const response = await api.post('/jobs/scrape', params);
    return response.data;
  },
};

export default api;