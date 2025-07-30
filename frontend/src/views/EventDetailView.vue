<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Loading state -->
    <div v-if="loading" class="flex items-center justify-center min-h-screen">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p class="text-gray-600">Loading event details...</p>
      </div>
    </div>
    
    <!-- Error state -->
    <div v-else-if="error || !event" class="flex items-center justify-center min-h-screen">
      <div class="text-center p-4">
        <AlertCircle class="w-12 h-12 text-red-600 mx-auto mb-4" />
        <h1 class="text-2xl font-bold text-red-800 mb-2">Event Not Found</h1>
        <p class="text-red-600 mb-4">
          {{ error || 'The event you are looking for could not be found.' }}
        </p>
        <div class="flex flex-col sm:flex-row gap-3 justify-center">
          <router-link
            to="/events"
            class="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            Browse All Events
          </router-link>
          <router-link
            to="/map"
            class="bg-gray-100 text-gray-700 px-6 py-3 rounded-lg font-medium hover:bg-gray-200 transition-colors"
          >
            View Map
          </router-link>
        </div>
      </div>
    </div>
    
    <!-- Event content -->
    <div v-else>
      <!-- Header with back navigation -->
      <div class="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex items-center justify-between h-16">
            <div class="flex items-center">
              <button
                @click="goBack"
                class="mr-4 p-2 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <ArrowLeft class="w-5 h-5" />
              </button>
              <h1 class="text-lg font-semibold text-gray-900 truncate">
                {{ event.title }}
              </h1>
            </div>
            
            <div class="flex items-center gap-2">
              <!-- Share button -->
              <button
                @click="shareEvent"
                class="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                title="Share event"
              >
                <Share2 class="w-5 h-5" />
              </button>
              
              <!-- View on map button -->
              <router-link
                :to="`/map?event=${event.id}`"
                class="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
              >
                <Map class="w-4 h-4 mr-2 inline" />
                View on Map
              </router-link>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Event hero section -->
      <div 
        class="h-64 sm:h-80 bg-gradient-to-br relative"
        :style="{ background: `linear-gradient(135deg, ${categoryColor}, ${categoryColorSecondary})` }"
      >
        <!-- Category icon overlay -->
        <div class="absolute inset-0 flex items-center justify-center">
          <div class="text-9xl opacity-20">
            {{ getCategoryIcon(event.category?.name) }}
          </div>
        </div>
        
        <!-- Event status badges -->
        <div class="absolute top-6 left-6 flex flex-col gap-2">
          <span 
            class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium text-white"
            :style="{ backgroundColor: categoryColor }"
          >
            {{ event.category?.name || 'Event' }}
          </span>
          
          <span 
            v-if="event.age_restrictions"
            class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium text-white bg-red-500"
          >
            {{ event.age_restrictions }}
          </span>
          
          <span 
            v-if="!event.is_approved"
            class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium text-white bg-orange-500"
          >
            <AlertCircle class="w-4 h-4 mr-1" />
            Pending Approval
          </span>
        </div>
        
        <!-- Date and time -->
        <div class="absolute bottom-6 left-6 bg-white bg-opacity-95 rounded-lg px-6 py-4">
          <div class="text-sm font-medium text-gray-600">
            {{ formatFullDate(event.date) }}
          </div>
          <div class="text-3xl font-bold text-gray-900">
            {{ event.time }}
          </div>
        </div>
      </div>
      
      <!-- Main content -->
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- Main content -->
          <div class="lg:col-span-2">
            <!-- Event title and rating -->
            <div class="bg-white rounded-lg shadow-sm p-6 mb-6">
              <h1 class="text-3xl font-bold text-gray-900 mb-4">
                {{ event.title }}
              </h1>
              
              <div 
                v-if="event.average_rating || event.review_count"
                class="flex items-center gap-4 mb-4"
              >
                <div class="flex items-center">
                  <div class="flex items-center mr-2">
                    <Star 
                      v-for="star in 5"
                      :key="star"
                      class="w-6 h-6"
                      :class="[
                        star <= Math.round(event.average_rating || 0)
                          ? 'text-yellow-400 fill-current'
                          : 'text-gray-300'
                      ]"
                    />
                  </div>
                  <span class="text-xl font-medium text-gray-900">
                    {{ event.average_rating?.toFixed(1) || '0.0' }}
                  </span>
                </div>
                
                <span class="text-gray-600">
                  {{ event.review_count || 0 }} review{{ (event.review_count || 0) !== 1 ? 's' : '' }}
                </span>
              </div>
              
              <!-- Tags -->
              <div 
                v-if="event.tags && event.tags.length > 0"
                class="flex flex-wrap gap-2"
              >
                <span
                  v-for="tag in event.tags"
                  :key="tag.id"
                  class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-700"
                >
                  {{ tag.name }}
                </span>
              </div>
            </div>
            
            <!-- Event description -->
            <div v-if="event.description" class="bg-white rounded-lg shadow-sm p-6 mb-6">
              <h2 class="text-xl font-semibold text-gray-900 mb-4">About This Event</h2>
              <p class="text-gray-700 whitespace-pre-line leading-relaxed">
                {{ event.description }}
              </p>
            </div>
            
            <!-- Reviews section -->
            <div class="bg-white rounded-lg shadow-sm p-6">
              <div class="flex items-center justify-between mb-6">
                <h2 class="text-xl font-semibold text-gray-900">Reviews</h2>
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
                  :event-id="event.id"
                  @review-added="handleReviewAdded"
                  @cancel="showAddReview = false"
                />
              </div>
              
              <!-- Reviews list -->
              <div v-if="reviewsLoading" class="text-center py-4">
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
          
          <!-- Sidebar -->
          <div class="lg:col-span-1">
            <!-- Event details -->
            <div class="bg-white rounded-lg shadow-sm p-6 mb-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-4">Event Details</h3>
              
              <div class="space-y-4">
                <!-- Date and time -->
                <div class="flex items-start">
                  <Calendar class="w-5 h-5 text-gray-400 mt-1 mr-3" />
                  <div>
                    <p class="font-medium text-gray-900">{{ formatFullDate(event.date) }}</p>
                    <p class="text-sm text-gray-600">{{ event.time }}</p>
                  </div>
                </div>
                
                <!-- Location -->
                <div class="flex items-start">
                  <MapPin class="w-5 h-5 text-gray-400 mt-1 mr-3" />
                  <div>
                    <p class="font-medium text-gray-900">{{ event.location }}</p>
                    <button
                      @click="navigateToLocation"
                      class="text-sm text-blue-600 hover:text-blue-700 transition-colors"
                    >
                      Get directions
                    </button>
                  </div>
                </div>
                
                <!-- External link -->
                <div v-if="event.external_url" class="flex items-start">
                  <ExternalLink class="w-5 h-5 text-gray-400 mt-1 mr-3" />
                  <div>
                    <a
                      :href="event.external_url"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="font-medium text-blue-600 hover:text-blue-700 transition-colors"
                    >
                      View on external site
                    </a>
                  </div>
                </div>
                
                <!-- Source -->
                <div class="flex items-start">
                  <component 
                    :is="getSourceIcon(event.source)"
                    class="w-5 h-5 text-gray-400 mt-1 mr-3"
                  />
                  <div>
                    <p class="text-gray-700">
                      Source: {{ getSourceLabel(event.source) }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Action buttons -->
            <div class="bg-white rounded-lg shadow-sm p-6">
              <div class="space-y-3">
                <button
                  @click="shareEvent"
                  class="w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center justify-center"
                >
                  <Share2 class="w-5 h-5 mr-2" />
                  Share Event
                </button>
                
                <button
                  @click="navigateToLocation"
                  class="w-full bg-gray-100 text-gray-700 px-6 py-3 rounded-lg font-medium hover:bg-gray-200 transition-colors flex items-center justify-center"
                >
                  <Navigation class="w-5 h-5 mr-2" />
                  Get Directions
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import {
  ArrowLeft,
  Share2,
  Map,
  AlertCircle,
  Star,
  Calendar,
  MapPin,
  ExternalLink,
  Navigation,
  User,
  Globe,
  Shield
} from 'lucide-vue-next'
import { useEventsStore } from '@/stores/events'
import { useAuthStore } from '@/stores/auth'
import { apiService } from '@/services/api'
import ReviewForm from '@/components/event/ReviewForm.vue'
import ReviewItem from '@/components/event/ReviewItem.vue'
import type { Event, Review } from '@/types'

interface Props {
  id: string
}

const props = defineProps<Props>()

// Router
const route = useRoute()
const router = useRouter()

// Stores
const eventsStore = useEventsStore()
const authStore = useAuthStore()
const { loading } = storeToRefs(eventsStore)
const { isAuthenticated } = storeToRefs(authStore)

// State
const event = ref<Event | null>(null)
const error = ref<string | null>(null)
const reviews = ref<Review[]>([])
const reviewsLoading = ref(false)
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
  
  const categoryName = event.value?.category?.name?.toLowerCase() || 'default'
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
  
  const categoryName = event.value?.category?.name?.toLowerCase() || 'default'
  return colorMap[categoryName] || '#616161'
})

const canAddReview = computed(() => {
  return isAuthenticated.value && event.value?.is_approved
})

// Methods
async function loadEvent() {
  try {
    const eventId = parseInt(props.id, 10)
    if (isNaN(eventId)) {
      error.value = 'Invalid event ID'
      return
    }
    
    event.value = await eventsStore.fetchEvent(eventId)
    await loadReviews()
  } catch (err: any) {
    error.value = err.message || 'Failed to load event'
  }
}

async function loadReviews() {
  if (!event.value?.id) return
  
  try {
    reviewsLoading.value = true
    reviews.value = await apiService.getEventReviews(event.value.id)
  } catch (error) {
    console.error('Failed to load reviews:', error)
    reviews.value = []
  } finally {
    reviewsLoading.value = false
  }
}

function handleReviewAdded(newReview: Review) {
  reviews.value.unshift(newReview)
  showAddReview.value = false
  
  // Update event rating if needed
  if (event.value) {
    // This would typically be handled by refreshing the event data
  }
}

function goBack() {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    router.push('/events')
  }
}

async function shareEvent() {
  if (!event.value) return
  
  const shareData = {
    title: event.value.title,
    text: `Check out this event: ${event.value.title}`,
    url: window.location.href
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
  if (!event.value) return
  
  const url = `https://www.google.com/maps/dir/?api=1&destination=${event.value.latitude},${event.value.longitude}`
  window.open(url, '_blank')
}

function formatFullDate(dateString: string): string {
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

function getSourceIcon(source: string) {
  const iconMap = {
    'user_submission': User,
    'scraped': Globe,
    'admin': Shield
  }
  return iconMap[source as keyof typeof iconMap] || Globe
}

function getSourceLabel(source: string): string {
  const labelMap = {
    'user_submission': 'User Submission',
    'scraped': 'Web Scraping',
    'admin': 'Official'
  }
  return labelMap[source as keyof typeof labelMap] || 'Unknown'
}

// Lifecycle
onMounted(() => {
  loadEvent()
})
</script>