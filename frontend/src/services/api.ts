import axios, { type AxiosInstance, type AxiosResponse } from 'axios'
import type { 
  Event, 
  Category, 
  Tag, 
  Review, 
  ReviewListResponse,
  ReviewStats,
  ReviewCreate,
  ReviewUpdate,
  ReviewReport,
  User,
  UserUpdate,
  PasswordChange,
  PasswordResetRequest,
  PasswordReset,
  ApiResponse, 
  PaginatedResponse,
  EventFilters,
  LoginCredentials,
  RegisterCredentials,
  AuthResponse
} from '@/types'

class ApiService {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
      timeout: parseInt(import.meta.env.VITE_API_TIMEOUT) || 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token')
          localStorage.removeItem('user')
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  // Events API
  async getEvents(filters?: EventFilters): Promise<PaginatedResponse<Event>> {
    const response: AxiosResponse<PaginatedResponse<Event>> = await this.client.get('/events', {
      params: filters
    })
    return response.data
  }

  async getEvent(id: number): Promise<Event> {
    const response: AxiosResponse<ApiResponse<Event>> = await this.client.get(`/events/${id}`)
    return response.data.data
  }

  async createEvent(event: Partial<Event>): Promise<Event> {
    const response: AxiosResponse<ApiResponse<Event>> = await this.client.post('/events', event)
    return response.data.data
  }

  async updateEvent(id: number, event: Partial<Event>): Promise<Event> {
    const response: AxiosResponse<ApiResponse<Event>> = await this.client.put(`/events/${id}`, event)
    return response.data.data
  }

  async deleteEvent(id: number): Promise<void> {
    await this.client.delete(`/events/${id}`)
  }

  // Categories API
  async getCategories(): Promise<Category[]> {
    const response: AxiosResponse<ApiResponse<Category[]>> = await this.client.get('/categories')
    return response.data.data
  }

  // Tags API
  async getTags(): Promise<Tag[]> {
    const response: AxiosResponse<ApiResponse<Tag[]>> = await this.client.get('/tags')
    return response.data.data
  }

  // Authentication API
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    // Convert to FormData as backend expects OAuth2PasswordRequestForm
    const formData = new FormData()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)
    
    const response: AxiosResponse<AuthResponse> = await this.client.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
    return response.data
  }

  async register(credentials: RegisterCredentials): Promise<User> {
    const response: AxiosResponse<User> = await this.client.post('/auth/register', credentials)
    return response.data
  }

  async logout(): Promise<void> {
    await this.client.post('/auth/logout')
  }

  async getCurrentUser(): Promise<User> {
    const response: AxiosResponse<User> = await this.client.get('/auth/me')
    return response.data
  }

  async updateProfile(userData: UserUpdate): Promise<User> {
    const response: AxiosResponse<User> = await this.client.put('/auth/me', userData)
    return response.data
  }

  async changePassword(passwordData: PasswordChange): Promise<{ message: string }> {
    const response: AxiosResponse<{ message: string }> = await this.client.post('/auth/change-password', passwordData)
    return response.data
  }

  async requestPasswordReset(data: PasswordResetRequest): Promise<{ message: string }> {
    const response: AxiosResponse<{ message: string }> = await this.client.post('/auth/forgot-password', data)
    return response.data
  }

  async resetPassword(data: PasswordReset): Promise<{ message: string }> {
    const response: AxiosResponse<{ message: string }> = await this.client.post('/auth/reset-password', data)
    return response.data
  }

  async refreshToken(refresh_token: string): Promise<AuthResponse> {
    const response: AxiosResponse<AuthResponse> = await this.client.post('/auth/refresh', { refresh_token })
    return response.data
  }

  // Reviews API
  async getEventReviews(eventId: number, params?: {
    skip?: number
    limit?: number
    sort_by?: 'created_at' | 'rating' | 'helpful'
    sort_order?: 'asc' | 'desc'
  }): Promise<ReviewListResponse> {
    const response: AxiosResponse<ReviewListResponse> = await this.client.get(`/reviews/event/${eventId}`, { params })
    return response.data
  }

  async getEventReviewStats(eventId: number): Promise<ReviewStats> {
    const response: AxiosResponse<ReviewStats> = await this.client.get(`/reviews/event/${eventId}/stats`)
    return response.data
  }

  async createReview(review: ReviewCreate): Promise<Review> {
    const response: AxiosResponse<Review> = await this.client.post('/reviews', review)
    return response.data
  }

  async updateReview(reviewId: number, review: ReviewUpdate): Promise<Review> {
    const response: AxiosResponse<Review> = await this.client.put(`/reviews/${reviewId}`, review)
    return response.data
  }

  async deleteReview(reviewId: number): Promise<{ message: string }> {
    const response: AxiosResponse<{ message: string }> = await this.client.delete(`/reviews/${reviewId}`)
    return response.data
  }

  async reportReview(reviewId: number, report: ReviewReport): Promise<{ message: string }> {
    const response: AxiosResponse<{ message: string }> = await this.client.post(`/reviews/${reviewId}/report`, report)
    return response.data
  }

  async getMyReviews(params?: {
    skip?: number
    limit?: number
  }): Promise<ReviewListResponse> {
    const response: AxiosResponse<ReviewListResponse> = await this.client.get('/reviews/user/my-reviews', { params })
    return response.data
  }
}

export const apiService = new ApiService()