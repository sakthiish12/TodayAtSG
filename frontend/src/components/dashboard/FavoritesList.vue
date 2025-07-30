<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-semibold text-gray-900">Favorite Events</h3>
      <p class="text-sm text-gray-600">{{ favorites.length }} favorite{{ favorites.length !== 1 ? 's' : '' }}</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center py-8">
      <p class="text-red-600 mb-3">{{ error }}</p>
      <button
        @click="loadFavorites"
        class="text-blue-600 hover:text-blue-500 text-sm"
      >
        Try again
      </button>
    </div>

    <!-- Favorites List -->
    <div v-else-if="favorites.length > 0" class="space-y-4">
      <div
        v-for="favorite in favorites"
        :key="favorite.id"
        class="bg-gray-50 rounded-lg border border-gray-200 p-4"
      >
        <!-- Event Header -->
        <div class="flex items-start justify-between mb-3">
          <div class="flex-1">
            <h4 class="font-medium text-gray-900 mb-2">{{ favorite.title }}</h4>
            <p class="text-gray-600 text-sm mb-2">{{ favorite.description }}</p>
            
            <div class="flex items-center text-sm text-gray-500 space-x-4 mb-2">
              <span class="flex items-center">
                <Calendar class="w-4 h-4 mr-1" />
                {{ formatDate(favorite.date) }}
              </span>
              <span class="flex items-center">
                <MapPin class="w-4 h-4 mr-1" />
                {{ favorite.location }}
              </span>
              <span class="flex items-center">
                <Star class="w-4 h-4 mr-1" />
                {{ favorite.average_rating ? favorite.average_rating.toFixed(1) : 'No ratings' }}
              </span>
            </div>

            <div class="text-xs text-gray-400">
              Added to favorites {{ formatRelativeDate(favorite.favorited_at) }}
            </div>
          </div>
          
          <!-- Event Actions -->
          <div class="flex items-center space-x-2 ml-4">
            <router-link
              :to="`/events/${favorite.id}`"
              class="p-2 text-gray-400 hover:text-gray-600 rounded"
              title="View event"
            >
              <ExternalLink class="w-4 h-4" />
            </router-link>
            <button
              @click="removeFavorite(favorite.id)"
              class="p-2 text-red-400 hover:text-red-600 rounded"
              title="Remove from favorites"
            >
              <Heart class="w-4 h-4 fill-current" />
            </button>
          </div>
        </div>
      </div>

      <!-- Load More Button -->
      <div v-if="hasMore" class="text-center mt-6">
        <button
          @click="loadMoreFavorites"
          :disabled="loadingMore"
          class="bg-gray-100 text-gray-700 px-6 py-2 rounded-md hover:bg-gray-200 transition-colors disabled:opacity-50"
        >
          <span v-if="loadingMore" class="flex items-center">
            <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600 mr-2"></div>
            Loading...
          </span>
          <span v-else>Load More Favorites</span>
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-12">
      <Heart class="w-12 h-12 text-gray-400 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-2">No favorite events</h3>
      <p class="text-gray-600 mb-6">Start favoriting events you're interested in to see them here!</p>
      <router-link
        to="/events"
        class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
      >
        <Search class="w-4 h-4 mr-2" />
        Browse Events
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { 
  Calendar, 
  MapPin, 
  Star, 
  ExternalLink, 
  Heart,
  Search
} from 'lucide-vue-next'
import type { Event } from '@/types'

interface FavoriteEvent extends Event {
  favorited_at: string
}

// State
const favorites = ref<FavoriteEvent[]>([])
const loading = ref(false)
const loadingMore = ref(false)
const error = ref<string | null>(null)

// Pagination
const currentPage = ref(0)
const pageSize = ref(10)
const hasMore = ref(true)

// Methods
async function loadFavorites(reset = true) {
  try {
    if (reset) {
      loading.value = true
      currentPage.value = 0
      favorites.value = []
    } else {
      loadingMore.value = true
    }
    
    error.value = null
    
    // This would be an actual API call to get user's favorite events
    // For now, we'll simulate with placeholder data
    const mockFavorites: FavoriteEvent[] = [
      {
        id: 1,
        title: "Singapore Night Festival 2024",
        description: "Experience Singapore's arts and culture come alive at night",
        date: "2024-08-20",
        time: "19:00",
        location: "Civic District",
        latitude: 1.2966,
        longitude: 103.8520,
        category_id: 2,
        is_approved: true,
        source: 'scraped',
        average_rating: 4.7,
        review_count: 45,
        created_at: "2024-06-15T10:00:00Z",
        updated_at: "2024-06-15T10:00:00Z",
        favorited_at: "2024-07-20T14:30:00Z"
      }
    ]
    
    if (reset) {
      favorites.value = mockFavorites
    } else {
      favorites.value.push(...mockFavorites)
    }
    
    hasMore.value = false // No more mock data
    currentPage.value++
  } catch (err: any) {
    error.value = 'Failed to load favorite events'
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

async function loadMoreFavorites() {
  await loadFavorites(false)
}

async function removeFavorite(eventId: number) {
  if (!confirm('Remove this event from your favorites?')) {
    return
  }

  try {
    // This would be an actual API call to remove from favorites
    // For now, just remove from local state
    favorites.value = favorites.value.filter(f => f.id !== eventId)
  } catch (err: any) {
    console.error('Failed to remove favorite:', err)
    // You might want to show a toast notification here
  }
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-SG', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

function formatRelativeDate(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now.getTime() - date.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 1) {
    return 'yesterday'
  } else if (diffDays < 7) {
    return `${diffDays} days ago`
  } else if (diffDays < 30) {
    const weeks = Math.floor(diffDays / 7)
    return `${weeks} week${weeks !== 1 ? 's' : ''} ago`
  } else {
    return date.toLocaleDateString('en-SG', {
      month: 'short',
      year: 'numeric'
    })
  }
}

// Lifecycle
onMounted(() => {
  loadFavorites()
})
</script>