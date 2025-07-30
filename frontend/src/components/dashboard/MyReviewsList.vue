<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-semibold text-gray-900">My Reviews</h3>
      <p class="text-sm text-gray-600">{{ totalReviews }} review{{ totalReviews !== 1 ? 's' : '' }}</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center py-8">
      <p class="text-red-600 mb-3">{{ error }}</p>
      <button
        @click="loadReviews"
        class="text-blue-600 hover:text-blue-500 text-sm"
      >
        Try again
      </button>
    </div>

    <!-- Reviews List -->
    <div v-else-if="reviews.length > 0" class="space-y-4">
      <!-- Edit Review Modal -->
      <EditReviewModal
        v-if="editingReview"
        :review="editingReview"
        @close="editingReview = null"
        @updated="handleReviewUpdated"
      />

      <!-- Review Items -->
      <div
        v-for="review in reviews"
        :key="review.id"
        class="bg-gray-50 rounded-lg border border-gray-200 p-4"
      >
        <!-- Review Header -->
        <div class="flex items-start justify-between mb-3">
          <div class="flex-1">
            <h4 class="font-medium text-gray-900 mb-1">
              Review for Event #{{ review.event_id }}
            </h4>
            <div class="flex items-center mb-2">
              <div class="flex">
                <Star
                  v-for="star in 5"
                  :key="star"
                  class="w-4 h-4"
                  :class="[
                    star <= review.rating
                      ? 'text-yellow-400 fill-current'
                      : 'text-gray-300'
                  ]"
                />
              </div>
              <span class="ml-2 text-sm text-gray-600">{{ review.rating }}/5</span>
            </div>
          </div>
          
          <!-- Review Actions -->
          <div class="flex items-center space-x-2">
            <button
              @click="editReview(review)"
              class="p-1 text-gray-400 hover:text-gray-600 rounded"
              title="Edit review"
            >
              <Edit3 class="w-4 h-4" />
            </button>
            <button
              @click="deleteReview(review.id)"
              class="p-1 text-gray-400 hover:text-red-600 rounded"
              title="Delete review"
            >
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Review Comment -->
        <div v-if="review.comment" class="text-gray-700 mb-3">
          {{ review.comment }}
        </div>

        <!-- Review Meta -->
        <div class="flex items-center justify-between text-sm text-gray-500">
          <span>{{ formatDate(review.created_at) }}</span>
          <span v-if="isEdited(review)" class="italic">Edited</span>
        </div>
      </div>

      <!-- Load More Button -->
      <div v-if="hasMore" class="text-center mt-6">
        <button
          @click="loadMoreReviews"
          :disabled="loadingMore"
          class="bg-gray-100 text-gray-700 px-6 py-2 rounded-md hover:bg-gray-200 transition-colors disabled:opacity-50"
        >
          <span v-if="loadingMore" class="flex items-center">
            <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600 mr-2"></div>
            Loading...
          </span>
          <span v-else>Load More Reviews</span>
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-12">
      <MessageSquare class="w-12 h-12 text-gray-400 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-2">No reviews yet</h3>
      <p class="text-gray-600 mb-6">Start exploring events and share your experiences!</p>
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
  Star, 
  MessageSquare, 
  Edit3, 
  Trash2, 
  Search 
} from 'lucide-vue-next'
import { apiService } from '@/services/api'
import EditReviewModal from '@/components/event/EditReviewModal.vue'
import type { Review, ReviewListResponse } from '@/types'

// State
const reviews = ref<Review[]>([])
const totalReviews = ref(0)
const loading = ref(false)
const loadingMore = ref(false)
const error = ref<string | null>(null)
const editingReview = ref<Review | null>(null)

// Pagination
const currentPage = ref(0)
const pageSize = ref(10)
const hasMore = ref(true)

// Methods
async function loadReviews(reset = true) {
  try {
    if (reset) {
      loading.value = true
      currentPage.value = 0
      reviews.value = []
    } else {
      loadingMore.value = true
    }
    
    error.value = null
    
    const response: ReviewListResponse = await apiService.getMyReviews({
      skip: currentPage.value * pageSize.value,
      limit: pageSize.value
    })
    
    if (reset) {
      reviews.value = response.reviews
    } else {
      reviews.value.push(...response.reviews)
    }
    
    totalReviews.value = response.total
    hasMore.value = response.reviews.length === pageSize.value && 
                    reviews.value.length < response.total
    
    currentPage.value++
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to load reviews'
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

async function loadMoreReviews() {
  await loadReviews(false)
}

function editReview(review: Review) {
  editingReview.value = review
}

function handleReviewUpdated(updatedReview: Review) {
  const index = reviews.value.findIndex(r => r.id === updatedReview.id)
  if (index !== -1) {
    reviews.value[index] = updatedReview
  }
  editingReview.value = null
}

async function deleteReview(reviewId: number) {
  if (!confirm('Are you sure you want to delete this review?')) {
    return
  }

  try {
    await apiService.deleteReview(reviewId)
    
    reviews.value = reviews.value.filter(r => r.id !== reviewId)
    totalReviews.value--
  } catch (err: any) {
    console.error('Failed to delete review:', err)
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

function isEdited(review: Review): boolean {
  return review.updated_at !== review.created_at
}

// Lifecycle
onMounted(() => {
  loadReviews()
})
</script>