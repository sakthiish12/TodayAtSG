<template>
  <div class="max-w-3xl mx-auto p-6">
    <div class="bg-white rounded-lg shadow">
      <!-- Header -->
      <div class="px-6 py-4 border-b border-gray-200">
        <h1 class="text-2xl font-semibold text-gray-900">Profile Settings</h1>
        <p class="text-sm text-gray-600 mt-1">Manage your account settings and preferences</p>
      </div>

      <!-- Success Message -->
      <div v-if="successMessage" class="mx-6 mt-6 p-4 bg-green-50 border border-green-200 rounded-md">
        <div class="flex">
          <Check class="h-5 w-5 text-green-400" />
          <div class="ml-3">
            <p class="text-sm text-green-700">{{ successMessage }}</p>
          </div>
        </div>
      </div>

      <div class="p-6">
        <!-- Profile Information -->
        <div class="mb-8">
          <h2 class="text-lg font-medium text-gray-900 mb-4">Personal Information</h2>
          
          <!-- Error Display -->
          <div v-if="profileError" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
            <p class="text-sm text-red-600">{{ profileError }}</p>
          </div>

          <form @submit.prevent="updateProfile">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label for="first_name" class="block text-sm font-medium text-gray-700 mb-1">
                  First Name
                </label>
                <input
                  id="first_name"
                  v-model="profileForm.first_name"
                  type="text"
                  class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="First name"
                />
              </div>
              
              <div>
                <label for="last_name" class="block text-sm font-medium text-gray-700 mb-1">
                  Last Name
                </label>
                <input
                  id="last_name"
                  v-model="profileForm.last_name"
                  type="text"
                  class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Last name"
                />
              </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label for="email" class="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  id="email"
                  :value="authStore.user?.email"
                  type="email"
                  disabled
                  class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm bg-gray-50 text-gray-500"
                />
                <p class="text-xs text-gray-500 mt-1">Email cannot be changed</p>
              </div>
              
              <div>
                <label for="phone_number" class="block text-sm font-medium text-gray-700 mb-1">
                  Phone Number
                </label>
                <input
                  id="phone_number"
                  v-model="profileForm.phone_number"
                  type="tel"
                  class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Phone number"
                />
              </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label for="search_radius" class="block text-sm font-medium text-gray-700 mb-1">
                  Preferred Search Radius (km)
                </label>
                <input
                  id="search_radius"
                  v-model.number="profileForm.preferred_search_radius"
                  type="number"
                  min="1"
                  max="100"
                  class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div class="flex items-end">
                <div class="w-full">
                  <div class="flex items-center h-10">
                    <input
                      id="is_event_organizer"
                      :checked="authStore.user?.is_event_organizer"
                      type="checkbox"
                      disabled
                      class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label for="is_event_organizer" class="ml-2 text-sm text-gray-600">
                      Event Organizer
                    </label>
                  </div>
                  <p class="text-xs text-gray-500">Contact support to change organizer status</p>
                </div>
              </div>
            </div>
            
            <div class="flex justify-end">
              <button
                type="submit"
                :disabled="profileLoading"
                class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span v-if="profileLoading" class="flex items-center">
                  <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Updating...
                </span>
                <span v-else>Update Profile</span>
              </button>
            </div>
          </form>
        </div>

        <!-- Divider -->
        <div class="border-t border-gray-200 mb-8"></div>

        <!-- Password Change -->
        <div class="mb-8">
          <h2 class="text-lg font-medium text-gray-900 mb-4">Change Password</h2>
          
          <!-- Error Display -->
          <div v-if="passwordError" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
            <p class="text-sm text-red-600">{{ passwordError }}</p>
          </div>

          <form @submit.prevent="changePassword">
            <div class="space-y-4">
              <div>
                <label for="current_password" class="block text-sm font-medium text-gray-700 mb-1">
                  Current Password
                </label>
                <div class="relative">
                  <input
                    id="current_password"
                    v-model="passwordForm.current_password"
                    :type="showCurrentPassword ? 'text' : 'password'"
                    required
                    class="w-full border border-gray-300 rounded-md px-3 py-2 pr-10 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter current password"
                  />
                  <button
                    type="button"
                    @click="showCurrentPassword = !showCurrentPassword"
                    class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    <Eye v-if="!showCurrentPassword" class="w-4 h-4" />
                    <EyeOff v-else class="w-4 h-4" />
                  </button>
                </div>
              </div>
              
              <div>
                <label for="new_password" class="block text-sm font-medium text-gray-700 mb-1">
                  New Password
                </label>
                <div class="relative">
                  <input
                    id="new_password"
                    v-model="passwordForm.new_password"
                    :type="showNewPassword ? 'text' : 'password'"
                    required
                    class="w-full border border-gray-300 rounded-md px-3 py-2 pr-10 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter new password"
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
                <label for="confirm_password" class="block text-sm font-medium text-gray-700 mb-1">
                  Confirm New Password
                </label>
                <div class="relative">
                  <input
                    id="confirm_password"
                    v-model="passwordForm.confirm_password"
                    :type="showConfirmPassword ? 'text' : 'password'"
                    required
                    class="w-full border border-gray-300 rounded-md px-3 py-2 pr-10 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Confirm new password"
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
            </div>
            
            <div class="flex justify-end mt-6">
              <button
                type="submit"
                :disabled="passwordLoading || passwordForm.new_password !== passwordForm.confirm_password"
                class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span v-if="passwordLoading" class="flex items-center">
                  <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Changing...
                </span>
                <span v-else>Change Password</span>
              </button>
            </div>
          </form>
        </div>

        <!-- Divider -->
        <div class="border-t border-gray-200 mb-8"></div>

        <!-- Account Information -->
        <div>
          <h2 class="text-lg font-medium text-gray-900 mb-4">Account Information</h2>
          <div class="bg-gray-50 rounded-lg p-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <span class="font-medium text-gray-700">Account Status:</span>
                <span class="ml-2" :class="authStore.user?.is_active ? 'text-green-600' : 'text-red-600'">
                  {{ authStore.user?.is_active ? 'Active' : 'Inactive' }}
                </span>
              </div>
              <div>
                <span class="font-medium text-gray-700">Email Verified:</span>
                <span class="ml-2" :class="authStore.user?.is_verified ? 'text-green-600' : 'text-orange-600'">
                  {{ authStore.user?.is_verified ? 'Yes' : 'Pending' }}
                </span>
              </div>
              <div>
                <span class="font-medium text-gray-700">Member Since:</span>
                <span class="ml-2 text-gray-600">
                  {{ formatDate(authStore.user?.created_at) }}
                </span>
              </div>
              <div>
                <span class="font-medium text-gray-700">Last Login:</span>
                <span class="ml-2 text-gray-600">
                  {{ authStore.user?.last_login ? formatDate(authStore.user.last_login) : 'Never' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Check, Eye, EyeOff } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import type { UserUpdate, PasswordChange } from '@/types'

const authStore = useAuthStore()

// State
const profileForm = ref<UserUpdate>({
  first_name: '',
  last_name: '',
  phone_number: '',
  preferred_search_radius: 10
})

const passwordForm = ref<PasswordChange>({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

const profileLoading = ref(false)
const passwordLoading = ref(false)
const profileError = ref<string | null>(null)
const passwordError = ref<string | null>(null)
const successMessage = ref<string | null>(null)

const showCurrentPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

// Methods
async function updateProfile() {
  try {
    profileLoading.value = true
    profileError.value = null
    successMessage.value = null
    
    await authStore.updateProfile(profileForm.value)
    
    successMessage.value = 'Profile updated successfully'
    setTimeout(() => {
      successMessage.value = null
    }, 5000)
  } catch (err: any) {
    profileError.value = err.response?.data?.detail || 'Failed to update profile'
  } finally {
    profileLoading.value = false
  }
}

async function changePassword() {
  try {
    passwordLoading.value = true
    passwordError.value = null
    successMessage.value = null
    
    await authStore.changePassword(passwordForm.value)
    
    // Reset form
    passwordForm.value = {
      current_password: '',
      new_password: '',
      confirm_password: ''
    }
    
    successMessage.value = 'Password changed successfully'
    setTimeout(() => {
      successMessage.value = null
    }, 5000)
  } catch (err: any) {
    passwordError.value = err.response?.data?.detail || 'Failed to change password'
  } finally {
    passwordLoading.value = false
  }
}

function formatDate(dateString: string | undefined): string {
  if (!dateString) return 'Unknown'
  return new Date(dateString).toLocaleDateString('en-SG', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// Initialize form with user data
onMounted(() => {
  if (authStore.user) {
    profileForm.value = {
      first_name: authStore.user.first_name || '',
      last_name: authStore.user.last_name || '',
      phone_number: authStore.user.phone_number || '',
      preferred_search_radius: authStore.user.preferred_search_radius || 10
    }
  }
})
</script>