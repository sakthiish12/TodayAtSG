<template>
  <div class="bg-white rounded-lg border border-gray-200 p-6 mb-6">
    <h3 class="text-lg font-semibold text-gray-900 mb-4">Reviews & Ratings</h3>
    
    <div v-if="loading" class="flex justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>
    
    <div v-else-if="stats" class="space-y-6">
      <!-- Overall Rating Summary -->
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <div class="text-3xl font-bold text-gray-900 mr-3">
            {{ stats.average_rating ? stats.average_rating.toFixed(1) : 'N/A' }}
          </div>
          <div>
            <div class="flex items-center mb-1">
              <Star
                v-for="star in 5"
                :key="star"
                class="w-5 h-5"
                :class="[
                  star <= Math.round(stats.average_rating || 0)
                    ? 'text-yellow-400 fill-current'
                    : 'text-gray-300'
                ]"
              />
            </div>
            <div class="text-sm text-gray-600">
              {{ stats.total_reviews }} {{ stats.total_reviews === 1 ? 'review' : 'reviews' }}
            </div>
          </div>
        </div>
        
        <button
          @click="$emit('write-review')"
          class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors text-sm font-medium"
        >
          Write Review
        </button>
      </div>
      
      <!-- Rating Distribution -->
      <div v-if="stats.total_reviews > 0" class="space-y-2">
        <h4 class="text-sm font-medium text-gray-700 mb-3">Rating Distribution</h4>
        <div 
          v-for="rating in [5, 4, 3, 2, 1]" 
          :key="rating"
          class="flex items-center space-x-3"
        >
          <div class="flex items-center space-x-1 w-12">
            <span class="text-sm text-gray-600">{{ rating }}</span>
            <Star class="w-3 h-3 text-yellow-400 fill-current" />
          </div>
          
          <div class="flex-1 bg-gray-200 rounded-full h-2">
            <div
              class="bg-yellow-400 h-2 rounded-full transition-all duration-300"
              :style="{ width: `${getRatingPercentage(rating)}%` }"
            ></div>
          </div>
          
          <span class="text-sm text-gray-600 w-12 text-right">
            {{ stats.rating_distribution[rating] || 0 }}
          </span>
        </div>
      </div>
      
      <!-- Recent Reviews Preview -->
      <div v-if="stats.recent_reviews && stats.recent_reviews.length > 0">
        <div class="flex items-center justify-between mb-3">
          <h4 class="text-sm font-medium text-gray-700">Recent Reviews</h4>
          <button
            @click="$emit('view-all-reviews')"
            class="text-sm text-blue-600 hover:text-blue-500"
          >
            View all
          </button>
        </div>
        
        <div class="space-y-3">
          <div 
            v-for="review in stats.recent_reviews.slice(0, 3)" 
            :key="review.id"
            class="bg-gray-50 rounded-lg p-3"
          >
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center">
                <div class="w-6 h-6 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mr-2 text-white font-medium text-xs">
                  {{ getUserInitials(review.user_name) }}
                </div>
                <span class="text-sm font-medium text-gray-900">{{ review.user_name }}</span>
              </div>
              
              <div class="flex items-center">
                <Star
                  v-for="star in 5"
                  :key="star"
                  class="w-3 h-3"
                  :class="[
                    star <= review.rating
                      ? 'text-yellow-400 fill-current'
                      : 'text-gray-300'
                  ]"
                />
              </div>
            </div>
            
            <p v-if="review.comment" class="text-sm text-gray-700 line-clamp-2">
              {{ review.comment }}
            </p>
            
            <div class="text-xs text-gray-500 mt-2">
              {{ formatDate(review.created_at) }}
            </div>
          </div>
        </div>
      </div>
      
      <!-- No Reviews State -->
      <div v-else-if="stats.total_reviews === 0" class="text-center py-8">
        <MessageSquare class="w-12 h-12 text-gray-400 mx-auto mb-3" />
        <h4 class="text-lg font-medium text-gray-900 mb-2">No reviews yet</h4>
        <p class="text-gray-600 mb-4">Be the first to share your experience!</p>
        <button
          @click="$emit('write-review')"
          class="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors font-medium"
        >
          Write the First Review
        </button>
      </div>
    </div>
    
    <div v-else-if="error" class="text-center py-8">
      <p class="text-red-600">Failed to load review statistics</p>
      <button
        @click="loadStats"
        class="mt-2 text-blue-600 hover:text-blue-500 text-sm"
      >
        Try again
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Star, MessageSquare } from 'lucide-vue-next'
import { apiService } from '@/services/api'
import type { ReviewStats } from '@/types'

interface Props {
  eventId: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'write-review': []
  'view-all-reviews': []
}>()

// State
const stats = ref<ReviewStats | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

// Computed
const getRatingPercentage = computed(() => {
  return (rating: number) => {
    if (!stats.value || stats.value.total_reviews === 0) return 0
    const count = stats.value.rating_distribution[rating] || 0
    return (count / stats.value.total_reviews) * 100
  }
})

// Methods
async function loadStats() {
  try {
    loading.value = true
    error.value = null
    
    stats.value = await apiService.getEventReviewStats(props.eventId)
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to load review statistics'
  } finally {
    loading.value = false
  }
}

function getUserInitials(name: string): string {
  if (!name) return '?'
  
  const parts = name.split(' ')
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return name.slice(0, 2).toUpperCase()
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now.getTime() - date.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 1) {
    return 'Yesterday'
  } else if (diffDays < 7) {
    return `${diffDays} days ago`
  } else {
    return date.toLocaleDateString('en-SG', {
      month: 'short',
      day: 'numeric'
    })
  }
}

// Lifecycle
onMounted(() => {
  loadStats()
})

// Expose methods for parent components
defineExpose({
  loadStats
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