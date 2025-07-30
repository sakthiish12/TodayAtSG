import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiService } from '@/services/api'
import type { User, LoginCredentials, RegisterCredentials, UserUpdate, PasswordChange, PasswordResetRequest, PasswordReset } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
  const isEventOrganizer = computed(() => user.value?.is_event_organizer || false)

  // Actions
  async function login(credentials: LoginCredentials) {
    try {
      loading.value = true
      error.value = null
      
      const response = await apiService.login(credentials)
      
      accessToken.value = response.access_token
      user.value = response.user
      
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('refresh_token', response.refresh_token)
      localStorage.setItem('user', JSON.stringify(response.user))
      
      return response
    } catch (err: any) {
      const message = err.response?.data?.detail || err.response?.data?.message || 'Login failed'
      error.value = Array.isArray(message) ? message[0]?.msg || 'Login failed' : message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function register(credentials: RegisterCredentials) {
    try {
      loading.value = true
      error.value = null
      
      // First register the user
      const newUser = await apiService.register(credentials)
      
      // Then login to get tokens
      const loginResponse = await apiService.login({
        username: credentials.email,
        password: credentials.password
      })
      
      accessToken.value = loginResponse.access_token
      user.value = loginResponse.user
      
      localStorage.setItem('access_token', loginResponse.access_token)
      localStorage.setItem('refresh_token', loginResponse.refresh_token)
      localStorage.setItem('user', JSON.stringify(loginResponse.user))
      
      return loginResponse
    } catch (err: any) {
      const message = err.response?.data?.detail || err.response?.data?.message || 'Registration failed'
      error.value = Array.isArray(message) ? message[0]?.msg || 'Registration failed' : message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    try {
      if (accessToken.value) {
        await apiService.logout()
      }
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      // Clear local state regardless of API call success
      accessToken.value = null
      user.value = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
    }
  }

  async function getCurrentUser() {
    try {
      if (!accessToken.value) return null
      
      const currentUser = await apiService.getCurrentUser()
      user.value = currentUser
      localStorage.setItem('user', JSON.stringify(currentUser))
      
      return currentUser
    } catch (err) {
      console.error('Get current user error:', err)
      // If token is invalid, clear auth state
      logout()
      return null
    }
  }

  async function updateProfile(userData: UserUpdate) {
    try {
      loading.value = true
      error.value = null
      
      const updatedUser = await apiService.updateProfile(userData)
      user.value = updatedUser
      
      localStorage.setItem('user', JSON.stringify(updatedUser))
      
      return updatedUser
    } catch (err: any) {
      const message = err.response?.data?.detail || err.response?.data?.message || 'Update failed'
      error.value = Array.isArray(message) ? message[0]?.msg || 'Update failed' : message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function changePassword(passwordData: PasswordChange) {
    try {
      loading.value = true
      error.value = null
      
      const response = await apiService.changePassword(passwordData)
      return response
    } catch (err: any) {
      const message = err.response?.data?.detail || err.response?.data?.message || 'Password change failed'
      error.value = Array.isArray(message) ? message[0]?.msg || 'Password change failed' : message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function requestPasswordReset(data: PasswordResetRequest) {
    try {
      loading.value = true
      error.value = null
      
      const response = await apiService.requestPasswordReset(data)
      return response
    } catch (err: any) {
      const message = err.response?.data?.detail || err.response?.data?.message || 'Password reset request failed'
      error.value = Array.isArray(message) ? message[0]?.msg || 'Password reset request failed' : message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function resetPassword(data: PasswordReset) {
    try {
      loading.value = true
      error.value = null
      
      const response = await apiService.resetPassword(data)
      return response
    } catch (err: any) {
      const message = err.response?.data?.detail || err.response?.data?.message || 'Password reset failed'
      error.value = Array.isArray(message) ? message[0]?.msg || 'Password reset failed' : message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function refreshToken() {
    try {
      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) {
        await logout()
        return null
      }
      
      const response = await apiService.refreshToken(refreshToken)
      
      accessToken.value = response.access_token
      user.value = response.user
      
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('refresh_token', response.refresh_token)
      localStorage.setItem('user', JSON.stringify(response.user))
      
      return response
    } catch (err) {
      console.error('Token refresh error:', err)
      await logout()
      return null
    }
  }

  function initializeAuth() {
    const storedUser = localStorage.getItem('user')
    const storedToken = localStorage.getItem('access_token')
    
    if (storedUser && storedToken) {
      try {
        user.value = JSON.parse(storedUser)
        accessToken.value = storedToken
      } catch (err) {
        console.error('Error parsing stored user:', err)
        logout()
      }
    }
  }

  return {
    // State
    user,
    accessToken,
    loading,
    error,
    
    // Getters
    isAuthenticated,
    isEventOrganizer,
    
    // Actions
    login,
    register,
    logout,
    getCurrentUser,
    updateProfile,
    changePassword,
    requestPasswordReset,
    resetPassword,
    refreshToken,
    initializeAuth
  }
})