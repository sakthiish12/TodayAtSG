<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-6 w-full max-w-md mx-4">
      <!-- Header -->
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-xl font-semibold text-gray-900">
          Report Review
        </h2>
        <button
          @click="$emit('close')"
          class="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <X class="w-6 h-6" />
        </button>
      </div>

      <!-- Success Message -->
      <div v-if="isSubmitted" class="text-center">
        <div class="mb-4">
          <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
            <Check class="h-6 w-6 text-green-600" />
          </div>
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">Report Submitted</h3>
        <p class="text-sm text-gray-600 mb-6">
          Thank you for reporting this review. Our team will investigate and take appropriate action.
        </p>
        <button
          @click="$emit('close')"
          class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
        >
          Close
        </button>
      </div>

      <!-- Form -->
      <form v-else @submit.prevent="handleSubmit">
        <div class="mb-4">
          <p class="text-sm text-gray-600 mb-4">
            Why are you reporting this review? Select the most appropriate reason.
          </p>
        </div>

        <!-- Error Display -->
        <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <p class="text-sm text-red-600">{{ error }}</p>
        </div>

        <!-- Reason Selection -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Reason for reporting
          </label>
          <div class="space-y-2">
            <label 
              v-for="option in reportReasons" 
              :key="option.value"
              class="flex items-center"
            >
              <input
                v-model="reportData.reason"
                :value="option.value"
                type="radio"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                required
              />
              <span class="ml-2 text-sm text-gray-700">{{ option.label }}</span>
            </label>
          </div>
        </div>

        <!-- Additional Description -->
        <div class="mb-6">
          <label for="description" class="block text-sm font-medium text-gray-700 mb-2">
            Additional details (optional)
          </label>
          <textarea
            id="description"
            v-model="reportData.description"
            rows="3"
            class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            placeholder="Provide more context about why you're reporting this review..."
            maxlength="500"
          ></textarea>
          <div class="text-xs text-gray-500 mt-1 text-right">
            {{ (reportData.description || '').length }}/500
          </div>
        </div>

        <div class="flex gap-3">
          <button
            type="button"
            @click="$emit('close')"
            class="flex-1 bg-white text-gray-700 border border-gray-300 py-2 px-4 rounded-md hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="loading || !reportData.reason"
            class="flex-1 bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="loading" class="flex items-center justify-center">
              <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Reporting...
            </span>
            <span v-else>Submit Report</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { X, Check } from 'lucide-vue-next'
import { apiService } from '@/services/api'
import type { ReviewReport } from '@/types'

interface Props {
  reviewId: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  reported: []
}>()

// State
const loading = ref(false)
const error = ref<string | null>(null)
const isSubmitted = ref(false)

const reportData = reactive<ReviewReport>({
  reason: '',
  description: ''
})

const reportReasons = [
  { value: 'inappropriate_content', label: 'Inappropriate or offensive content' },
  { value: 'spam', label: 'Spam or promotional content' },
  { value: 'fake_review', label: 'Fake or misleading review' },
  { value: 'harassment', label: 'Harassment or personal attacks' },
  { value: 'offensive_language', label: 'Offensive language or hate speech' },
  { value: 'other', label: 'Other (please specify in details)' }
]

// Methods
async function handleSubmit() {
  if (!reportData.reason) return
  
  try {
    loading.value = true
    error.value = null
    
    await apiService.reportReview(props.reviewId, reportData)
    
    isSubmitted.value = true
    emit('reported')
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to submit report'
  } finally {
    loading.value = false
  }
}
</script>