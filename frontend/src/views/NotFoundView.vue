<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center">
    <div class="text-center px-4">
      <!-- 404 Illustration -->
      <div class="mb-8">
        <div class="text-9xl font-bold text-gray-300 mb-4">404</div>
        <div class="flex justify-center space-x-4 text-6xl mb-4">
          <span class="animate-bounce">🗺️</span>
          <span class="animate-bounce" style="animation-delay: 0.1s">📍</span>
          <span class="animate-bounce" style="animation-delay: 0.2s">🎉</span>
        </div>
      </div>
      
      <!-- Error message -->
      <h1 class="text-4xl font-bold text-gray-900 mb-4">
        Oops! Page Not Found
      </h1>
      
      <p class="text-xl text-gray-600 mb-8 max-w-md mx-auto">
        Looks like you've wandered off the map! The page you're looking for doesn't exist.
      </p>
      
      <!-- Action buttons -->
      <div class="flex flex-col sm:flex-row gap-4 justify-center">
        <router-link
          to="/"
          class="bg-blue-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors inline-flex items-center justify-center"
        >
          <Home class="w-5 h-5 mr-2" />
          Go Home
        </router-link>
        
        <router-link
          to="/events"
          class="bg-gray-100 text-gray-700 px-8 py-3 rounded-lg font-medium hover:bg-gray-200 transition-colors inline-flex items-center justify-center"
        >
          <Calendar class="w-5 h-5 mr-2" />
          Browse Events
        </router-link>
        
        <router-link
          to="/map"
          class="bg-gray-100 text-gray-700 px-8 py-3 rounded-lg font-medium hover:bg-gray-200 transition-colors inline-flex items-center justify-center"
        >
          <Map class="w-5 h-5 mr-2" />
          View Map
        </router-link>
      </div>
      
      <!-- Popular events section -->
      <div class="mt-16 max-w-4xl mx-auto">
        <h2 class="text-2xl font-semibold text-gray-900 mb-6">
          Popular Events Right Now
        </h2>
        
        <div v-if="popularEvents.length > 0" class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <router-link
            v-for="event in popularEvents"
            :key="event.id"
            :to="`/events/${event.id}`"
            class="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-4 text-left"
          >
            <div class="flex items-center mb-2">
              <span class="text-2xl mr-2">{{ getCategoryIcon(event.category?.name) }}</span>
              <span 
                class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium text-white"
                :style="{ backgroundColor: getCategoryColor(event.category?.name) }"
              >
                {{ event.category?.name }}
              </span>
            </div>
            
            <h3 class="font-semibold text-gray-900 mb-2 line-clamp-2">
              {{ event.title }}
            </h3>
            
            <div class="text-sm text-gray-600 mb-2">
              {{ formatEventDate(event.date) }} • {{ event.location }}
            </div>
            
            <div v-if="event.average_rating" class="flex items-center">
              <div class="flex items-center mr-2">
                <Star 
                  v-for="star in 5"
                  :key="star"
                  class="w-3 h-3"
                  :class="[
                    star <= Math.round(event.average_rating || 0)
                      ? 'text-yellow-400 fill-current'
                      : 'text-gray-300'
                  ]"
                />
              </div>
              <span class="text-sm text-gray-600">
                {{ event.average_rating.toFixed(1) }}
              </span>
            </div>
          </router-link>
        </div>
        
        <div v-else class="text-center py-8">
          <p class="text-gray-600">No popular events available at the moment.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { 
  Home, 
  Calendar, 
  Map,
  Star
} from 'lucide-vue-next'
import { useEventsStore } from '@/stores/events'
import type { Event } from '@/types'

// Store
const eventsStore = useEventsStore()
const { featuredEvents } = storeToRefs(eventsStore)

// State
const popularEvents = ref<Event[]>([])

// Methods
function getCategoryIcon(categoryName?: string): string {
  const iconMap: Record<string, string> = {
    'concerts': '🎵',
    'festivals': '🎪',
    'dj events': '🎧',
    'kids events': '🎠',
    'food & drink': '🍽️',
    'art & culture': '🎨',
    'sports': '⚽',
    'nightlife': '🌙',
    'workshops': '🛠️',
    'markets': '🛒'
  }
  
  const category = categoryName?.toLowerCase() || 'default'
  return iconMap[category] || '📍'
}

function getCategoryColor(categoryName?: string): string {
  const colorMap: Record<string, string> = {
    'concerts': '#E91E63',
    'festivals': '#9C27B0',
    'dj events': '#3F51B5',
    'kids events': '#FF9800',
    'food & drink': '#4CAF50',
    'art & culture': '#F44336',
    'sports': '#2196F3',
    'nightlife': '#673AB7',
    'workshops': '#795548',
    'markets': '#607D8B'
  }
  
  const category = categoryName?.toLowerCase() || 'default'
  return colorMap[category] || '#757575'
}

function formatEventDate(dateString: string): string {
  const date = new Date(dateString)
  const today = new Date()
  const tomorrow = new Date(today)
  tomorrow.setDate(tomorrow.getDate() + 1)
  
  if (date.toDateString() === today.toDateString()) {
    return 'Today'
  } else if (date.toDateString() === tomorrow.toDateString()) {
    return 'Tomorrow'
  } else {
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric' 
    })
  }
}

async function loadPopularEvents() {
  try {
    await eventsStore.fetchEvents()
    popularEvents.value = featuredEvents.value.slice(0, 3)
  } catch (error) {
    console.error('Failed to load popular events:', error)
  }
}

// Lifecycle
onMounted(() => {
  loadPopularEvents()
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>