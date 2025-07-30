<template>
  <div class="bg-white rounded-lg border border-gray-200 p-4 mb-4">
    <!-- Review header -->
    <div class="flex items-start justify-between mb-3">
      <div class="flex items-center">
        <!-- User avatar -->
        <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mr-3 text-white font-medium text-sm">
          {{ getUserInitials(review.user_name) }}
        </div>
        
        <!-- User info and rating -->
        <div>
          <div class="flex items-center">
            <span class="font-medium text-gray-900 mr-2">
              {{ review.user_name }}
            </span>
            <!-- Verified badge -->
            <span v-if="review.is_verified" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
              <CheckCircle class="w-3 h-3 mr-1" />
              Verified
            </span>
          </div>
          
          <!-- Rating stars -->
          <div class="flex items-center mt-1">
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
            <span class="text-sm text-gray-600 ml-2">{{ review.rating }}/5</span>
          </div>
        </div>
      </div>
      
      <!-- Review date and menu -->
      <div class="flex items-center space-x-2">
        <span class="text-sm text-gray-500">
          {{ formatDate(review.created_at) }}
        </span>
        
        <!-- Review menu for own reviews or admin -->
        <div v-if="canEdit || canModerate" class="relative" ref="menuRef">
          <button
            @click="showMenu = !showMenu"
            class="p-1 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100"
          >
            <MoreVertical class="w-4 h-4" />
          </button>
          
          <!-- Dropdown menu -->
          <div
            v-if="showMenu"
            class="absolute right-0 mt-1 w-32 bg-white rounded-md shadow-lg py-1 z-10 border border-gray-200"
          >
            <button
              v-if="canEdit"
              @click="editReview"
              class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
            >
              <Edit3 class="w-4 h-4 mr-2 inline" />
              Edit
            </button>
            <button
              v-if="canDelete"
              @click="deleteReview"
              class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100"
            >
              <Trash2 class="w-4 h-4 mr-2 inline" />
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Review comment -->
    <div v-if="review.comment" class="text-gray-700 leading-relaxed mb-3">
      {{ review.comment }}
    </div>
    
    <!-- Review actions -->
    <div class="flex items-center justify-between pt-3 border-t border-gray-100">
      <div class="flex items-center space-x-4">
        <!-- Helpful button (placeholder for future feature) -->
        <button
          class="flex items-center text-sm text-gray-600 hover:text-gray-900 transition-colors"
          @click="toggleHelpful"
          disabled
        >
          <ThumbsUp class="w-4 h-4 mr-1" />
          Helpful ({{ helpfulCount }})
        </button>
        
        <!-- Report button -->
        <button
          v-if="!isOwnReview"
          class="flex items-center text-sm text-gray-600 hover:text-red-600 transition-colors"
          @click="reportReview"
        >
          <Flag class="w-4 h-4 mr-1" />
          Report
        </button>
      </div>
      
      <!-- Updated/edited indicator -->
      <div v-if="isEdited" class="text-xs text-gray-500">
        Edited
      </div>
    </div>
    
    <!-- Report Modal -->
    <ReportModal
      v-if="showReportModal"
      :review-id="review.id"
      @close="showReportModal = false"
      @reported="handleReported"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { 
  Star, 
  CheckCircle, 
  ThumbsUp, 
  Flag, 
  MoreVertical, 
  Edit3, 
  Trash2 
} from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import ReportModal from './ReportModal.vue'
import type { Review } from '@/types'

interface Props {
  review: Review
}

const props = defineProps<Props>()

const emit = defineEmits<{
  delete: [reviewId: number]
  edit: [review: Review]
  report: [reviewId: number]
}>()

const authStore = useAuthStore()

// State
const helpfulCount = ref(0) // This would come from the API in a real app
const isHelpful = ref(false)
const showMenu = ref(false)
const showReportModal = ref(false)
const menuRef = ref<HTMLElement>()

// Computed
const isOwnReview = computed(() => {
  return authStore.user?.id === props.review.user_id
})

const canEdit = computed(() => {
  return isOwnReview.value
})

const canDelete = computed(() => {
  return isOwnReview.value || authStore.user?.is_admin
})

const canModerate = computed(() => {
  return authStore.user?.is_admin
})

const isEdited = computed(() => {
  return props.review.updated_at !== props.review.created_at
})

// Methods
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
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }
}

function toggleHelpful() {
  // This would make an API call in a real app
  isHelpful.value = !isHelpful.value
  helpfulCount.value += isHelpful.value ? 1 : -1
}

function editReview() {
  showMenu.value = false
  emit('edit', props.review)
}

function reportReview() {
  showReportModal.value = true
}

function deleteReview() {
  showMenu.value = false
  if (confirm('Are you sure you want to delete this review?')) {
    emit('delete', props.review.id)
  }
}

function handleReported() {
  showReportModal.value = false
  emit('report', props.review.id)
}

function handleClickOutside(event: MouseEvent) {
  if (menuRef.value && !menuRef.value.contains(event.target as Node)) {
    showMenu.value = false
  }
}

// Lifecycle
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>