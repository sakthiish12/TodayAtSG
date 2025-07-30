<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-semibold text-gray-900">Submitted Events</h3>
      <router-link
        v-if="authStore.isEventOrganizer"
        to="/submit-event"
        class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm"
      >
        <Plus class="w-4 h-4 mr-2" />
        Submit New Event
      </router-link>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center py-8">
      <p class="text-red-600 mb-3">{{ error }}</p>
      <button
        @click="loadEvents"
        class="text-blue-600 hover:text-blue-500 text-sm"
      >
        Try again
      </button>
    </div>

    <!-- Events List -->
    <div v-else-if="events.length > 0" class="space-y-4">
      <div
        v-for="event in events"
        :key="event.id"
        class="bg-gray-50 rounded-lg border border-gray-200 p-4"
      >
        <!-- Event Header -->
        <div class="flex items-start justify-between mb-3">
          <div class="flex-1">
            <div class="flex items-center mb-2">
              <h4 class="font-medium text-gray-900 mr-3">{{ event.title }}</h4>
              <span
                :class="[
                  'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
                  getStatusColor(event.is_approved)
                ]"
              >
                {{ getStatusText(event.is_approved) }}
              </span>
            </div>
            
            <p class="text-gray-600 text-sm mb-2">{{ event.description }}</p>
            
            <div class="flex items-center text-sm text-gray-500 space-x-4">
              <span class="flex items-center">
                <Calendar class="w-4 h-4 mr-1" />
                {{ formatDate(event.date) }}
              </span>
              <span class="flex items-center">
                <MapPin class="w-4 h-4 mr-1" />
                {{ event.location }}
              </span>
              <span class="flex items-center">
                <Star class="w-4 h-4 mr-1" />
                {{ event.average_rating ? event.average_rating.toFixed(1) : 'No ratings' }}
              </span>
            </div>
          </div>
          
          <!-- Event Actions -->
          <div class="flex items-center space-x-2 ml-4">
            <router-link
              :to="`/events/${event.id}`"
              class="p-2 text-gray-400 hover:text-gray-600 rounded"
              title="View event"
            >
              <ExternalLink class="w-4 h-4" />
            </router-link>
            <button
              @click="editEvent(event)"
              class="p-2 text-gray-400 hover:text-gray-600 rounded"
              title="Edit event"
            >
              <Edit3 class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Event Stats -->
        <div class="flex items-center justify-between pt-3 border-t border-gray-200">
          <div class="flex items-center space-x-4 text-sm text-gray-500">
            <span>{{ event.review_count || 0 }} reviews</span>
            <span>Submitted {{ formatRelativeDate(event.created_at) }}</span>
          </div>
          
          <div v-if="event.source === 'user_submission'" class="text-xs text-gray-400">
            User Submission
          </div>
        </div>
      </div>

      <!-- Load More Button -->
      <div v-if="hasMore" class="text-center mt-6">
        <button
          @click="loadMoreEvents"
          :disabled="loadingMore"
          class="bg-gray-100 text-gray-700 px-6 py-2 rounded-md hover:bg-gray-200 transition-colors disabled:opacity-50"
        >
          <span v-if="loadingMore" class="flex items-center">
            <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600 mr-2"></div>
            Loading...
          </span>
          <span v-else>Load More Events</span>
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-12">
      <Calendar class="w-12 h-12 text-gray-400 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-2">No events submitted</h3>
      <div v-if="authStore.isEventOrganizer">
        <p class="text-gray-600 mb-6">Start sharing amazing events with the Singapore community!</p>
        <router-link
          to="/submit-event"
          class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          <Plus class="w-4 h-4 mr-2" />
          Submit Your First Event
        </router-link>
      </div>
      <div v-else>
        <p class="text-gray-600 mb-6">Become an event organizer to submit events to the platform.</p>
        <p class="text-sm text-gray-500">Contact support to upgrade your account.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { 
  Plus,
  Calendar, 
  MapPin, 
  Star, 
  ExternalLink, 
  Edit3 
} from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import type { Event } from '@/types'

const authStore = useAuthStore()

// State
const events = ref<Event[]>([])
const loading = ref(false)
const loadingMore = ref(false)
const error = ref<string | null>(null)

// Pagination
const currentPage = ref(0)
const pageSize = ref(10)
const hasMore = ref(true)

// Methods
async function loadEvents(reset = true) {
  try {
    if (reset) {
      loading.value = true
      currentPage.value = 0
      events.value = []
    } else {
      loadingMore.value = true
    }
    
    error.value = null
    
    // This would be an actual API call to get user's submitted events
    // For now, we'll simulate with placeholder data
    const mockEvents: Event[] = [
      {
        id: 1,
        title: "Singapore Food Festival 2024",
        description: "Discover the best of Singapore's culinary scene",
        date: "2024-08-15",
        time: "18:00",
        location: "Marina Bay Sands",
        latitude: 1.2834,
        longitude: 103.8607,
        category_id: 1,
        is_approved: true,
        source: 'user_submission',
        average_rating: 4.5,
        review_count: 23,
        created_at: "2024-07-01T10:00:00Z",
        updated_at: "2024-07-01T10:00:00Z"
      }
    ]
    
    if (reset) {
      events.value = mockEvents
    } else {
      events.value.push(...mockEvents)
    }
    
    hasMore.value = false // No more mock data
    currentPage.value++
  } catch (err: any) {
    error.value = 'Failed to load events'
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

async function loadMoreEvents() {
  await loadEvents(false)
}

function editEvent(event: Event) {
  // Navigate to edit event page or open edit modal
  console.log('Edit event:', event.id)
}

function getStatusColor(isApproved: boolean): string {
  return isApproved 
    ? 'bg-green-100 text-green-800'
    : 'bg-yellow-100 text-yellow-800'
}

function getStatusText(isApproved: boolean): string {
  return isApproved ? 'Approved' : 'Pending Review'
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
  loadEvents()
})
</script>