// Event types
export interface Event {
  id: number
  title: string
  description: string
  date: string
  time: string
  location: string
  latitude: number
  longitude: number
  age_restrictions?: string
  external_url?: string
  category_id: number
  category?: Category
  tags?: Tag[]
  is_approved: boolean
  source: 'user_submission' | 'scraped' | 'admin'
  average_rating?: number
  review_count?: number
  created_at: string
  updated_at: string
}

// Category types
export interface Category {
  id: number
  name: string
  description?: string
}

// Tag types
export interface Tag {
  id: number
  name: string
}

// User types
export interface User {
  id: number
  email: string
  first_name?: string
  last_name?: string
  phone_number?: string
  full_name: string
  is_event_organizer: boolean
  is_admin: boolean
  is_active: boolean
  is_verified: boolean
  preferred_search_radius: number
  last_login?: string
  created_at: string
}

// Review types
export interface Review {
  id: number
  user_id: number
  event_id: number
  rating: number
  comment?: string
  user_name: string
  is_verified: boolean
  is_reported: boolean
  created_at: string
  updated_at: string
  user?: User
}

export interface ReviewListResponse {
  reviews: Review[]
  total: number
  skip: number
  limit: number
  average_rating?: number
}

export interface ReviewStats {
  total_reviews: number
  average_rating?: number
  rating_distribution: Record<number, number>
  recent_reviews: Review[]
}

// API Response types
export interface ApiResponse<T> {
  data: T
  message?: string
  success: boolean
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  per_page: number
  pages: number
}

// Filter types
export interface EventFilters {
  category_ids?: number[]
  tag_ids?: number[]
  date_from?: string
  date_to?: string
  location?: string
  latitude?: number
  longitude?: number
  radius?: number
  search?: string
  age_restriction?: string
}

// Map types
export interface MapBounds {
  north: number
  south: number
  east: number
  west: number
}

export interface MapCenter {
  lat: number
  lng: number
}

// Authentication types
export interface LoginCredentials {
  username: string // Backend expects username field for OAuth2PasswordRequestForm
  password: string
}

export interface RegisterCredentials {
  email: string
  password: string
  confirm_password: string
  first_name?: string
  last_name?: string
  phone_number?: string
  is_event_organizer?: boolean
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: User
}

export interface UserUpdate {
  first_name?: string
  last_name?: string
  phone_number?: string
  preferred_location_lat?: string
  preferred_location_lng?: string
  preferred_search_radius?: number
}

export interface PasswordChange {
  current_password: string
  new_password: string
  confirm_password: string
}

export interface PasswordResetRequest {
  email: string
}

export interface PasswordReset {
  token: string
  new_password: string
  confirm_password: string
}

export interface ReviewCreate {
  event_id: number
  rating: number
  comment?: string
}

export interface ReviewUpdate {
  rating?: number
  comment?: string
}

export interface ReviewReport {
  reason: string
  description?: string
}