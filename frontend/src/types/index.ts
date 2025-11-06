export interface Job {
  id: number;
  title: string;
  company: string;
  location: string;
  description: string;
  employment_type?: string;
  seniority_level?: string;
  linkedin_url: string;
  requires_english: boolean;
  match_score: number;
  posted_date?: string;
  scraped_at: string;
}

export interface JobSearchParams {
  search_term: string;
  location: string;
  max_jobs: number;
}

export interface JobStats {
  total_jobs: number;
  jobs_without_english: number;
  english_percentage: number;
  top_companies: Array<{ name: string; count: number }>;
  top_locations: Array<{ name: string; count: number }>;
}

export interface User {
  id: number;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_verified: boolean;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface ScrapeResponse {
  success: boolean;
  jobs_found: number;
  jobs_saved: number;
  jobs_without_english: number;
  message: string;
}