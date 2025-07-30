<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-6 w-full max-w-md mx-4">
      <!-- Header -->
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-xl font-semibold text-gray-900">
          Edit Review
        </h2>
        <button
          @click="$emit('close')"
          class="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <X class="w-6 h-6" />
        </button>
      </div>

      <!-- Error Display -->
      <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
        <p class="text-sm text-red-600">{{ error }}</p>
      </div>

      <!-- Edit Form -->
      <form @submit.prevent="handleSubmit">
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
        <div class="mb-6">
          <label for="comment" class="block text-sm font-medium text-gray-700 mb-2">
            Comment (optional)
          </label>
          <textarea
            id="comment"
            v-model="comment"
            rows="4"
            class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            placeholder="Update your thoughts about this event..."
            maxlength="500"
          ></textarea>
          <div class="text-xs text-gray-500 mt-1 text-right">
            {{ comment.length }}/500
          </div>
        </div>
        
        <!-- Form actions -->
        <div class="flex items-center justify-end gap-3">
          <button
            type="button"
            @click="$emit('close')"
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
              Updating...
            </span>
            <span v-else>Update Review</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { X, Star } from 'lucide-vue-next'
import { apiService } from '@/services/api'
import type { Review, ReviewUpdate } from '@/types'

interface Props {
  review: Review
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  updated: [review: Review]
}>()

// State
const rating = ref(0)
const hoverRating = ref(0)
const comment = ref('')
const loading = ref(false)
const error = ref<string | null>(null)

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

async function handleSubmit() {
  if (!rating.value) return
  
  try {
    loading.value = true
    error.value = null
    
    const updateData: ReviewUpdate = {
      rating: rating.value,
      comment: comment.value.trim() || undefined
    }
    
    const updatedReview = await apiService.updateReview(props.review.id, updateData)
    
    emit('updated', updatedReview)
  } catch (err: any) {
    let errorMessage = 'Failed to update review'
    if (err.response?.data?.detail) {
      const detail = err.response.data.detail
      if (Array.isArray(detail)) {
        errorMessage = detail[0]?.msg || errorMessage
      } else {
        errorMessage = detail
      }
    }
    
    error.value = errorMessage
  } finally {
    loading.value = false
  }
}

// Initialize form with current review data
onMounted(() => {
  rating.value = props.review.rating
  comment.value = props.review.comment || ''
})
</script>