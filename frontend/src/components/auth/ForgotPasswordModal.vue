<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-60">
    <div class="bg-white rounded-lg p-6 w-full max-w-md mx-4">
      <!-- Header -->
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-xl font-semibold text-gray-900">
          Reset Password
        </h2>
        <button
          @click="$emit('close')"
          class="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <X class="w-6 h-6" />
        </button>
      </div>

      <!-- Success Message -->
      <div v-if="isSubmitted" class="text-center">
        <div class="mb-4">
          <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
            <Check class="h-6 w-6 text-green-600" />
          </div>
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">Check your email</h3>
        <p class="text-sm text-gray-600 mb-6">
          If an account with that email exists, we've sent you a password reset link.
        </p>
        <button
          @click="$emit('close')"
          class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
        >
          Close
        </button>
      </div>

      <!-- Form -->
      <form v-else @submit.prevent="handleSubmit">
        <div class="mb-4">
          <p class="text-sm text-gray-600 mb-4">
            Enter your email address and we'll send you a link to reset your password.
          </p>
        </div>

        <!-- Error Display -->
        <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <p class="text-sm text-red-600">{{ error }}</p>
        </div>

        <div class="mb-6">
          <label for="reset-email" class="block text-sm font-medium text-gray-700 mb-1">
            Email address
          </label>
          <input
            id="reset-email"
            v-model="email"
            type="email"
            required
            class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Enter your email address"
          />
        </div>

        <div class="flex gap-3">
          <button
            type="button"
            @click="$emit('close')"
            class="flex-1 bg-white text-gray-700 border border-gray-300 py-2 px-4 rounded-md hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="loading || !email"
            class="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="loading" class="flex items-center justify-center">
              <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Sending...
            </span>
            <span v-else>Send Reset Link</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { X, Check } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'

const emit = defineEmits<{
  close: []
}>()

const authStore = useAuthStore()

// State
const email = ref('')
const loading = ref(false)
const error = ref<string | null>(null)
const isSubmitted = ref(false)

// Methods
async function handleSubmit() {
  if (!email.value) return
  
  try {
    loading.value = true
    error.value = null
    
    await authStore.requestPasswordReset({ email: email.value })
    
    isSubmitted.value = true
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to send reset email'
  } finally {
    loading.value = false
  }
}
</script>