<template>
  <Teleport to="body">
    <div
      v-if="isOpen"
      class="fixed inset-0 z-50 overflow-y-auto"
      @click="handleBackdropClick"
    >
      <!-- Backdrop -->
      <div class="fixed inset-0 bg-black bg-opacity-50 transition-opacity"></div>
      
      <!-- Modal container -->
      <div class="flex min-h-full items-center justify-center p-4">
        <div
          ref="modalContent"
          class="relative bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
          @click.stop
        >
          <!-- Close button -->
          <button
            @click="$emit('close')"
            class="absolute top-4 right-4 z-10 p-2 rounded-full bg-white bg-opacity-90 hover:bg-opacity-100 transition-all shadow-md"
          >
            <X class="w-5 h-5 text-gray-600" />
          </button>
          
          <!-- Modal content -->
          <div class="flex flex-col md:flex-row max-h-[90vh]">
            <!-- Event header image -->
            <div 
              class="w-full md:w-1/2 h-64 md:h-auto bg-gradient-to-br relative"
              :style="{ background: `linear-gradient(135deg, ${categoryColor}, ${categoryColorSecondary})` }"
            >
              <!-- Category icon -->
              <div class="absolute inset-0 flex items-center justify-center">
                <div class="text-8xl opacity-20">
                  {{ getCategoryIcon(event?.category?.name) }}
                </div>
              </div>
              
              <!-- Event status badges -->
              <div class="absolute top-4 left-4 flex flex-col gap-2">
                <span 
                  class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium text-white"
                  :style="{ backgroundColor: categoryColor }"
                >
                  {{ event?.category?.name || 'Event' }}
                </span>
                
                <span 
                  v-if="event?.age_restrictions"
                  class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium text-white bg-red-500"
                >
                  {{ event.age_restrictions }}
                </span>
                
                <span 
                  v-if="!event?.is_approved"
                  class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium text-white bg-orange-500"
                >
                  <AlertCircle class="w-4 h-4 mr-1" />
                  Pending Approval
                </span>
              </div>
              
              <!-- Date display -->
              <div class="absolute bottom-4 left-4 bg-white bg-opacity-95 rounded-lg px-4 py-3">
                <div class="text-sm font-medium text-gray-600">
                  {{ formatFullDate(event?.date) }}
                </div>
                <div class="text-2xl font-bold text-gray-900">
                  {{ event?.time }}
                </div>
              </div>
            </div>
            
            <!-- Event details -->
            <div class="w-full md:w-1/2 overflow-y-auto">
              <div class="p-6">
                <!-- Event title and rating -->
                <div class="mb-4">
                  <h1 class="text-2xl font-bold text-gray-900 mb-2">
                    {{ event?.title }}
                  </h1>
                  
                  <div 
                    v-if="event?.average_rating || event?.review_count"
                    class="flex items-center gap-4"
                  >
                    <div class="flex items-center">
                      <div class="flex items-center mr-2">
                        <Star 
                          v-for="star in 5"
                          :key="star"
                          class="w-5 h-5"
                          :class="[
                            star <= Math.round(event?.average_rating || 0)
                              ? 'text-yellow-400 fill-current'
                              : 'text-gray-300'
                          ]"
                        />
                      </div>
                      <span class="text-lg font-medium text-gray-900">
                        {{ event?.average_rating?.toFixed(1) || '0.0' }}
                      </span>
                    </div>
                    
                    <span class="text-sm text-gray-600">
                      {{ event?.review_count || 0 }} review{{ (event?.review_count || 0) !== 1 ? 's' : '' }}
                    </span>
                  </div>
                </div>
                
                <!-- Event description -->
                <div v-if="event?.description" class="mb-6">
                  <h3 class="text-lg font-semibold text-gray-900 mb-2">About</h3>
                  <p class="text-gray-700 whitespace-pre-line leading-relaxed">
                    {{ event.description }}
                  </p>
                </div>
                
                <!-- Event details -->
                <div class="space-y-4 mb-6">
                  <!-- Location -->
                  <div class="flex items-start">
                    <MapPin class="w-5 h-5 text-gray-400 mt-0.5 mr-3" />
                    <div>
                      <p class="font-medium text-gray-900">{{ event?.location }}</p>
                      <button
                        @click="navigateToLocation"
                        class="text-sm text-blue-600 hover:text-blue-700 transition-colors"
                      >
                        Get directions
                      </button>
                    </div>
                  </div>
                  
                  <!-- Date and time -->
                  <div class="flex items-center">
                    <Calendar class="w-5 h-5 text-gray-400 mr-3" />
                    <div>
                      <p class="font-medium text-gray-900">{{ formatFullDate(event?.date) }}</p>
                      <p class="text-sm text-gray-600">{{ event?.time }}</p>
                    </div>
                  </div>
                  
                  <!-- External link -->
                  <div v-if="event?.external_url" class="flex items-center">
                    <ExternalLink class="w-5 h-5 text-gray-400 mr-3" />
                    <a
                      :href="event.external_url"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="font-medium text-blue-600 hover:text-blue-700 transition-colors"
                    >
                      View on external site
                    </a>
                  </div>
                  
                  <!-- Source -->
                  <div class="flex items-center">
                    <component 
                      :is="getSourceIcon(event?.source)"
                      class="w-5 h-5 text-gray-400 mr-3"
                    />
                    <span class="text-gray-700">
                      Source: {{ getSourceLabel(event?.source) }}
                    </span>
                  </div>
                </div>
                
                <!-- Tags -->
                <div 
                  v-if="event?.tags && event.tags.length > 0"
                  class="mb-6"
                >
                  <h3 class="text-lg font-semibold text-gray-900 mb-3">Tags</h3>
                  <div class="flex flex-wrap gap-2">
                    <span
                      v-for="tag in event.tags"
                      :key="tag.id"
                      class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-700"
                    >
                      {{ tag.name }}
                    </span>
                  </div>
                </div>
                
                <!-- Action buttons -->
                <div class="flex flex-col sm:flex-row gap-3 mb-6">
                  <button
                    @click="shareEvent"
                    class="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center justify-center"
                  >
                    <Share2 class="w-5 h-5 mr-2" />
                    Share Event
                  </button>
                  
                  <button
                    @click="navigateToLocation"
                    class="flex-1 bg-gray-100 text-gray-700 px-6 py-3 rounded-lg font-medium hover:bg-gray-200 transition-colors flex items-center justify-center"
                  >
                    <Navigation class="w-5 h-5 mr-2" />
                    Get Directions
                  </button>
                </div>
                
                <!-- Reviews section -->
                <div class="border-t pt-6">
                  <div class="flex items-center justify-between mb-4">
                    <h3 class="text-lg font-semibold text-gray-900">Reviews</h3>
                    <button
                      v-if="canAddReview"
                      @click="showAddReview = !showAddReview"
                      class="text-sm text-blue-600 hover:text-blue-700 transition-colors font-medium"
                    >
                      {{ showAddReview ? 'Cancel' : 'Write Review' }}
                    </button>
                  </div>
                  
                  <!-- Add review form -->
                  <div v-if="showAddReview && canAddReview" class="mb-6">
                    <ReviewForm
                      :event-id="event?.id"
                      @review-added="handleReviewAdded"
                      @cancel="showAddReview = false"
                    />
                  </div>
                  
                  <!-- Reviews list -->
                  <div v-if="loading" class="text-center py-4">
                    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                  </div>
                  
                  <div v-else-if="reviews.length === 0" class="text-center py-8 text-gray-500">
                    <Star class="w-12 h-12 mx-auto mb-2 text-gray-300" />
                    <p>No reviews yet. Be the first to review this event!</p>
                  </div>
                  
                  <div v-else class="space-y-4">
                    <ReviewItem
                      v-for="review in reviews"
                      :key="review.id"
                      :review="review"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import {
  X,
  Star, 
  MapPin, 
  Calendar,
  ExternalLink,
  Share2,
  Navigation,
  AlertCircle,
  User,
  Globe,
  Shield
} from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { apiService } from '@/services/api'
import type { Event, Review } from '@/types'
import ReviewForm from './ReviewForm.vue'
import ReviewItem from './ReviewItem.vue'

interface Props {
  event: Event | null
  isOpen: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
}>()

// Stores
const authStore = useAuthStore()
const { user, isAuthenticated } = storeToRefs(authStore)

// State
const modalContent = ref<HTMLElement>()
const reviews = ref<Review[]>([])
const loading = ref(false)
const showAddReview = ref(false)

// Computed
const categoryColor = computed(() => {
  const colorMap: Record<string, string> = {
    'concerts': '#E91E63',
    'festivals': '#9C27B0',
    'dj events': '#3F51B5',
    'kids events': '#FF9800',
    'food & drink': '#4CAF50',
    'art & culture': '#F44336',
    'sports': '#2196F3',
    'nightlife': '#673AB7',
    'workshops': '#795548',
    'markets': '#607D8B'
  }
  
  const categoryName = props.event?.category?.name?.toLowerCase() || 'default'
  return colorMap[categoryName] || '#757575'
})

const categoryColorSecondary = computed(() => {
  const colorMap: Record<string, string> = {
    'concerts': '#C2185B',
    'festivals': '#7B1FA2',
    'dj events': '#303F9F',
    'kids events': '#F57C00',
    'food & drink': '#388E3C',
    'art & culture': '#D32F2F',
    'sports': '#1976D2',
    'nightlife': '#512DA8',
    'workshops': '#5D4037',
    'markets': '#455A64'
  }
  
  const categoryName = props.event?.category?.name?.toLowerCase() || 'default'
  return colorMap[categoryName] || '#616161'
})

const canAddReview = computed(() => {
  return isAuthenticated.value && props.event?.is_approved
})

// Methods
function handleBackdropClick(event: MouseEvent) {
  if (event.target === event.currentTarget) {
    emit('close')
  }
}

function handleEscapeKey(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    emit('close')
  }
}

function formatFullDate(dateString?: string): string {
  if (!dateString) return ''
  
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

function getCategoryIcon(categoryName?: string): string {
  const iconMap: Record<string, string> = {
    'concerts': '🎵',
    'festivals': '🎪',
    'dj events': '🎧',
    'kids events': '🎠',
    'food & drink': '🍽️',
    'art & culture': '🎨',
    'sports': '⚽',
    'nightlife': '🌙',
    'workshops': '🛠️',
    'markets': '🛒'
  }
  
  const category = categoryName?.toLowerCase() || 'default'
  return iconMap[category] || '📍'
}

function getSourceIcon(source?: string) {
  const iconMap = {
    'user_submission': User,
    'scraped': Globe,
    'admin': Shield
  }
  return iconMap[source as keyof typeof iconMap] || Globe
}

function getSourceLabel(source?: string): string {
  const labelMap = {
    'user_submission': 'User Submission',
    'scraped': 'Web Scraping',
    'admin': 'Official'
  }
  return labelMap[source as keyof typeof labelMap] || 'Unknown'
}

async function shareEvent() {
  if (!props.event) return
  
  const shareData = {
    title: props.event.title,
    text: `Check out this event: ${props.event.title}`,
    url: window.location.origin + `/events/${props.event.id}`
  }
  
  try {
    if (navigator.share) {
      await navigator.share(shareData)
    } else {
      // Fallback to clipboard
      await navigator.clipboard.writeText(shareData.url)
      // You might want to show a toast notification here
      console.log('Event link copied to clipboard!')
    }
  } catch (error) {
    console.error('Error sharing event:', error)
  }
}

function navigateToLocation() {
  if (!props.event) return
  
  const url = `https://www.google.com/maps/dir/?api=1&destination=${props.event.latitude},${props.event.longitude}`
  window.open(url, '_blank')
}

async function loadReviews() {
  if (!props.event?.id) return
  
  try {
    loading.value = true
    reviews.value = await apiService.getEventReviews(props.event.id)
  } catch (error) {
    console.error('Failed to load reviews:', error)
    reviews.value = []
  } finally {
    loading.value = false
  }
}

function handleReviewAdded(newReview: Review) {
  reviews.value.unshift(newReview)
  showAddReview.value = false
  
  // Update event average rating and review count if needed
  // This would typically be handled by a store action
}

// Watchers
watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    document.body.style.overflow = 'hidden'
    loadReviews()
  } else {
    document.body.style.overflow = ''
    showAddReview.value = false
  }
})

watch(() => props.event?.id, () => {
  if (props.isOpen && props.event?.id) {
    loadReviews()
  }
})

// Lifecycle
onMounted(() => {
  document.addEventListener('keydown', handleEscapeKey)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscapeKey)
  document.body.style.overflow = ''
})
</script>