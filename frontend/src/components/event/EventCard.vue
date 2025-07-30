<template>
  <div
    class="bg-white rounded-lg shadow-md hover:shadow-lg transition-all duration-300 cursor-pointer overflow-hidden group"
    :class="{ 'ring-2 ring-blue-500': isSelected, 'shadow-lg': isHovered }"
    @click="$emit('click', event)"
    @mouseenter="$emit('hover', event)"
    @mouseleave="$emit('hover', null)"
  >
    <!-- Event image placeholder / category indicator -->
    <div 
      class="h-48 sm:h-40 md:h-48 bg-gradient-to-br from-blue-500 to-purple-600 relative overflow-hidden"
      :style="{ background: `linear-gradient(135deg, ${categoryColor}, ${categoryColorSecondary})` }"
    >
      <!-- Event source badge -->
      <div class="absolute top-2 left-2">
        <span 
          class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium text-white bg-black bg-opacity-30"
        >
          <component 
            :is="getSourceIcon(event.source)"
            class="w-3 h-3 mr-1"
          />
          {{ getSourceLabel(event.source) }}
        </span>
      </div>
      
      <!-- Age restriction badge -->
      <div 
        v-if="event.age_restrictions"
        class="absolute top-2 right-2"
      >
        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium text-white bg-red-500 bg-opacity-90">
          {{ event.age_restrictions }}
        </span>
      </div>
      
      <!-- Category icon overlay -->
      <div class="absolute inset-0 flex items-center justify-center">
        <div class="text-6xl opacity-20">
          {{ getCategoryIcon(event.category?.name) }}
        </div>
      </div>
      
      <!-- Date overlay -->
      <div class="absolute bottom-2 left-2 bg-white bg-opacity-90 rounded-lg px-3 py-2">
        <div class="text-xs font-medium text-gray-900">
          {{ formatMonth(event.date) }}
        </div>
        <div class="text-lg font-bold text-gray-900 leading-none">
          {{ formatDay(event.date) }}
        </div>
      </div>
    </div>
    
    <!-- Event content -->
    <div class="p-4">
      <!-- Category and time -->
      <div class="flex items-center justify-between mb-2">
        <span 
          class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium text-white"
          :style="{ backgroundColor: categoryColor }"
        >
          {{ event.category?.name || 'Event' }}
        </span>
        <div class="flex items-center text-xs text-gray-500">
          <Clock class="w-3 h-3 mr-1" />
          {{ event.time }}
        </div>
      </div>
      
      <!-- Event title -->
      <h3 class="font-semibold text-lg text-gray-900 mb-2 line-clamp-2 group-hover:text-blue-600 transition-colors">
        {{ event.title }}
      </h3>
      
      <!-- Event description -->
      <p 
        v-if="event.description"
        class="text-sm text-gray-600 mb-3 line-clamp-2"
      >
        {{ event.description }}
      </p>
      
      <!-- Location -->
      <div class="flex items-center text-sm text-gray-600 mb-3">
        <MapPin class="w-4 h-4 mr-2 flex-shrink-0" />
        <span class="truncate">{{ event.location }}</span>
        <span 
          v-if="distance !== null"
          class="ml-auto text-xs text-gray-500 flex-shrink-0"
        >
          {{ distance.toFixed(1) }}km away
        </span>
      </div>
      
      <!-- Rating and reviews -->
      <div 
        v-if="event.average_rating || event.review_count"
        class="flex items-center justify-between mb-3"
      >
        <div class="flex items-center">
          <div class="flex items-center">
            <Star 
              v-for="star in 5"
              :key="star"
              class="w-4 h-4"
              :class="[
                star <= Math.round(event.average_rating || 0)
                  ? 'text-yellow-400 fill-current'
                  : 'text-gray-300'
              ]"
            />
          </div>
          <span class="ml-2 text-sm text-gray-600">
            {{ event.average_rating?.toFixed(1) || '0.0' }}
          </span>
        </div>
        
        <span class="text-xs text-gray-500">
          {{ event.review_count || 0 }} review{{ (event.review_count || 0) !== 1 ? 's' : '' }}
        </span>
      </div>
      
      <!-- Tags -->
      <div 
        v-if="event.tags && event.tags.length > 0"
        class="flex flex-wrap gap-1 mb-3"
      >
        <span
          v-for="tag in event.tags.slice(0, 3)"
          :key="tag.id"
          class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700"
        >
          {{ tag.name }}
        </span>
        <span
          v-if="event.tags.length > 3"
          class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700"
        >
          +{{ event.tags.length - 3 }} more
        </span>
      </div>
      
      <!-- Action buttons -->
      <div class="flex items-center justify-between pt-2 border-t border-gray-100">
        <button
          @click.stop="$emit('viewDetails', event)"
          class="text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors"
        >
          View Details
        </button>
        
        <div class="flex items-center gap-2">
          <!-- Share button -->
          <button
            @click.stop="shareEvent"
            class="p-2 text-gray-400 hover:text-gray-600 transition-colors"
            title="Share event"
          >
            <Share2 class="w-4 h-4" />
          </button>
          
          <!-- External link -->
          <a
            v-if="event.external_url"
            :href="event.external_url"
            target="_blank"
            rel="noopener noreferrer"
            @click.stop
            class="p-2 text-gray-400 hover:text-gray-600 transition-colors"
            title="View on external site"
          >
            <ExternalLink class="w-4 h-4" />
          </a>
          
          <!-- Navigate to location -->
          <button
            @click.stop="navigateToLocation"
            class="p-2 text-gray-400 hover:text-gray-600 transition-colors"
            title="Get directions"
          >
            <Navigation class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
    
    <!-- Approval status indicator -->
    <div 
      v-if="!event.is_approved"
      class="absolute top-2 left-1/2 transform -translate-x-1/2"
    >
      <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium text-white bg-orange-500 bg-opacity-90">
        <AlertCircle class="w-3 h-3 mr-1" />
        Pending Approval
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { 
  Clock, 
  MapPin, 
  Star, 
  Share2, 
  ExternalLink,
  Navigation,
  AlertCircle,
  User,
  Globe,
  Shield
} from 'lucide-vue-next'
import type { Event } from '@/types'

interface Props {
  event: Event
  isSelected?: boolean
  isHovered?: boolean
  userLocation?: { lat: number; lng: number } | null
}

const props = withDefaults(defineProps<Props>(), {
  isSelected: false,
  isHovered: false,
  userLocation: null
})

const emit = defineEmits<{
  click: [event: Event]
  hover: [event: Event | null]
  viewDetails: [event: Event]
}>()

// Computed properties
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
  
  const categoryName = props.event.category?.name?.toLowerCase() || 'default'
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
  
  const categoryName = props.event.category?.name?.toLowerCase() || 'default'
  return colorMap[categoryName] || '#616161'
})

const distance = computed(() => {
  if (!props.userLocation) return null
  
  const R = 6371 // Earth's radius in kilometers
  const dLat = toRadians(props.event.latitude - props.userLocation.lat)
  const dLng = toRadians(props.event.longitude - props.userLocation.lng)
  
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(toRadians(props.userLocation.lat)) * 
            Math.cos(toRadians(props.event.latitude)) *
            Math.sin(dLng / 2) * Math.sin(dLng / 2)
            
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return R * c
})

// Helper functions
function toRadians(degrees: number): number {
  return degrees * (Math.PI / 180)
}

function formatMonth(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { month: 'short' })
}

function formatDay(dateString: string): string {
  const date = new Date(dateString)
  return date.getDate().toString()
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
    'user_submission': 'User',
    'scraped': 'Web',
    'admin': 'Official'
  }
  return labelMap[source as keyof typeof labelMap] || 'Event'
}

async function shareEvent() {
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
  const url = `https://www.google.com/maps/dir/?api=1&destination=${props.event.latitude},${props.event.longitude}`
  window.open(url, '_blank')
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>