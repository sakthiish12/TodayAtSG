<template>
  <div class="bg-gray-50 rounded-lg p-4">
    <form @submit.prevent="submitReview">
      <!-- Rating input -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Rating
        </label>
        <div class="flex items-center gap-1">
          <button
            v-for="star in 5"
            :key="star"
            type="button"
            @click="setRating(star)"
            @mouseenter="hoverRating = star"
            @mouseleave="hoverRating = 0"
            class="p-1 transition-transform hover:scale-110"
          >
            <Star
              class="w-6 h-6 transition-colors"
              :class="[
                star <= (hoverRating || rating)
                  ? 'text-yellow-400 fill-current'
                  : 'text-gray-300'
              ]"
            />
          </button>
          <span class="ml-2 text-sm text-gray-600">
            {{ getRatingText(rating) }}
          </span>
        </div>
      </div>
      
      <!-- Comment input -->
      <div class="mb-4">
        <label for="comment" class="block text-sm font-medium text-gray-700 mb-2">
          Comment (optional)
        </label>
        <textarea
          id="comment"
          v-model="comment"
          rows="3"
          class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
          placeholder="Share your thoughts about this event..."
          maxlength="500"
        ></textarea>
        <div class="text-xs text-gray-500 mt-1 text-right">
          {{ comment.length }}/500
        </div>
      </div>
      
      <!-- Form actions -->
      <div class="flex items-center justify-end gap-2">
        <button
          type="button"
          @click="$emit('cancel')"
          class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
          :disabled="loading"
        >
          Cancel
        </button>
        <button
          type="submit"
          class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="!rating || loading"
        >
          <span v-if="loading" class="flex items-center">
            <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            Submitting...
          </span>
          <span v-else>Submit Review</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Star } from 'lucide-vue-next'
import { apiService } from '@/services/api'
import type { Review } from '@/types'

interface Props {
  eventId?: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  reviewAdded: [review: Review]
  cancel: []
}>()

// State
const rating = ref(0)
const hoverRating = ref(0)
const comment = ref('')
const loading = ref(false)

// Methods
function setRating(value: number) {
  rating.value = value
}

function getRatingText(value: number): string {
  const texts = [
    '',
    'Poor',
    'Fair', 
    'Good',
    'Very Good',
    'Excellent'
  ]
  return texts[value] || ''
}

async function submitReview() {
  if (!rating.value || !props.eventId) return
  
  try {
    loading.value = true
    
    const reviewData = {
      event_id: props.eventId,
      rating: rating.value,
      comment: comment.value.trim() || undefined
    }
    
    const newReview = await apiService.createReview(reviewData)
    
    // Reset form
    rating.value = 0
    comment.value = ''
    hoverRating.value = 0
    
    emit('reviewAdded', newReview)
    
  } catch (error: any) {
    console.error('Failed to submit review:', error)
    
    // Show specific error messages
    let errorMessage = 'Failed to submit review'
    if (error.response?.data?.detail) {
      const detail = error.response.data.detail
      if (Array.isArray(detail)) {
        errorMessage = detail[0]?.msg || errorMessage
      } else {
        errorMessage = detail
      }
    }
    
    // You can emit an error event or show a toast notification
    // For now, we'll log it to console
    console.error('Review submission error:', errorMessage)
  } finally {
    loading.value = false
  }
}
</script>