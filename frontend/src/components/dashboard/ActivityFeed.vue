<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-semibold text-gray-900">Recent Activity</h3>
      <button
        @click="loadActivity(true)"
        class="text-sm text-blue-600 hover:text-blue-500"
        :disabled="loading"
      >
        Refresh
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading && activities.length === 0" class="flex justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center py-8">
      <p class="text-red-600 mb-3">{{ error }}</p>
      <button
        @click="loadActivity(true)"
        class="text-blue-600 hover:text-blue-500 text-sm"
      >
        Try again
      </button>
    </div>

    <!-- Activity Feed -->
    <div v-else-if="activities.length > 0" class="space-y-4">
      <div
        v-for="activity in activities"
        :key="activity.id"
        class="flex items-start space-x-3 p-4 bg-gray-50 rounded-lg border border-gray-200"
      >
        <!-- Activity Icon -->
        <div class="flex-shrink-0">
          <div 
            :class="[
              'w-8 h-8 rounded-full flex items-center justify-center',
              getActivityColor(activity.type)
            ]"
          >
            <component :is="getActivityIcon(activity.type)" class="w-4 h-4" />
          </div>
        </div>
        
        <!-- Activity Content -->
        <div class="flex-1 min-w-0">
          <div class="text-sm">
            <span class="font-medium text-gray-900">{{ activity.title }}</span>
            <span class="text-gray-600">{{ activity.description }}</span>
          </div>
          
          <div class="mt-1 flex items-center text-xs text-gray-500 space-x-2">
            <span>{{ formatRelativeDate(activity.created_at) }}</span>
            <span v-if="activity.location" class="flex items-center">
              <MapPin class="w-3 h-3 mr-1" />
              {{ activity.location }}
            </span>
          </div>
          
          <!-- Activity Link -->
          <router-link
            v-if="activity.link"
            :to="activity.link"
            class="mt-2 inline-flex items-center text-xs text-blue-600 hover:text-blue-500"
          >
            View details
            <ExternalLink class="w-3 h-3 ml-1" />
          </router-link>
        </div>
        
        <!-- Activity Time -->
        <div class="flex-shrink-0 text-xs text-gray-400">
          {{ formatTime(activity.created_at) }}
        </div>
      </div>

      <!-- Load More Button -->
      <div v-if="hasMore" class="text-center mt-6">
        <button
          @click="loadMoreActivity"
          :disabled="loadingMore"
          class="bg-gray-100 text-gray-700 px-6 py-2 rounded-md hover:bg-gray-200 transition-colors disabled:opacity-50"
        >
          <span v-if="loadingMore" class="flex items-center">
            <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600 mr-2"></div>
            Loading...
          </span>
          <span v-else>Load More Activity</span>
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-12">
      <Activity class="w-12 h-12 text-gray-400 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-2">No recent activity</h3>
      <p class="text-gray-600 mb-6">Start interacting with events to see your activity here!</p>
      <router-link
        to="/events"
        class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
      >
        <Search class="w-4 h-4 mr-2" />
        Explore Events
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { 
  Activity,
  MessageSquare,
  Heart,
  Calendar,
  Plus,
  MapPin,
  ExternalLink,
  Search
} from 'lucide-vue-next'

interface ActivityItem {
  id: string
  type: 'review' | 'favorite' | 'event_submission' | 'event_update'
  title: string
  description: string
  location?: string
  link?: string
  created_at: string
}

// State
const activities = ref<ActivityItem[]>([])
const loading = ref(false)
const loadingMore = ref(false)
const error = ref<string | null>(null)

// Pagination
const currentPage = ref(0)
const pageSize = ref(15)
const hasMore = ref(true)

// Methods
async function loadActivity(reset = true) {
  try {
    if (reset) {
      loading.value = true
      currentPage.value = 0
      activities.value = []
    } else {
      loadingMore.value = true
    }
    
    error.value = null
    
    // This would be an actual API call to get user's activity feed
    // For now, we'll simulate with placeholder data
    const mockActivities: ActivityItem[] = [
      {
        id: '1',
        type: 'review',
        title: 'You reviewed',
        description: 'Singapore Food Festival 2024 - "Amazing variety of local dishes!"',
        location: 'Marina Bay Sands',
        link: '/events/1',
        created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString() // 2 hours ago
      },
      {
        id: '2',
        type: 'favorite',
        title: 'You favorited',
        description: 'Singapore Night Festival 2024',
        location: 'Civic District',
        link: '/events/2',
        created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString() // 1 day ago
      },
      {
        id: '3',
        type: 'event_submission',
        title: 'You submitted',
        description: 'Tech Conference Singapore 2024 (pending approval)',
        location: 'Suntec City',
        link: '/events/3',
        created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString() // 3 days ago
      }
    ]
    
    if (reset) {
      activities.value = mockActivities
    } else {
      activities.value.push(...mockActivities)
    }
    
    hasMore.value = false // No more mock data
    currentPage.value++
  } catch (err: any) {
    error.value = 'Failed to load activity feed'
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

async function loadMoreActivity() {
  await loadActivity(false)
}

function getActivityIcon(type: string) {
  const icons = {
    review: MessageSquare,
    favorite: Heart,
    event_submission: Plus,
    event_update: Calendar
  }
  return icons[type] || Activity
}

function getActivityColor(type: string): string {
  const colors = {
    review: 'bg-blue-100 text-blue-600',
    favorite: 'bg-red-100 text-red-600',
    event_submission: 'bg-green-100 text-green-600',
    event_update: 'bg-yellow-100 text-yellow-600'
  }
  return colors[type] || 'bg-gray-100 text-gray-600'
}

function formatRelativeDate(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now.getTime() - date.getTime())
  const diffHours = Math.ceil(diffTime / (1000 * 60 * 60))
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffHours < 1) {
    return 'Just now'
  } else if (diffHours < 24) {
    return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`
  } else if (diffDays < 7) {
    return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`
  } else if (diffDays < 30) {
    const weeks = Math.floor(diffDays / 7)
    return `${weeks} week${weeks !== 1 ? 's' : ''} ago`
  } else {
    return date.toLocaleDateString('en-SG', {
      month: 'short',
      day: 'numeric'
    })
  }
}

function formatTime(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleTimeString('en-SG', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Lifecycle
onMounted(() => {
  loadActivity()
})
</script>