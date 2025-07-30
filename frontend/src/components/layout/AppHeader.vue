<template>
  <header class="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">
        <!-- Logo and Navigation -->
        <div class="flex items-center space-x-8">
          <RouterLink to="/" class="flex items-center space-x-2">
            <div class="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <span class="text-white font-bold text-sm">T</span>
            </div>
            <span class="text-xl font-bold text-gray-900">TodayAtSG</span>
          </RouterLink>
          
          <nav class="hidden md:flex items-center space-x-6">
            <RouterLink 
              to="/events" 
              class="text-gray-700 hover:text-primary-600 font-medium transition-colors"
              active-class="text-primary-600"
            >
              Events
            </RouterLink>
            <RouterLink 
              to="/map" 
              class="text-gray-700 hover:text-primary-600 font-medium transition-colors"
              active-class="text-primary-600"
            >
              Map View
            </RouterLink>
            <RouterLink 
              to="/categories" 
              class="text-gray-700 hover:text-primary-600 font-medium transition-colors"
              active-class="text-primary-600"
            >
              Categories
            </RouterLink>
          </nav>
        </div>

        <!-- Search Bar -->
        <div class="hidden md:block flex-1 max-w-md mx-8">
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <SearchIcon class="h-5 w-5 text-gray-400" />
            </div>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search events..."
              class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-primary-500 focus:border-primary-500"
              @keyup.enter="handleSearch"
            />
          </div>
        </div>

        <!-- User Menu -->
        <div class="flex items-center space-x-4">
          <!-- Mobile menu button -->
          <button
            @click="mobileMenuOpen = !mobileMenuOpen"
            class="md:hidden inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500"
          >
            <MenuIcon v-if="!mobileMenuOpen" class="h-6 w-6" />
            <XIcon v-else class="h-6 w-6" />
          </button>

          <!-- User Authentication -->
          <div v-if="isAuthenticated" class="relative">
            <button
              @click="userMenuOpen = !userMenuOpen"
              class="flex items-center space-x-2 text-gray-700 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 rounded-lg p-2"
            >
              <UserIcon class="h-5 w-5" />
              <span class="hidden md:block font-medium">{{ user?.email }}</span>
              <ChevronDownIcon class="h-4 w-4" />
            </button>

            <!-- User Dropdown -->
            <div
              v-if="userMenuOpen"
              v-click-outside="() => userMenuOpen = false"
              class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 ring-1 ring-black ring-opacity-5 z-50"
            >
              <RouterLink
                to="/profile"
                class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                @click="userMenuOpen = false"
              >
                Profile
              </RouterLink>
              <RouterLink
                v-if="isEventOrganizer"
                to="/dashboard"
                class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                @click="userMenuOpen = false"
              >
                Dashboard
              </RouterLink>
              <button
                @click="handleLogout"
                class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              >
                Sign out
              </button>
            </div>
          </div>

          <div v-else class="flex items-center space-x-3">
            <RouterLink
              to="/login"
              class="text-gray-700 hover:text-gray-900 font-medium"
            >
              Sign in
            </RouterLink>
            <RouterLink
              to="/register"
              class="btn-primary"
            >
              Sign up
            </RouterLink>
          </div>
        </div>
      </div>

      <!-- Mobile Navigation -->
      <div v-if="mobileMenuOpen" class="md:hidden py-4 border-t border-gray-200">
        <nav class="space-y-2">
          <RouterLink
            to="/events"
            class="block px-3 py-2 text-gray-700 hover:text-primary-600 font-medium"
            @click="mobileMenuOpen = false"
          >
            Events
          </RouterLink>
          <RouterLink
            to="/map"
            class="block px-3 py-2 text-gray-700 hover:text-primary-600 font-medium"
            @click="mobileMenuOpen = false"
          >
            Map View
          </RouterLink>
          <RouterLink
            to="/categories"
            class="block px-3 py-2 text-gray-700 hover:text-primary-600 font-medium"
            @click="mobileMenuOpen = false"
          >
            Categories
          </RouterLink>
        </nav>

        <!-- Mobile Search -->
        <div class="mt-4 px-3">
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <SearchIcon class="h-5 w-5 text-gray-400" />
            </div>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search events..."
              class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-primary-500 focus:border-primary-500"
              @keyup.enter="handleSearch"
            />
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useEventsStore } from '@/stores/events'
import { 
  SearchIcon, 
  MenuIcon, 
  XIcon, 
  UserIcon, 
  ChevronDownIcon 
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()
const eventsStore = useEventsStore()

// Reactive state
const searchQuery = ref('')
const mobileMenuOpen = ref(false)
const userMenuOpen = ref(false)

// Computed properties
const isAuthenticated = computed(() => authStore.isAuthenticated)
const isEventOrganizer = computed(() => authStore.isEventOrganizer)
const user = computed(() => authStore.user)

// Methods
function handleSearch() {
  if (searchQuery.value.trim()) {
    eventsStore.updateFilters({ search: searchQuery.value.trim() })
    router.push('/events')
    searchQuery.value = ''
  }
}

async function handleLogout() {
  try {
    await authStore.logout()
    userMenuOpen.value = false
    router.push('/')
  } catch (error) {
    console.error('Logout error:', error)
  }
}

// Directive for clicking outside
const vClickOutside = {
  beforeMount(el: HTMLElement, binding: any) {
    el.clickOutsideEvent = (event: Event) => {
      if (!(el === event.target || el.contains(event.target as Node))) {
        binding.value(event)
      }
    }
    document.addEventListener('click', el.clickOutsideEvent)
  },
  unmounted(el: HTMLElement) {
    document.removeEventListener('click', el.clickOutsideEvent)
  }
}
</script>