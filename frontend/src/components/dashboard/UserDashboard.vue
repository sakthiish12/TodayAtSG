<template>
  <div class="max-w-7xl mx-auto p-6">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900">Dashboard</h1>
      <p class="text-gray-600 mt-2">Welcome back, {{ authStore.user?.full_name || authStore.user?.email }}!</p>
    </div>

    <!-- Quick Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-3 rounded-full bg-blue-100">
            <MessageSquare class="w-6 h-6 text-blue-600" />
          </div>
          <div class="ml-4">
            <h3 class="text-lg font-semibold text-gray-900">{{ userStats.total_reviews }}</h3>
            <p class="text-gray-600">Reviews Written</p>
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-3 rounded-full bg-green-100">
            <Calendar class="w-6 h-6 text-green-600" />
          </div>
          <div class="ml-4">
            <h3 class="text-lg font-semibold text-gray-900">{{ userStats.submitted_events }}</h3>
            <p class="text-gray-600">Events Submitted</p>
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-3 rounded-full bg-yellow-100">
            <Star class="w-6 h-6 text-yellow-600" />
          </div>
          <div class="ml-4">
            <h3 class="text-lg font-semibold text-gray-900">
              {{ userStats.average_rating ? userStats.average_rating.toFixed(1) : 'N/A' }}
            </h3>
            <p class="text-gray-600">Average Rating</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab Navigation -->
    <div class="bg-white rounded-lg shadow mb-6">
      <div class="border-b border-gray-200">
        <nav class="-mb-px flex space-x-8 px-6" aria-label="Tabs">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            <component :is="tab.icon" class="w-5 h-5 mr-2 inline" />
            {{ tab.name }}
          </button>
        </nav>
      </div>
      
      <!-- Tab Content -->
      <div class="p-6">
        <!-- My Reviews Tab -->
        <div v-if="activeTab === 'reviews'">
          <MyReviewsList />
        </div>
        
        <!-- Submitted Events Tab -->
        <div v-else-if="activeTab === 'events'">
          <SubmittedEventsList />
        </div>
        
        <!-- Favorites Tab -->
        <div v-else-if="activeTab === 'favorites'">
          <FavoritesList />
        </div>
        
        <!-- Activity Tab -->
        <div v-else-if="activeTab === 'activity'">
          <ActivityFeed />
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <router-link
          to="/events"
          class="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <Search class="w-6 h-6 text-gray-400 mr-3" />
          <div>
            <h3 class="font-medium text-gray-900">Browse Events</h3>
            <p class="text-sm text-gray-600">Discover new events in Singapore</p>
          </div>
        </router-link>
        
        <router-link
          v-if="authStore.isEventOrganizer"
          to="/submit-event"
          class="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <Plus class="w-6 h-6 text-gray-400 mr-3" />
          <div>
            <h3 class="font-medium text-gray-900">Submit Event</h3>
            <p class="text-sm text-gray-600">Add a new event to the platform</p>
          </div>
        </router-link>
        
        <router-link
          to="/profile"
          class="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <Settings class="w-6 h-6 text-gray-400 mr-3" />
          <div>
            <h3 class="font-medium text-gray-900">Account Settings</h3>
            <p class="text-sm text-gray-600">Manage your profile and preferences</p>
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import {
  MessageSquare,
  Calendar,
  Star,
  Heart,
  Activity,
  Search,
  Plus,
  Settings
} from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import MyReviewsList from './MyReviewsList.vue'
import SubmittedEventsList from './SubmittedEventsList.vue'
import FavoritesList from './FavoritesList.vue'
import ActivityFeed from './ActivityFeed.vue'

const authStore = useAuthStore()

// State
const activeTab = ref('reviews')
const userStats = ref({
  total_reviews: 0,
  submitted_events: 0,
  average_rating: null as number | null
})

// Tab configuration
const tabs = [
  {
    id: 'reviews',
    name: 'My Reviews',
    icon: MessageSquare
  },
  {
    id: 'events',
    name: 'Submitted Events',
    icon: Calendar
  },
  {
    id: 'favorites',
    name: 'Favorites',
    icon: Heart
  },
  {
    id: 'activity',
    name: 'Activity',
    icon: Activity
  }
]

// Methods
async function loadUserStats() {
  try {
    // This would be actual API calls in a real implementation
    // For now, we'll use placeholder data
    userStats.value = {
      total_reviews: 12,
      submitted_events: 3,
      average_rating: 4.2
    }
  } catch (error) {
    console.error('Failed to load user stats:', error)
  }
}

// Lifecycle
onMounted(() => {
  loadUserStats()
})
</script>