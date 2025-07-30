<template>
  <div class="relative">
    <!-- Main search input -->
    <div class="relative">
      <Search class="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
      <input
        ref="searchInput"
        v-model="searchQuery"
        type="text"
        :placeholder="placeholder"
        class="w-full pl-12 pr-20 py-3 bg-white border border-gray-300 rounded-lg text-base focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm"
        @input="handleSearch"
        @focus="showSuggestions = true"
        @keydown="handleKeydown"
      />
      
      <!-- Quick action buttons -->
      <div class="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center gap-1">
        <!-- Location button -->
        <button
          @click="searchNearMe"
          :disabled="loadingLocation"
          class="p-2 text-gray-400 hover:text-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          title="Search near me"
        >
          <div v-if="loadingLocation" class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
          <MapPin v-else class="w-4 h-4" />
        </button>
        
        <!-- Clear button -->
        <button
          v-if="searchQuery"
          @click="clearSearch"
          class="p-2 text-gray-400 hover:text-gray-600 transition-colors"
          title="Clear search"
        >
          <X class="w-4 h-4" />
        </button>
      </div>
    </div>
    
    <!-- Search suggestions dropdown -->
    <div
      v-if="showSuggestions && (searchSuggestions.length > 0 || locationSuggestions.length > 0)"
      class="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-10 max-h-96 overflow-y-auto"
    >
      <!-- Recent searches -->
      <div v-if="recentSearches.length > 0 && !searchQuery" class="p-2">
        <div class="px-2 py-1 text-xs font-medium text-gray-500 uppercase tracking-wider">
          Recent Searches
        </div>
        <button
          v-for="(search, index) in recentSearches"
          :key="`recent-${index}`"
          @click="selectSearch(search)"
          class="w-full text-left px-2 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded flex items-center"
        >
          <Clock class="w-4 h-4 mr-2 text-gray-400" />
          {{ search }}
        </button>
        <div class="border-t border-gray-100 my-2"></div>
      </div>
      
      <!-- Event suggestions -->
      <div v-if="searchSuggestions.length > 0" class="p-2">
        <div class="px-2 py-1 text-xs font-medium text-gray-500 uppercase tracking-wider">
          Events
        </div>
        <button
          v-for="(event, index) in searchSuggestions"
          :key="`event-${event.id}`"
          @click="selectEvent(event)"
          :class="[
            'w-full text-left px-2 py-2 text-sm rounded flex items-start hover:bg-gray-50',
            highlightedIndex === index ? 'bg-blue-50' : ''
          ]"
        >
          <div 
            class="w-2 h-2 rounded-full mr-3 mt-2 flex-shrink-0"
            :style="{ backgroundColor: getCategoryColor(event.category?.name) }"
          ></div>
          <div class="min-w-0 flex-1">
            <div class="font-medium text-gray-900 truncate">{{ event.title }}</div>
            <div class="text-gray-500 text-xs flex items-center mt-1">
              <Calendar class="w-3 h-3 mr-1" />
              {{ formatEventDate(event.date) }}
              <span class="mx-1">•</span>
              <MapPin class="w-3 h-3 mr-1" />
              <span class="truncate">{{ event.location }}</span>
            </div>
          </div>
        </button>
      </div>
      
      <!-- Location suggestions -->
      <div v-if="locationSuggestions.length > 0" class="p-2">
        <div v-if="searchSuggestions.length > 0" class="border-t border-gray-100 my-2"></div>
        <div class="px-2 py-1 text-xs font-medium text-gray-500 uppercase tracking-wider">
          Locations
        </div>
        <button
          v-for="location in locationSuggestions"
          :key="`location-${location.place_id}`"
          @click="selectLocation(location)"
          class="w-full text-left px-2 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded flex items-center"
        >
          <MapPin class="w-4 h-4 mr-2 text-gray-400" />
          <div>
            <div class="font-medium">{{ location.structured_formatting.main_text }}</div>
            <div class="text-xs text-gray-500">{{ location.structured_formatting.secondary_text }}</div>
          </div>
        </button>
      </div>
      
      <!-- No results -->
      <div v-if="searchQuery && searchSuggestions.length === 0 && locationSuggestions.length === 0" class="p-4 text-center text-gray-500">
        <SearchX class="w-8 h-8 mx-auto mb-2 text-gray-300" />
        <p class="text-sm">No results found for "{{ searchQuery }}"</p>
      </div>
    </div>
    
    <!-- Loading overlay -->
    <div v-if="loading" class="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg p-4 text-center">
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto mb-2"></div>
      <p class="text-sm text-gray-600">Searching...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { 
  Search, 
  MapPin, 
  X, 
  Clock,
  Calendar,
  SearchX
} from 'lucide-vue-next'
import { useEventsStore } from '@/stores/events'
import { useMapStore } from '@/stores/map'
import { googleMapsService } from '@/services/googleMaps'
import { useDebounceFn } from '@vueuse/core'
import type { Event } from '@/types'

interface Props {
  placeholder?: string
  maxSuggestions?: number
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Search events, locations, or categories...',
  maxSuggestions: 5
})

const emit = defineEmits<{
  search: [query: string]
  eventSelected: [event: Event]
  locationSelected: [location: google.maps.places.AutocompletePrediction]
  nearMeSearch: [location: { lat: number; lng: number }]
}>()

// Stores
const eventsStore = useEventsStore()
const mapStore = useMapStore()
const { eventsWithCategories } = storeToRefs(eventsStore)
const { userLocation } = storeToRefs(mapStore)

// State
const searchInput = ref<HTMLInputElement>()
const searchQuery = ref('')
const showSuggestions = ref(false)
const loading = ref(false)
const loadingLocation = ref(false)
const highlightedIndex = ref(-1)

// Suggestions
const searchSuggestions = ref<Event[]>([])
const locationSuggestions = ref<google.maps.places.AutocompletePrediction[]>([])
const recentSearches = ref<string[]>([])

// Google Places service
let placesService: google.maps.places.AutocompleteService | null = null

// Computed
const allSuggestions = computed(() => [
  ...searchSuggestions.value,
  ...locationSuggestions.value
])

// Debounced search function
const debouncedSearch = useDebounceFn(async (query: string) => {
  if (!query.trim()) {
    searchSuggestions.value = []
    locationSuggestions.value = []
    loading.value = false
    return
  }
  
  loading.value = true
  
  try {
    // Search events
    await searchEvents(query)
    
    // Search locations
    await searchLocations(query)
  } catch (error) {
    console.error('Search error:', error)
  } finally {
    loading.value = false
  }
}, 300)

// Methods
async function initializePlacesService() {
  try {
    await googleMapsService.initialize()
    placesService = new google.maps.places.AutocompleteService()
  } catch (error) {
    console.error('Failed to initialize Places service:', error)
  }
}

function handleSearch() {
  highlightedIndex.value = -1
  debouncedSearch(searchQuery.value)
}

async function searchEvents(query: string) {
  const lowerQuery = query.toLowerCase()
  
  // Filter events based on title, description, location, and category
  const filteredEvents = eventsWithCategories.value.filter(event => {
    return (
      event.title.toLowerCase().includes(lowerQuery) ||
      event.description?.toLowerCase().includes(lowerQuery) ||
      event.location.toLowerCase().includes(lowerQuery) ||
      event.category?.name.toLowerCase().includes(lowerQuery)
    )
  }).slice(0, props.maxSuggestions)
  
  searchSuggestions.value = filteredEvents
}

async function searchLocations(query: string) {
  if (!placesService) {
    locationSuggestions.value = []
    return
  }
  
  return new Promise<void>((resolve) => {
    placesService!.getPlacePredictions(
      {
        input: query,
        componentRestrictions: { country: 'sg' }, // Restrict to Singapore
        types: ['establishment', 'geocode']
      },
      (predictions, status) => {
        if (status === google.maps.places.PlacesServiceStatus.OK && predictions) {
          locationSuggestions.value = predictions.slice(0, props.maxSuggestions)
        } else {
          locationSuggestions.value = []
        }
        resolve()
      }
    )
  })
}

function selectSearch(query: string) {
  searchQuery.value = query
  showSuggestions.value = false
  addToRecentSearches(query)
  emit('search', query)
}

function selectEvent(event: Event) {
  searchQuery.value = event.title
  showSuggestions.value = false
  addToRecentSearches(event.title)
  emit('eventSelected', event)
}

function selectLocation(location: google.maps.places.AutocompletePrediction) {
  searchQuery.value = location.description
  showSuggestions.value = false
  addToRecentSearches(location.description)
  emit('locationSelected', location)
}

async function searchNearMe() {
  if (userLocation.value) {
    emit('nearMeSearch', userLocation.value)
    return
  }
  
  try {
    loadingLocation.value = true
    const position = await googleMapsService.getCurrentLocation()
    const location = {
      lat: position.coords.latitude,
      lng: position.coords.longitude
    }
    
    mapStore.setUserLocation(location)
    emit('nearMeSearch', location)
  } catch (error) {
    console.error('Failed to get current location:', error)
    // You might want to show an error toast here
  } finally {
    loadingLocation.value = false
  }
}

function clearSearch() {
  searchQuery.value = ''
  searchSuggestions.value = []
  locationSuggestions.value = []
  showSuggestions.value = false
  highlightedIndex.value = -1
  emit('search', '')
}

function handleKeydown(event: KeyboardEvent) {
  const suggestions = allSuggestions.value
  
  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault()
      highlightedIndex.value = Math.min(highlightedIndex.value + 1, suggestions.length - 1)
      break
    case 'ArrowUp':
      event.preventDefault()
      highlightedIndex.value = Math.max(highlightedIndex.value - 1, -1)
      break
    case 'Enter':
      event.preventDefault()
      if (highlightedIndex.value >= 0) {
        const suggestion = suggestions[highlightedIndex.value]
        if ('title' in suggestion) {
          selectEvent(suggestion as Event)
        } else {
          selectLocation(suggestion as google.maps.places.AutocompletePrediction)
        }
      } else if (searchQuery.value.trim()) {
        showSuggestions.value = false
        addToRecentSearches(searchQuery.value)
        emit('search', searchQuery.value)
      }
      break
    case 'Escape':
      showSuggestions.value = false
      highlightedIndex.value = -1
      searchInput.value?.blur()
      break
  }
}

function addToRecentSearches(query: string) {
  const trimmedQuery = query.trim()
  if (!trimmedQuery) return
  
  // Remove if already exists
  const index = recentSearches.value.indexOf(trimmedQuery)
  if (index > -1) {
    recentSearches.value.splice(index, 1)
  }
  
  // Add to beginning
  recentSearches.value.unshift(trimmedQuery)
  
  // Keep only last 5
  recentSearches.value = recentSearches.value.slice(0, 5)
  
  // Save to localStorage
  localStorage.setItem('todayatsg_recent_searches', JSON.stringify(recentSearches.value))
}

function loadRecentSearches() {
  try {
    const saved = localStorage.getItem('todayatsg_recent_searches')
    if (saved) {
      recentSearches.value = JSON.parse(saved)
    }
  } catch (error) {
    console.error('Failed to load recent searches:', error)
  }
}

function getCategoryColor(categoryName?: string): string {
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
  
  const category = categoryName?.toLowerCase() || 'default'
  return colorMap[category] || '#757575'
}

function formatEventDate(dateString: string): string {
  const date = new Date(dateString)
  const today = new Date()
  const tomorrow = new Date(today)
  tomorrow.setDate(tomorrow.getDate() + 1)
  
  if (date.toDateString() === today.toDateString()) {
    return 'Today'
  } else if (date.toDateString() === tomorrow.toDateString()) {
    return 'Tomorrow'
  } else {
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric' 
    })
  }
}

function handleClickOutside(event: MouseEvent) {
  if (searchInput.value && !searchInput.value.contains(event.target as Node)) {
    showSuggestions.value = false
    highlightedIndex.value = -1
  }
}

// Lifecycle
onMounted(async () => {
  await initializePlacesService()
  loadRecentSearches()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>