<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Reset your password
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Enter your new password below
        </p>
      </div>

      <!-- Success State -->
      <div v-if="isSuccess" class="text-center">
        <div class="mb-4">
          <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
            <Check class="h-6 w-6 text-green-600" />
          </div>
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">Password Reset Successful</h3>
        <p class="text-sm text-gray-600 mb-6">
          Your password has been successfully reset. You can now sign in with your new password.
        </p>
        <router-link
          to="/"
          class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Go to Home
        </router-link>
      </div>

      <!-- Form -->
      <form v-else @submit.prevent="handleSubmit" class="mt-8 space-y-6">
        <!-- Error Display -->
        <div v-if="error" class="p-3 bg-red-50 border border-red-200 rounded-md">
          <p class="text-sm text-red-600">{{ error }}</p>
        </div>

        <div class="space-y-4">
          <div>
            <label for="new-password" class="block text-sm font-medium text-gray-700 mb-1">
              New Password
            </label>
            <div class="relative">
              <input
                id="new-password"
                v-model="form.new_password"
                :type="showNewPassword ? 'text' : 'password'"
                required
                class="appearance-none relative block w-full px-3 py-2 pr-10 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                placeholder="Enter your new password"
              />
              <button
                type="button"
                @click="showNewPassword = !showNewPassword"
                class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                <Eye v-if="!showNewPassword" class="w-4 h-4" />
                <EyeOff v-else class="w-4 h-4" />
              </button>
            </div>
          </div>

          <div>
            <label for="confirm-password" class="block text-sm font-medium text-gray-700 mb-1">
              Confirm New Password
            </label>
            <div class="relative">
              <input
                id="confirm-password"
                v-model="form.confirm_password"
                :type="showConfirmPassword ? 'text' : 'password'"
                required
                class="appearance-none relative block w-full px-3 py-2 pr-10 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                placeholder="Confirm your new password"
              />
              <button
                type="button"
                @click="showConfirmPassword = !showConfirmPassword"
                class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                <Eye v-if="!showConfirmPassword" class="w-4 h-4" />
                <EyeOff v-else class="w-4 h-4" />
              </button>
            </div>
          </div>

          <!-- Password Requirements -->
          <div class="text-xs text-gray-500">
            <p class="mb-1">Password must contain:</p>
            <ul class="list-disc list-inside space-y-1">
              <li>At least 8 characters</li>
              <li>At least one uppercase letter</li>
              <li>At least one lowercase letter</li>
              <li>At least one number</li>
            </ul>
          </div>
        </div>

        <div>
          <button
            type="submit"
            :disabled="loading || form.new_password !== form.confirm_password || !form.new_password"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="loading" class="flex items-center">
              <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Resetting password...
            </span>
            <span v-else>Reset Password</span>
          </button>
        </div>

        <div class="text-center">
          <router-link
            to="/"
            class="font-medium text-blue-600 hover:text-blue-500"
          >
            Back to Home
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Check, Eye, EyeOff } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import type { PasswordReset } from '@/types'

const route = useRoute()
const authStore = useAuthStore()

// State
const form = ref<PasswordReset>({
  token: '',
  new_password: '',
  confirm_password: ''
})

const loading = ref(false)
const error = ref<string | null>(null)
const isSuccess = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

// Methods
async function handleSubmit() {
  if (form.value.new_password !== form.value.confirm_password) {
    error.value = 'Passwords do not match'
    return
  }

  try {
    loading.value = true
    error.value = null
    
    await authStore.resetPassword(form.value)
    
    isSuccess.value = true
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to reset password'
  } finally {
    loading.value = false
  }
}

// Initialize token from URL
onMounted(() => {
  const token = route.query.token as string
  if (token) {
    form.value.token = token
  } else {
    error.value = 'Invalid or missing reset token'
  }
})
</script>