<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Top navigation bar -->
    <div class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="px-4 py-3 flex items-center gap-4">
        <!-- Mobile menu button -->
        <button
          @click="showMobileFilters = !showMobileFilters"
          class="lg:hidden p-2 text-gray-600 hover:text-gray-900 transition-colors"
        >
          <Menu class="w-5 h-5" />
        </button>
        
        <!-- Search bar -->
        <div class="flex-1 max-w-2xl">
          <EventSearch
            placeholder="Search events and locations in Singapore..."
            @search="handleSearch"
            @event-selected="handleEventSelected"
            @location-selected="handleLocationSelected"
            @near-me-search="handleNearMeSearch"
          />
        </div>
        
        <!-- View toggle -->
        <div class="hidden sm:flex items-center bg-gray-100 rounded-lg p-1">
          <router-link
            to="/map"
            class="px-3 py-2 text-sm font-medium rounded-md transition-colors"
            :class="[
              $route.name === 'map' 
                ? 'bg-white text-gray-900 shadow-sm' 
                : 'text-gray-600 hover:text-gray-900'
            ]"
          >
            <Map class="w-4 h-4 mr-2 inline" />
            Map
          </router-link>
          <router-link
            to="/events"
            class="px-3 py-2 text-sm font-medium rounded-md transition-colors"
            :class="[
              $route.name === 'events' 
                ? 'bg-white text-gray-900 shadow-sm' 
                : 'text-gray-600 hover:text-gray-900'
            ]"
          >
            <List class="w-4 h-4 mr-2 inline" />
            List
          </router-link>
        </div>
        
        <!-- Sort dropdown -->
        <div class="relative">
          <select
            v-model="sortBy"
            class="bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            @change="handleSortChange"
          >
            <option value="date">Sort by Date</option>
            <option value="rating">Sort by Rating</option>
            <option value="distance">Sort by Distance</option>
            <option value="title">Sort by Title</option>
          </select>
        </div>
      </div>
    </div>
    
    <!-- Main content area -->
    <div class="flex">
      <!-- Sidebar with filters (desktop) -->
      <div 
        class="hidden lg:block w-80 bg-white border-r border-gray-200 sticky top-16 h-[calc(100vh-4rem)] overflow-y-auto"
        :class="showDesktopFilters ? 'block' : 'hidden'"
      >
        <div class="p-6">
          <EventFilters
            @filters-changed="handleFiltersChanged"
          />
        </div>
      </div>
      
      <!-- Mobile filters overlay -->
      <div
        v-if="showMobileFilters"
        class="fixed inset-0 z-50 lg:hidden"
      >
        <!-- Backdrop -->
        <div 
          class="absolute inset-0 bg-black bg-opacity-50"
          @click="showMobileFilters = false"
        ></div>
        
        <!-- Filters panel -->
        <div class="absolute left-0 top-0 bottom-0 w-80 bg-white overflow-y-auto">
          <div class="p-4">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-semibold text-gray-900">Filters</h2>
              <button
                @click="showMobileFilters = false"
                class="p-2 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X class="w-5 h-5" />
              </button>
            </div>
            
            <EventFilters
              @filters-changed="handleFiltersChanged"
              @apply="showMobileFilters = false"
            />
          </div>
        </div>
      </div>
      
      <!-- Events list -->
      <div class="flex-1 p-4 lg:p-6">
        <!-- Results header -->
        <div class="flex items-center justify-between mb-6">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">
              Events in Singapore
            </h1>
            <p class="text-gray-600 mt-1">
              {{ filteredAndSortedEvents.length }} event{{ filteredAndSortedEvents.length !== 1 ? 's' : '' }} found
              <span v-if="hasActiveFilters" class="text-blue-600">with current filters</span>
            </p>
          </div>
          
          <!-- View options -->
          <div class="hidden lg:flex items-center gap-2">
            <button
              @click="showDesktopFilters = !showDesktopFilters"
              class="flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Filter class="w-4 h-4 mr-2" />
              {{ showDesktopFilters ? 'Hide' : 'Show' }} Filters
            </button>
            
            <div class="flex items-center bg-gray-100 rounded-lg p-1">
              <button
                @click="viewMode = 'grid'"
                class="px-3 py-2 text-sm font-medium rounded-md transition-colors"
                :class="[
                  viewMode === 'grid' 
                    ? 'bg-white text-gray-900 shadow-sm' 
                    : 'text-gray-600 hover:text-gray-900'
                ]"
              >
                <Grid3X3 class="w-4 h-4" />
              </button>
              <button
                @click="viewMode = 'list'"
                class="px-3 py-2 text-sm font-medium rounded-md transition-colors"
                :class="[
                  viewMode === 'list' 
                    ? 'bg-white text-gray-900 shadow-sm' 
                    : 'text-gray-600 hover:text-gray-900'
                ]"
              >
                <List class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
        
        <!-- Loading state -->
        <div v-if="loading" class="text-center py-12">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p class="text-gray-600">Loading events...</p>
        </div>
        
        <!-- Error state -->
        <div v-else-if="error" class="text-center py-12">
          <AlertCircle class="w-12 h-12 text-red-600 mx-auto mb-4" />
          <h3 class="text-lg font-semibold text-red-800 mb-2">Error Loading Events</h3>
          <p class="text-red-600 mb-4">{{ error }}</p>
          <button
            @click="loadEvents"
            class="bg-red-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-red-700 transition-colors"
          >
            Try Again
          </button>
        </div>
        
        <!-- Empty state -->
        <div v-else-if="filteredAndSortedEvents.length === 0" class="text-center py-12">
          <SearchX class="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 class="text-lg font-semibold text-gray-900 mb-2">No events found</h3>
          <p class="text-gray-600 mb-4">
            Try adjusting your filters or search terms to find more events.
          </p>
          <button
            @click="clearAllFilters"
            class="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            Clear All Filters
          </button>
        </div>
        
        <!-- Events grid/list -->
        <div
          v-else
          :class="[
            viewMode === 'grid' 
              ? 'grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6' 
              : 'space-y-4'
          ]"
        >
          <EventCard
            v-for="event in filteredAndSortedEvents"
            :key="event.id"
            :event="event"
            :is-selected="selectedEventId === event.id"
            :is-hovered="hoveredEventId === event.id"
            :user-location="userLocation"
            @click="handleEventClick"
            @hover="handleEventHover"
            @view-details="handleEventViewDetails"
            :class="viewMode === 'list' ? 'max-w-none' : ''"
          />
        </div>
        
        <!-- Load more button (if pagination is implemented) -->
        <div 
          v-if="canLoadMore"
          class="text-center mt-8"
        >
          <button
            @click="loadMoreEvents"
            :disabled="loadingMore"
            class="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="loadingMore" class="flex items-center">
              <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Loading...
            </span>
            <span v-else>Load More Events</span>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Event modal -->
    <EventModal
      :event="selectedEvent"
      :is-open="showEventModal"
      @close="handleEventModalClose"
    />
    
    <!-- Floating action button (mobile) -->
    <div class="fixed bottom-6 right-6 sm:hidden">
      <router-link
        to="/map"
        class="w-14 h-14 bg-blue-600 text-white rounded-full shadow-lg flex items-center justify-center hover:bg-blue-700 transition-colors"
      >
        <Map class="w-6 h-6" />
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import {
  Menu,
  X,
  Map,
  List,
  Filter,
  Grid3X3,
  AlertCircle,
  SearchX
} from 'lucide-vue-next'
import { useEventsStore } from '@/stores/events'
import { useMapStore } from '@/stores/map'
import { useGeolocation } from '@/composables/useGeolocation'
import EventCard from '@/components/event/EventCard.vue'
import EventSearch from '@/components/event/EventSearch.vue'
import EventFilters from '@/components/event/EventFilters.vue'
import EventModal from '@/components/event/EventModal.vue'
import type { Event, EventFilters as EventFiltersType } from '@/types'

// Router
const route = useRoute()
const router = useRouter()

// Stores
const eventsStore = useEventsStore()
const mapStore = useMapStore()

const {
  eventsWithCategories,
  loading,
  error,
  pagination
} = storeToRefs(eventsStore)

const { userLocation } = storeToRefs(mapStore)

// Geolocation
const { position: geoPosition } = useGeolocation({ immediate: true })

// State
const showMobileFilters = ref(false)
const showDesktopFilters = ref(true)
const showEventModal = ref(false)
const selectedEventId = ref<number | null>(null)
const hoveredEventId = ref<number | null>(null)
const currentFilters = ref<EventFiltersType>({})
const sortBy = ref<'date' | 'rating' | 'distance' | 'title'>('date')
const viewMode = ref<'grid' | 'list'>('grid')
const loadingMore = ref(false)

// Computed
const filteredEvents = computed(() => {
  let events = eventsWithCategories.value
  
  // Apply search filter
  if (currentFilters.value.search) {
    const searchTerm = currentFilters.value.search.toLowerCase()
    events = events.filter(event =>
      event.title.toLowerCase().includes(searchTerm) ||
      event.description?.toLowerCase().includes(searchTerm) ||
      event.location.toLowerCase().includes(searchTerm) ||
      event.category?.name.toLowerCase().includes(searchTerm)
    )
  }
  
  // Apply category filter
  if (currentFilters.value.category_ids?.length) {
    events = events.filter(event =>
      currentFilters.value.category_ids!.includes(event.category_id)
    )
  }
  
  // Apply tag filter
  if (currentFilters.value.tag_ids?.length) {
    events = events.filter(event =>
      event.tags?.some(tag => currentFilters.value.tag_ids!.includes(tag.id))
    )
  }
  
  // Apply date filter
  if (currentFilters.value.date_from || currentFilters.value.date_to) {
    events = events.filter(event => {
      const eventDate = new Date(event.date)
      const fromDate = currentFilters.value.date_from ? new Date(currentFilters.value.date_from) : null
      const toDate = currentFilters.value.date_to ? new Date(currentFilters.value.date_to) : null
      
      if (fromDate && eventDate < fromDate) return false
      if (toDate && eventDate > toDate) return false
      
      return true
    })
  }
  
  // Apply location/radius filter
  if (currentFilters.value.latitude && currentFilters.value.longitude && currentFilters.value.radius) {
    events = events.filter(event => {
      const distance = calculateDistance(
        currentFilters.value.latitude!,
        currentFilters.value.longitude!,
        event.latitude,
        event.longitude
      )
      return distance <= currentFilters.value.radius!
    })
  }
  
  // Apply age restriction filter
  if (currentFilters.value.age_restriction) {
    events = events.filter(event =>
      event.age_restrictions === currentFilters.value.age_restriction
    )
  }
  
  return events
})

const filteredAndSortedEvents = computed(() => {
  let events = [...filteredEvents.value]
  
  switch (sortBy.value) {
    case 'date':
      events.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
      break
    case 'rating':
      events.sort((a, b) => (b.average_rating || 0) - (a.average_rating || 0))
      break
    case 'distance':
      if (userLocation.value) {
        events.sort((a, b) => {
          const distanceA = calculateDistance(
            userLocation.value!.lat,
            userLocation.value!.lng,
            a.latitude,
            a.longitude
          )
          const distanceB = calculateDistance(
            userLocation.value!.lat,
            userLocation.value!.lng,
            b.latitude,
            b.longitude
          )
          return distanceA - distanceB
        })
      }
      break
    case 'title':
      events.sort((a, b) => a.title.localeCompare(b.title))
      break
  }
  
  return events
})

const selectedEvent = computed(() => {
  if (!selectedEventId.value) return null
  return eventsWithCategories.value.find(event => event.id === selectedEventId.value) || null
})

const hasActiveFilters = computed(() => {
  return Object.keys(currentFilters.value).some(key => {
    const value = currentFilters.value[key as keyof EventFiltersType]
    return value !== undefined && value !== null && value !== '' && 
           (Array.isArray(value) ? value.length > 0 : true)
  })
})

const canLoadMore = computed(() => {
  return pagination.value.page < pagination.value.pages
})

// Methods
async function loadEvents() {
  try {
    await eventsStore.fetchEvents()
    await eventsStore.fetchCategories()
    await eventsStore.fetchTags()
  } catch (err) {
    console.error('Failed to load events:', err)
  }
}

async function loadMoreEvents() {
  if (loadingMore.value || !canLoadMore.value) return
  
  try {
    loadingMore.value = true
    // Implement pagination - this would depend on your API
    // await eventsStore.fetchEvents({ ...currentFilters.value, page: pagination.value.page + 1 })
  } catch (err) {
    console.error('Failed to load more events:', err)
  } finally {
    loadingMore.value = false
  }
}

function handleSearch(query: string) {
  currentFilters.value = {
    ...currentFilters.value,
    search: query || undefined
  }
}

function handleEventSelected(event: Event) {
  selectedEventId.value = event.id
  showEventModal.value = true
  
  // Update URL
  router.push({
    name: 'events',
    query: { event: event.id.toString() }
  })
}

function handleLocationSelected(location: google.maps.places.AutocompletePrediction) {
  // You could geocode the location and filter events near it
  console.log('Location selected:', location)
}

function handleNearMeSearch(location: { lat: number; lng: number }) {
  mapStore.setUserLocation(location)
  
  // Apply location filter
  currentFilters.value = {
    ...currentFilters.value,
    latitude: location.lat,
    longitude: location.lng,
    radius: 5 // 5km radius
  }
  
  // Sort by distance
  sortBy.value = 'distance'
}

function handleFiltersChanged(newFilters: EventFiltersType) {
  currentFilters.value = newFilters
}

function handleSortChange() {
  // Sorting is handled by the computed property
}

function handleEventClick(event: Event) {
  selectedEventId.value = event.id
  showEventModal.value = true
  
  // Update URL
  router.push({
    name: 'events',
    query: { event: event.id.toString() }
  })
}

function handleEventHover(event: Event | null) {
  hoveredEventId.value = event?.id || null
}

function handleEventViewDetails(event: Event) {
  handleEventClick(event)
}

function handleEventModalClose() {
  showEventModal.value = false
  selectedEventId.value = null
  
  if (route.query.event) {
    router.push({ name: 'events', query: {} })
  }
}

function clearAllFilters() {
  currentFilters.value = {}
}

function calculateDistance(lat1: number, lng1: number, lat2: number, lng2: number): number {
  const R = 6371 // Earth's radius in kilometers
  const dLat = toRadians(lat2 - lat1)
  const dLng = toRadians(lng2 - lng1)
  
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(toRadians(lat1)) * Math.cos(toRadians(lat2)) *
            Math.sin(dLng / 2) * Math.sin(dLng / 2)
            
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return R * c
}

function toRadians(degrees: number): number {
  return degrees * (Math.PI / 180)
}

// Watchers
watch(() => route.query.event, (eventId) => {
  if (eventId && typeof eventId === 'string') {
    const id = parseInt(eventId, 10)
    if (!isNaN(id)) {
      selectedEventId.value = id
      showEventModal.value = true
    }
  } else {
    selectedEventId.value = null
    showEventModal.value = false
  }
})

watch(geoPosition, (position) => {
  if (position) {
    mapStore.setUserLocation(position)
  }
})

// Lifecycle
onMounted(async () => {
  await loadEvents()
  
  // Handle initial event selection from URL
  if (route.query.event && typeof route.query.event === 'string') {
    const eventId = parseInt(route.query.event, 10)
    if (!isNaN(eventId)) {
      selectedEventId.value = eventId
      showEventModal.value = true
    }
  }
})
</script>