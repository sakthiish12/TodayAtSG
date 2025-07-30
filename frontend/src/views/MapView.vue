<template>
  <div class="h-screen flex flex-col">
    <!-- Top navigation bar -->
    <div class="bg-white border-b border-gray-200 px-4 py-3 flex-shrink-0">
      <div class="flex items-center gap-4">
        <!-- Mobile menu button -->
        <button
          @click="showMobileFilters = !showMobileFilters"
          class="md:hidden p-2 text-gray-600 hover:text-gray-900 transition-colors"
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
        
        <!-- Results count -->
        <div class="hidden lg:block text-sm text-gray-600">
          {{ filteredEvents.length }} event{{ filteredEvents.length !== 1 ? 's' : '' }}
        </div>
      </div>
    </div>
    
    <!-- Main content area -->
    <div class="flex-1 flex relative">
      <!-- Sidebar with filters (desktop) -->
      <div 
        class="hidden md:block w-80 bg-white border-r border-gray-200 overflow-y-auto"
        :class="showFilters ? 'block' : 'hidden'"
      >
        <div class="p-4">
          <EventFilters
            @filters-changed="handleFiltersChanged"
          />
        </div>
      </div>
      
      <!-- Mobile filters overlay -->
      <div
        v-if="showMobileFilters"
        class="fixed inset-0 z-50 md:hidden"
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
      
      <!-- Map container -->
      <div class="flex-1 relative">
        <GoogleMap
          :events="filteredEvents"
          :selected-event-id="selectedEventId"
          :hovered-event-id="hoveredEventId"
          @event-click="handleEventClick"
          @event-hover="handleEventHover"
          @bounds-changed="handleBoundsChanged"
          @map-click="handleMapClick"
        />
        
        <!-- Map controls overlay -->
        <div class="absolute top-4 left-4 flex flex-col gap-2">
          <!-- Toggle filters button -->
          <button
            @click="showFilters = !showFilters"
            class="hidden md:flex items-center justify-center w-10 h-10 bg-white rounded-lg shadow-lg text-gray-600 hover:text-gray-900 transition-colors"
            title="Toggle filters"
          >
            <Filter class="w-5 h-5" />
          </button>
          
          <!-- Current location button -->
          <button
            @click="centerOnUserLocation"
            :disabled="!userLocation || geoLoading"
            class="flex items-center justify-center w-10 h-10 bg-white rounded-lg shadow-lg text-gray-600 hover:text-gray-900 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title="Center on my location"
          >
            <div v-if="geoLoading" class="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
            <Navigation v-else class="w-5 h-5" />
          </button>
        </div>
        
        <!-- Event count overlay (mobile) -->
        <div class="absolute bottom-4 left-4 bg-white rounded-lg shadow-lg px-3 py-2 lg:hidden">
          <div class="text-sm font-medium text-gray-900">
            {{ filteredEvents.length }} event{{ filteredEvents.length !== 1 ? 's' : '' }}
          </div>
        </div>
        
        <!-- Loading overlay -->
        <div
          v-if="loading"
          class="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center"
        >
          <div class="text-center">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p class="text-gray-600">Loading events...</p>
          </div>
        </div>
        
        <!-- Error overlay -->
        <div
          v-if="error"
          class="absolute inset-0 bg-red-50 flex items-center justify-center"
        >
          <div class="text-center p-4">
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
        </div>
      </div>
    </div>
    
    <!-- Event modal -->
    <EventModal
      :event="selectedEvent"
      :is-open="showEventModal"
      @close="handleEventModalClose"
    />
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
  Navigation,
  AlertCircle
} from 'lucide-vue-next'
import { useEventsStore } from '@/stores/events'
import { useMapStore } from '@/stores/map'
import { useGeolocation } from '@/composables/useGeolocation'
import GoogleMap from '@/components/map/GoogleMap.vue'
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
  filters
} = storeToRefs(eventsStore)

const {
  userLocation,
  selectedEvent: mapSelectedEvent
} = storeToRefs(mapStore)

// Geolocation
const {
  position: geoPosition,
  loading: geoLoading,
  getCurrentPosition
} = useGeolocation({ immediate: true })

// State
const showFilters = ref(true)
const showMobileFilters = ref(false)
const showEventModal = ref(false)
const selectedEventId = ref<number | null>(null)
const hoveredEventId = ref<number | null>(null)
const currentFilters = ref<EventFiltersType>({})

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

const selectedEvent = computed(() => {
  if (!selectedEventId.value) return null
  return eventsWithCategories.value.find(event => event.id === selectedEventId.value) || null
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
    name: 'map',
    query: { event: event.id.toString() }
  })
}

function handleLocationSelected(location: google.maps.places.AutocompletePrediction) {
  // You could geocode the location and center the map on it
  console.log('Location selected:', location)
}

function handleNearMeSearch(location: { lat: number; lng: number }) {
  mapStore.setUserLocation(location)
  mapStore.setCenter(location, 14)
  
  // Apply location filter
  currentFilters.value = {
    ...currentFilters.value,
    latitude: location.lat,
    longitude: location.lng,
    radius: 5 // 5km radius
  }
}

function handleFiltersChanged(newFilters: EventFiltersType) {
  currentFilters.value = newFilters
}

function handleEventClick(event: Event) {
  selectedEventId.value = event.id
  showEventModal.value = true
  
  // Update URL
  router.push({
    name: 'map',
    query: { event: event.id.toString() }
  })
}

function handleEventHover(event: Event | null) {
  hoveredEventId.value = event?.id || null
}

function handleBoundsChanged(bounds: google.maps.LatLngBounds) {
  // You could use this to only show events within the current map bounds
  // for performance optimization
}

function handleMapClick() {
  // Clear selection when clicking on empty map area
  selectedEventId.value = null
  hoveredEventId.value = null
  
  if (route.query.event) {
    router.push({ name: 'map', query: {} })
  }
}

function handleEventModalClose() {
  showEventModal.value = false
  selectedEventId.value = null
  
  if (route.query.event) {
    router.push({ name: 'map', query: {} })
  }
}

async function centerOnUserLocation() {
  if (userLocation.value) {
    mapStore.setCenter(userLocation.value, 15)
  } else {
    try {
      const position = await getCurrentPosition()
      mapStore.setUserLocation(position)
      mapStore.setCenter(position, 15)
    } catch (error) {
      console.error('Failed to get current location:', error)
    }
  }
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