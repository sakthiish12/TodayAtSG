<template>
  <div class="bg-white rounded-lg border border-gray-200 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-semibold text-gray-900">
        Reviews ({{ totalReviews }})
      </h3>
      
      <!-- Sort Options -->
      <div class="flex items-center space-x-3">
        <label class="text-sm text-gray-600">Sort by:</label>
        <select
          v-model="sortBy"
          @change="loadReviews"
          class="text-sm border border-gray-300 rounded-md px-3 py-1 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="created_at">Most Recent</option>
          <option value="rating">Highest Rated</option>
        </select>
        
        <button
          @click="toggleSortOrder"
          class="p-1 text-gray-400 hover:text-gray-600 rounded"
          :title="sortOrder === 'desc' ? 'Sort Ascending' : 'Sort Descending'"
        >
          <ArrowUpDown class="w-4 h-4" />
        </button>
      </div>
    </div>
    
    <!-- Review Form for Authenticated Users -->
    <div v-if="showReviewForm && authStore.isAuthenticated" class="mb-6">
      <ReviewForm
        :event-id="eventId"
        @review-added="handleReviewAdded"
        @cancel="showReviewForm = false"
      />
    </div>
    
    <!-- Add Review Button -->
    <div v-else-if="!hasUserReviewed && authStore.isAuthenticated" class="mb-6">
      <button
        @click="showReviewForm = true"
        class="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
      >
        <Plus class="w-4 h-4" />
        <span>Write a Review</span>
      </button>
    </div>
    
    <!-- Login Prompt -->
    <div v-else-if="!authStore.isAuthenticated" class="mb-6 p-4 bg-gray-50 rounded-lg">
      <p class="text-gray-600 mb-3">Sign in to write a review for this event.</p>
      <button
        @click="$emit('login-required')"
        class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors text-sm"
      >
        Sign In to Review
      </button>
    </div>
    
    <!-- User Already Reviewed -->
    <div v-else-if="hasUserReviewed" class="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
      <div class="flex items-center">
        <CheckCircle class="w-5 h-5 text-green-600 mr-2" />
        <span class="text-green-800 text-sm">You have already reviewed this event.</span>
      </div>
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
      
      <!-- Reviews -->
      <ReviewItem
        v-for="review in reviews"
        :key="review.id"
        :review="review"
        @delete="handleDeleteReview"
        @edit="handleEditReview"
        @report="handleReportReview"
      />
      
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
    
    <!-- No Reviews State -->
    <div v-else class="text-center py-8">
      <MessageSquare class="w-12 h-12 text-gray-400 mx-auto mb-3" />
      <h4 class="text-lg font-medium text-gray-900 mb-2">No reviews yet</h4>
      <p class="text-gray-600">Be the first to share your experience with this event!</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { 
  Plus, 
  ArrowUpDown, 
  CheckCircle, 
  MessageSquare 
} from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { apiService } from '@/services/api'
import ReviewForm from './ReviewForm.vue'
import ReviewItem from './ReviewItem.vue'
import EditReviewModal from './EditReviewModal.vue'
import type { Review, ReviewListResponse } from '@/types'

interface Props {
  eventId: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'login-required': []
  'review-added': [review: Review]
}>()

const authStore = useAuthStore()
const { user } = storeToRefs(authStore)

// State
const reviews = ref<Review[]>([])
const totalReviews = ref(0)
const loading = ref(false)
const loadingMore = ref(false)
const error = ref<string | null>(null)
const showReviewForm = ref(false)
const editingReview = ref<Review | null>(null)

// Pagination
const currentPage = ref(0)
const pageSize = ref(10)
const hasMore = ref(true)

// Sorting
const sortBy = ref<'created_at' | 'rating'>('created_at')
const sortOrder = ref<'asc' | 'desc'>('desc')

// Computed
const hasUserReviewed = computed(() => {
  return user.value ? reviews.value.some(review => review.user_id === user.value?.id) : false
})

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
    
    const response: ReviewListResponse = await apiService.getEventReviews(props.eventId, {
      skip: currentPage.value * pageSize.value,
      limit: pageSize.value,
      sort_by: sortBy.value,
      sort_order: sortOrder.value
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

function toggleSortOrder() {
  sortOrder.value = sortOrder.value === 'desc' ? 'asc' : 'desc'
  loadReviews()
}

function handleReviewAdded(review: Review) {
  reviews.value.unshift(review)
  totalReviews.value++
  showReviewForm.value = false
  emit('review-added', review)
}

function handleEditReview(review: Review) {
  editingReview.value = review
}

function handleReviewUpdated(updatedReview: Review) {
  const index = reviews.value.findIndex(r => r.id === updatedReview.id)
  if (index !== -1) {
    reviews.value[index] = updatedReview
  }
  editingReview.value = null
}

async function handleDeleteReview(reviewId: number) {
  try {
    await apiService.deleteReview(reviewId)
    
    reviews.value = reviews.value.filter(r => r.id !== reviewId)
    totalReviews.value--
  } catch (err: any) {
    console.error('Failed to delete review:', err)
    // You might want to show a toast notification here
  }
}

function handleReportReview(reviewId: number) {
  // Review reported successfully
  console.log('Review reported:', reviewId)
  // You might want to show a success message or refresh the reviews
}

// Lifecycle
onMounted(() => {
  loadReviews()
})

// Expose methods for parent components
defineExpose({
  loadReviews
})
</script>