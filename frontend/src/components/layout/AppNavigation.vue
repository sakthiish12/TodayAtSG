<template>
  <nav class="bg-white shadow-sm border-b border-gray-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">
        <!-- Logo and brand -->
        <div class="flex items-center">
          <router-link
            to="/"
            class="flex items-center space-x-2"
          >
            <div class="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <span class="text-white font-bold text-sm">SG</span>
            </div>
            <span class="text-xl font-bold text-gray-900">TodayAtSG</span>
          </router-link>
        </div>
        
        <!-- Desktop navigation -->
        <div class="hidden md:flex items-center space-x-8">
          <!-- Main navigation links -->
          <div class="flex items-center space-x-1">
            <router-link
              to="/"
              class="px-3 py-2 rounded-md text-sm font-medium transition-colors"
              :class="[
                $route.name === 'home'
                  ? 'text-blue-600 bg-blue-50'
                  : 'text-gray-700 hover:text-gray-900'
              ]"
            >
              Home
            </router-link>
            
            <!-- Map/List toggle for event pages -->
            <div 
              v-if="isEventPage"
              class="flex items-center bg-gray-100 rounded-lg p-1 ml-4"
            >
              <router-link
                to="/map"
                class="px-3 py-2 text-sm font-medium rounded-md transition-colors flex items-center"
                :class="[
                  $route.name === 'map' 
                    ? 'bg-white text-gray-900 shadow-sm' 
                    : 'text-gray-600 hover:text-gray-900'
                ]"
              >
                <MapIcon class="w-4 h-4 mr-2" />
                Map
              </router-link>
              <router-link
                to="/events"
                class="px-3 py-2 text-sm font-medium rounded-md transition-colors flex items-center"
                :class="[
                  $route.name === 'events' 
                    ? 'bg-white text-gray-900 shadow-sm' 
                    : 'text-gray-600 hover:text-gray-900'
                ]"
              >
                <List class="w-4 h-4 mr-2" />
                Events
              </router-link>
            </div>
            
            <router-link
              to="/about"
              class="px-3 py-2 rounded-md text-sm font-medium transition-colors"
              :class="[
                $route.name === 'about'
                  ? 'text-blue-600 bg-blue-50'
                  : 'text-gray-700 hover:text-gray-900'
              ]"
            >
              About
            </router-link>
          </div>
          
          <!-- Auth section -->
          <div class="flex items-center space-x-3">
            <template v-if="isAuthenticated">
              <!-- User menu -->
              <div class="relative" ref="userMenuRef">
                <button
                  @click="showUserMenu = !showUserMenu"
                  class="flex items-center space-x-2 p-2 rounded-md text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 transition-colors"
                >
                  <div class="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-medium text-sm">
                    {{ getUserInitials(user?.email) }}
                  </div>
                  <ChevronDown class="w-4 h-4" />
                </button>
                
                <!-- User dropdown -->
                <div
                  v-if="showUserMenu"
                  class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-200"
                >
                  <div class="px-4 py-2 text-sm text-gray-700 border-b border-gray-100">
                    <div class="font-medium">{{ user?.full_name || user?.email }}</div>
                    <div class="text-xs text-gray-500">{{ user?.email }}</div>
                  </div>
                  
                  <router-link
                    to="/dashboard"
                    @click="showUserMenu = false"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <User class="w-4 h-4 mr-2 inline" />
                    Dashboard
                  </router-link>
                  
                  <router-link
                    to="/profile"
                    @click="showUserMenu = false"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <Settings class="w-4 h-4 mr-2 inline" />
                    Settings
                  </router-link>
                  
                  <router-link
                    v-if="user?.is_event_organizer"
                    to="/submit-event"
                    @click="showUserMenu = false"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <Plus class="w-4 h-4 mr-2 inline" />
                    Submit Event
                  </router-link>
                  
                  <div class="border-t border-gray-100 mt-1 pt-1">
                    <button
                      @click="handleLogout"
                      class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      <LogOut class="w-4 h-4 mr-2 inline" />
                      Sign out
                    </button>
                  </div>
                </div>
              </div>
            </template>
            
            <template v-else>
              <button
                @click="openAuthModal('login')"
                class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Sign in
              </button>
              <button
                @click="openAuthModal('register')"
                class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Sign up
              </button>
            </template>
          </div>
        </div>
        
        <!-- Mobile menu button -->
        <div class="md:hidden">
          <button
            @click="showMobileMenu = !showMobileMenu"
            class="p-2 rounded-md text-gray-700 hover:text-gray-900 hover:bg-gray-50 transition-colors"
          >
            <Menu v-if="!showMobileMenu" class="w-6 h-6" />
            <X v-else class="w-6 h-6" />
          </button>
        </div>
      </div>
    </div>
    
    <!-- Mobile menu -->
    <div
      v-if="showMobileMenu"
      class="md:hidden border-t border-gray-200 bg-white"
    >
      <div class="px-2 pt-2 pb-3 space-y-1">
        <router-link
          to="/"
          @click="showMobileMenu = false"
          class="block px-3 py-2 rounded-md text-base font-medium transition-colors"
          :class="[
            $route.name === 'home'
              ? 'text-blue-600 bg-blue-50'
              : 'text-gray-700 hover:text-gray-900 hover:bg-gray-50'
          ]"
        >
          Home
        </router-link>
        
        <!-- Map/List links for mobile -->
        <router-link
          to="/map"
          @click="showMobileMenu = false"
          class="flex items-center px-3 py-2 rounded-md text-base font-medium transition-colors"
          :class="[
            $route.name === 'map'
              ? 'text-blue-600 bg-blue-50'
              : 'text-gray-700 hover:text-gray-900 hover:bg-gray-50'
          ]"
        >
          <MapIcon class="w-5 h-5 mr-3" />
          Event Map
        </router-link>
        
        <router-link
          to="/events"
          @click="showMobileMenu = false"
          class="flex items-center px-3 py-2 rounded-md text-base font-medium transition-colors"
          :class="[
            $route.name === 'events'
              ? 'text-blue-600 bg-blue-50'
              : 'text-gray-700 hover:text-gray-900 hover:bg-gray-50'
          ]"
        >
          <List class="w-5 h-5 mr-3" />
          Event List
        </router-link>
        
        <router-link
          to="/about"
          @click="showMobileMenu = false"
          class="block px-3 py-2 rounded-md text-base font-medium transition-colors"
          :class="[
            $route.name === 'about'
              ? 'text-blue-600 bg-blue-50'
              : 'text-gray-700 hover:text-gray-900 hover:bg-gray-50'
          ]"
        >
          About
        </router-link>
      </div>
      
      <!-- Mobile auth section -->
      <div class="pt-4 pb-3 border-t border-gray-200">
        <template v-if="isAuthenticated">
          <div class="px-4 py-2 text-sm text-gray-700 border-b border-gray-100">
            <div class="font-medium">{{ user?.full_name || user?.email }}</div>
            <div class="text-xs text-gray-500">{{ user?.email }}</div>
          </div>
          
          <router-link
            to="/dashboard"
            @click="showMobileMenu = false"
            class="flex items-center px-4 py-2 text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50"
          >
            <User class="w-5 h-5 mr-3" />
            Dashboard
          </router-link>
          
          <router-link
            to="/profile"
            @click="showMobileMenu = false"
            class="flex items-center px-4 py-2 text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50"
          >
            <Settings class="w-5 h-5 mr-3" />
            Settings
          </router-link>
          
          <router-link
            v-if="user?.is_event_organizer"
            to="/submit-event"
            @click="showMobileMenu = false"
            class="flex items-center px-4 py-2 text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50"
          >
            <Plus class="w-5 h-5 mr-3" />
            Submit Event
          </router-link>
          
          <div class="border-t border-gray-100 mt-2 pt-2">
            <button
              @click="handleLogout"
              class="flex items-center w-full text-left px-4 py-2 text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50"
            >
              <LogOut class="w-5 h-5 mr-3" />
              Sign out
            </button>
          </div>
        </template>
        
        <template v-else>
          <div class="px-4 space-y-1">
            <button
              @click="openAuthModal('login')"
              class="block w-full text-left px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 transition-colors"
            >
              Sign in
            </button>
            <button
              @click="openAuthModal('register')"
              class="block w-full text-left px-3 py-2 rounded-md text-base font-medium bg-blue-600 text-white hover:bg-blue-700 transition-colors"
            >
              Sign up
            </button>
          </div>
        </template>
      </div>
    </div>
    
    <!-- Auth Modal -->
    <AuthModal
      :is-open="showAuthModal"
      :initial-mode="authModalMode"
      @close="closeAuthModal"
      @success="handleAuthSuccess"
    />
  </nav>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import {
  Menu,
  X,
  Map as MapIcon,
  List,
  ChevronDown,
  LogOut,
  User,
  Settings,
  Plus
} from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import AuthModal from '@/components/auth/AuthModal.vue'

// Router
const route = useRoute()
const router = useRouter()

// Store
const authStore = useAuthStore()
const { user, isAuthenticated } = storeToRefs(authStore)

// State
const showMobileMenu = ref(false)
const showUserMenu = ref(false)
const userMenuRef = ref<HTMLElement>()
const showAuthModal = ref(false)
const authModalMode = ref<'login' | 'register'>('login')

// Computed
const isEventPage = computed(() => {
  return ['map', 'events', 'event-detail'].includes(route.name as string)
})

// Methods
function getUserInitials(email?: string): string {
  if (!email) return '?'
  
  const parts = email.split('@')[0].split('.')
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return email.slice(0, 2).toUpperCase()
}

async function handleLogout() {
  try {
    await authStore.logout()
    showUserMenu.value = false
    showMobileMenu.value = false
    router.push('/')
  } catch (error) {
    console.error('Logout failed:', error)
  }
}

function openAuthModal(mode: 'login' | 'register') {
  authModalMode.value = mode
  showAuthModal.value = true
  showMobileMenu.value = false
}

function closeAuthModal() {
  showAuthModal.value = false
}

function handleAuthSuccess() {
  showAuthModal.value = false
  
  // Check for redirect after login
  const redirectPath = sessionStorage.getItem('redirectAfterLogin')
  if (redirectPath) {
    sessionStorage.removeItem('redirectAfterLogin')
    router.push(redirectPath)
  }
}

function handleClickOutside(event: MouseEvent) {
  if (userMenuRef.value && !userMenuRef.value.contains(event.target as Node)) {
    showUserMenu.value = false
  }
}

// Lifecycle
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>