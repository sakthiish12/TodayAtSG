<template>
  <div 
    v-if="isOpen" 
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    @click="closeModal"
  >
    <div 
      class="bg-white rounded-lg p-6 w-full max-w-md mx-4"
      @click.stop
    >
      <!-- Modal Header -->
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-xl font-semibold text-gray-900">
          {{ mode === 'login' ? 'Sign In' : 'Create Account' }}
        </h2>
        <button
          @click="closeModal"
          class="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <X class="w-6 h-6" />
        </button>
      </div>

      <!-- Toggle Tabs -->
      <div class="flex mb-6 bg-gray-100 rounded-lg p-1">
        <button
          @click="mode = 'login'"
          :class="[
            'flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors',
            mode === 'login' 
              ? 'bg-white text-gray-900 shadow-sm' 
              : 'text-gray-500 hover:text-gray-700'
          ]"
        >
          Sign In
        </button>
        <button
          @click="mode = 'register'"
          :class="[
            'flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors',
            mode === 'register' 
              ? 'bg-white text-gray-900 shadow-sm' 
              : 'text-gray-500 hover:text-gray-700'
          ]"
        >
          Sign Up
        </button>
      </div>

      <!-- Error Display -->
      <div v-if="authStore.error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
        <p class="text-sm text-red-600">{{ authStore.error }}</p>
      </div>

      <!-- Login Form -->
      <form v-if="mode === 'login'" @submit.prevent="handleLogin">
        <div class="space-y-4">
          <div>
            <label for="login-email" class="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              id="login-email"
              v-model="loginForm.email"
              type="email"
              required
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter your email"
            />
          </div>
          
          <div>
            <label for="login-password" class="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <div class="relative">
              <input
                id="login-password"
                v-model="loginForm.password"
                :type="showLoginPassword ? 'text' : 'password'"
                required
                class="w-full border border-gray-300 rounded-md px-3 py-2 pr-10 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter your password"
              />
              <button
                type="button"
                @click="showLoginPassword = !showLoginPassword"
                class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                <Eye v-if="!showLoginPassword" class="w-4 h-4" />
                <EyeOff v-else class="w-4 h-4" />
              </button>
            </div>
          </div>
          
          <div class="flex items-center justify-between">
            <label class="flex items-center">
              <input
                v-model="loginForm.rememberMe"
                type="checkbox"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <span class="ml-2 text-sm text-gray-600">Remember me</span>
            </label>
            
            <button
              type="button"
              @click="showForgotPassword = true"
              class="text-sm text-blue-600 hover:text-blue-500"
            >
              Forgot password?
            </button>
          </div>
          
          <button
            type="submit"
            :disabled="authStore.loading"
            class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="authStore.loading" class="flex items-center justify-center">
              <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Signing in...
            </span>
            <span v-else>Sign In</span>
          </button>
        </div>
      </form>

      <!-- Register Form -->
      <form v-else @submit.prevent="handleRegister">
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label for="register-first-name" class="block text-sm font-medium text-gray-700 mb-1">
                First Name
              </label>
              <input
                id="register-first-name"
                v-model="registerForm.first_name"
                type="text"
                class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="First name"
              />
            </div>
            
            <div>
              <label for="register-last-name" class="block text-sm font-medium text-gray-700 mb-1">
                Last Name
              </label>
              <input
                id="register-last-name"
                v-model="registerForm.last_name"
                type="text"
                class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Last name"
              />
            </div>
          </div>
          
          <div>
            <label for="register-email" class="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              id="register-email"
              v-model="registerForm.email"
              type="email"
              required
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter your email"
            />
          </div>
          
          <div>
            <label for="register-phone" class="block text-sm font-medium text-gray-700 mb-1">
              Phone Number
            </label>
            <input
              id="register-phone"
              v-model="registerForm.phone_number"
              type="tel"
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Phone number (optional)"
            />
          </div>
          
          <div>
            <label for="register-password" class="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <div class="relative">
              <input
                id="register-password"
                v-model="registerForm.password"
                :type="showRegisterPassword ? 'text' : 'password'"
                required
                class="w-full border border-gray-300 rounded-md px-3 py-2 pr-10 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Create a password"
              />
              <button
                type="button"
                @click="showRegisterPassword = !showRegisterPassword"
                class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                <Eye v-if="!showRegisterPassword" class="w-4 h-4" />
                <EyeOff v-else class="w-4 h-4" />
              </button>
            </div>
          </div>
          
          <div>
            <label for="register-confirm-password" class="block text-sm font-medium text-gray-700 mb-1">
              Confirm Password
            </label>
            <div class="relative">
              <input
                id="register-confirm-password"
                v-model="registerForm.confirm_password"
                :type="showConfirmPassword ? 'text' : 'password'"
                required
                class="w-full border border-gray-300 rounded-md px-3 py-2 pr-10 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Confirm your password"
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
          
          <div>
            <label class="flex items-center">
              <input
                v-model="registerForm.is_event_organizer"
                type="checkbox"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <span class="ml-2 text-sm text-gray-600">
                I want to organize and submit events
              </span>
            </label>
          </div>
          
          <div>
            <label class="flex items-start">
              <input
                v-model="registerForm.agreeToTerms"
                type="checkbox"
                required
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded mt-0.5"
              />
              <span class="ml-2 text-sm text-gray-600">
                I agree to the 
                <a href="/terms" class="text-blue-600 hover:text-blue-500">Terms of Service</a>
                and 
                <a href="/privacy" class="text-blue-600 hover:text-blue-500">Privacy Policy</a>
              </span>
            </label>
          </div>
          
          <button
            type="submit"
            :disabled="authStore.loading"
            class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="authStore.loading" class="flex items-center justify-center">
              <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Creating account...
            </span>
            <span v-else>Create Account</span>
          </button>
        </div>
      </form>

      <!-- Forgot Password Modal -->
      <ForgotPasswordModal 
        v-if="showForgotPassword"
        @close="showForgotPassword = false"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { X, Eye, EyeOff } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import ForgotPasswordModal from './ForgotPasswordModal.vue'
import type { LoginCredentials, RegisterCredentials } from '@/types'

interface Props {
  isOpen: boolean
  initialMode?: 'login' | 'register'
}

const props = withDefaults(defineProps<Props>(), {
  initialMode: 'login'
})

const emit = defineEmits<{
  close: []
  success: []
}>()

const authStore = useAuthStore()

// State
const mode = ref<'login' | 'register'>(props.initialMode)
const showLoginPassword = ref(false)
const showRegisterPassword = ref(false)
const showConfirmPassword = ref(false)
const showForgotPassword = ref(false)

// Form data
const loginForm = ref<LoginCredentials & { rememberMe?: boolean }>({
  username: '',
  password: '',
  rememberMe: false
})

const registerForm = ref<RegisterCredentials & { agreeToTerms?: boolean }>({
  email: '',
  password: '',
  confirm_password: '',
  first_name: '',
  last_name: '',
  phone_number: '',
  is_event_organizer: false,
  agreeToTerms: false
})

// Methods
function closeModal() {
  emit('close')
}

async function handleLogin() {
  try {
    await authStore.login({
      username: loginForm.value.username,
      password: loginForm.value.password
    })
    
    emit('success')
    closeModal()
  } catch (error) {
    // Error handled by store
  }
}

async function handleRegister() {
  try {
    await authStore.register(registerForm.value)
    
    emit('success')
    closeModal()
  } catch (error) {
    // Error handled by store
  }
}

// Watchers
watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    mode.value = props.initialMode
    // Reset forms
    loginForm.value = { username: '', password: '', rememberMe: false }
    registerForm.value = {
      email: '',
      password: '',
      confirm_password: '',
      first_name: '',
      last_name: '',
      phone_number: '',
      is_event_organizer: false,
      agreeToTerms: false
    }
  }
})

// Reset error when mode changes
watch(mode, () => {
  authStore.error = null
})
</script>