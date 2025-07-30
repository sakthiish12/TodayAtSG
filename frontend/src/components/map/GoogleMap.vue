<template>
  <div class="relative w-full h-full">
    <!-- Map container -->
    <div
      ref="mapContainer"
      class="w-full h-full rounded-lg overflow-hidden"
      :class="{ 'opacity-50': isInitializing }"
    />
    
    <!-- Map controls overlay -->
    <div class="absolute top-4 right-4 flex flex-col gap-2">
      <!-- Map style switcher -->
      <div class="bg-white rounded-lg shadow-lg p-2">
        <select
          v-model="selectedMapStyle"
          @change="changeMapStyle"
          class="text-sm border-none focus:ring-0 bg-transparent"
        >
          <option value="roadmap">Roadmap</option>
          <option value="satellite">Satellite</option>
          <option value="hybrid">Hybrid</option>
          <option value="terrain">Terrain</option>
        </select>
      </div>
      
      <!-- User location controls -->
      <div class="bg-white rounded-lg shadow-lg p-2 flex flex-col gap-1">
        <button
          @click="toggleUserLocation"
          :class="[
            'p-2 rounded text-sm font-medium transition-colors',
            showUserLocation 
              ? 'bg-blue-600 text-white' 
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          ]"
          :disabled="!locationPermissionGranted"
          title="Toggle user location"
        >
          <MapPin class="w-4 h-4" />
        </button>
        
        <button
          @click="centerOnUserLocation"
          class="p-2 rounded text-sm font-medium bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors"
          :disabled="!userLocation"
          title="Center on my location"
        >
          <Crosshair class="w-4 h-4" />
        </button>
      </div>
      
      <!-- Fit bounds control -->
      <button
        @click="fitBoundsToMarkers"
        class="bg-white rounded-lg shadow-lg p-3 text-gray-700 hover:bg-gray-50 transition-colors"
        :disabled="allMarkers.length === 0"
        title="Fit all events"
      >
        <Maximize2 class="w-4 h-4" />
      </button>
    </div>
    
    <!-- Loading overlay -->
    <div
      v-if="isInitializing"
      class="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center rounded-lg"
    >
      <div class="text-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
        <p class="text-sm text-gray-600">Loading map...</p>
      </div>
    </div>
    
    <!-- Error overlay -->
    <div
      v-if="error"
      class="absolute inset-0 bg-red-50 flex items-center justify-center rounded-lg"
    >
      <div class="text-center p-4">
        <AlertCircle class="w-8 h-8 text-red-600 mx-auto mb-2" />
        <p class="text-sm text-red-800 font-medium">Failed to load map</p>
        <p class="text-xs text-red-600 mt-1">{{ error }}</p>
        <button
          @click="initializeMap"
          class="mt-3 px-4 py-2 bg-red-600 text-white rounded-md text-sm font-medium hover:bg-red-700 transition-colors"
        >
          Retry
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { 
  MapPin, 
  Crosshair, 
  Maximize2, 
  AlertCircle 
} from 'lucide-vue-next'
import { useMapStore } from '@/stores/map'
import { useEventsStore } from '@/stores/events'
import { googleMapsService } from '@/services/googleMaps'
import type { Event } from '@/types'
import type { MarkerData } from '@/stores/map'

interface Props {
  events?: Event[]
  selectedEventId?: number | null
  hoveredEventId?: number | null
  height?: string
}

const props = withDefaults(defineProps<Props>(), {
  events: () => [],
  selectedEventId: null,
  hoveredEventId: null,
  height: '100%'
})

const emit = defineEmits<{
  eventClick: [event: Event]
  eventHover: [event: Event | null]
  boundsChanged: [bounds: google.maps.LatLngBounds]
  mapClick: [latLng: google.maps.LatLng]
}>()

// Stores
const mapStore = useMapStore()
const eventsStore = useEventsStore()

const {
  map,
  mapLoaded,
  isInitializing,
  error,
  center,
  zoom,
  markers,
  markerCluster,
  selectedMarker,
  userLocation,
  locationPermissionGranted,
  showUserLocation,
  mapStyle,
  allMarkers
} = storeToRefs(mapStore)

const { categories } = storeToRefs(eventsStore)

// Component state
const mapContainer = ref<HTMLElement>()
const selectedMapStyle = ref<'roadmap' | 'satellite' | 'hybrid' | 'terrain'>('roadmap')
const googleMarkers = ref<Map<number, google.maps.Marker>>(new Map())
const infoWindows = ref<Map<number, google.maps.InfoWindow>>(new Map())
const activeInfoWindow = ref<google.maps.InfoWindow | null>(null)

// Computed
const eventsToShow = computed(() => {
  return props.events.length > 0 ? props.events : eventsStore.eventsWithCategories
})

// Methods
async function initializeMap() {
  if (!mapContainer.value) return

  try {
    mapStore.setInitializing(true)
    mapStore.clearError()

    const mapInstance = await googleMapsService.createMap(mapContainer.value, {
      center: center.value,
      zoom: zoom.value,
      mapTypeId: selectedMapStyle.value
    })

    mapStore.setMap(mapInstance)

    // Set up map event listeners
    mapInstance.addListener('click', (event: google.maps.MouseEvent) => {
      if (event.latLng) {
        emit('mapClick', event.latLng)
        closeActiveInfoWindow()
      }
    })

    mapInstance.addListener('bounds_changed', () => {
      const bounds = mapInstance.getBounds()
      if (bounds) {
        emit('boundsChanged', bounds)
      }
    })

    // Request user location
    await requestUserLocation()

    // Initialize events on map
    await updateMarkers()

  } catch (err: any) {
    console.error('Failed to initialize map:', err)
    mapStore.setError(err.message || 'Failed to initialize map')
  } finally {
    mapStore.setInitializing(false)
  }
}

async function updateMarkers() {
  if (!map.value) return

  // Clear existing markers
  clearMarkers()

  const markersToAdd: google.maps.Marker[] = []

  // Create markers for events
  for (const event of eventsToShow.value) {
    const category = categories.value.find(cat => cat.id === event.category_id)
    
    const marker = googleMapsService.createEventMarker(map.value, {
      event,
      category,
      onClick: (clickedEvent) => {
        selectEvent(clickedEvent)
        emit('eventClick', clickedEvent)
      },
      onHover: (hoveredEvent) => {
        emit('eventHover', hoveredEvent)
      }
    })

    const infoWindow = googleMapsService.createInfoWindow(event, category)
    
    googleMarkers.value.set(event.id, marker)
    infoWindows.value.set(event.id, infoWindow)
    markersToAdd.push(marker)
    
    // Add marker to map store
    mapStore.addMarker(event)
  }

  // Initialize clustering
  if (markersToAdd.length > 0) {
    try {
      await googleMapsService.initializeMarkerClusterer(map.value, markersToAdd, {
        gridSize: 60,
        maxZoom: 15,
        minimumClusterSize: 2
      })
    } catch (error) {
      console.error('Failed to initialize marker clustering:', error)
    }
  }
}

function clearMarkers() {
  // Close any open info windows
  closeActiveInfoWindow()
  
  // Clear Google Maps markers
  googleMarkers.value.forEach(marker => {
    marker.setMap(null)
  })
  googleMarkers.value.clear()
  
  // Clear info windows
  infoWindows.value.clear()
  
  // Clear clusterer
  googleMapsService.clearClusterer()
  
  // Clear map store markers
  mapStore.clearMarkers()
}

function selectEvent(event: Event) {
  closeActiveInfoWindow()
  
  const marker = googleMarkers.value.get(event.id)
  const infoWindow = infoWindows.value.get(event.id)
  
  if (marker && infoWindow && map.value) {
    infoWindow.open(map.value, marker)
    activeInfoWindow.value = infoWindow
    
    // Highlight marker
    googleMapsService.highlightMarker(marker)
    
    // Pan to marker
    map.value.panTo(marker.getPosition()!)
    
    // Update store
    mapStore.selectMarker(event.id)
  }
}

function closeActiveInfoWindow() {
  if (activeInfoWindow.value) {
    activeInfoWindow.value.close()
    activeInfoWindow.value = null
  }
  
  // Reset all marker styles
  googleMarkers.value.forEach((marker, eventId) => {
    const event = eventsToShow.value.find(e => e.id === eventId)
    const category = categories.value.find(cat => cat.id === event?.category_id)
    googleMapsService.resetMarkerStyle(marker, category)
  })
}

async function requestUserLocation() {
  try {
    const position = await googleMapsService.getCurrentLocation()
    const userPos = {
      lat: position.coords.latitude,
      lng: position.coords.longitude
    }
    
    mapStore.setUserLocation(userPos)
  } catch (error) {
    console.log('Location access denied or failed:', error)
  }
}

function toggleUserLocation() {
  mapStore.toggleUserLocation()
}

function centerOnUserLocation() {
  if (userLocation.value) {
    mapStore.setCenter(userLocation.value, 15)
  }
}

function fitBoundsToMarkers() {
  mapStore.fitBoundsToMarkers()
}

function changeMapStyle() {
  mapStore.setMapStyle(selectedMapStyle.value)
}

// Global event listener for info window actions
function setupGlobalEventListeners() {
  window.addEventListener('view-event-details', (event: any) => {
    const eventId = event.detail.id
    const eventData = eventsToShow.value.find(e => e.id === eventId)
    if (eventData) {
      emit('eventClick', eventData)
    }
  })
}

// Watchers
watch(eventsToShow, async () => {
  if (mapLoaded.value) {
    await nextTick()
    await updateMarkers()
  }
}, { deep: true })

watch(() => props.selectedEventId, (newEventId) => {
  if (newEventId) {
    const event = eventsToShow.value.find(e => e.id === newEventId)
    if (event) {
      selectEvent(event)
    }
  } else {
    closeActiveInfoWindow()
  }
})

watch(() => props.hoveredEventId, (newEventId, oldEventId) => {
  // Reset previous hovered marker
  if (oldEventId) {
    const oldMarker = googleMarkers.value.get(oldEventId)
    if (oldMarker) {
      const event = eventsToShow.value.find(e => e.id === oldEventId)
      const category = categories.value.find(cat => cat.id === event?.category_id)
      googleMapsService.resetMarkerStyle(oldMarker, category)
    }
  }
  
  // Highlight new hovered marker
  if (newEventId) {
    const newMarker = googleMarkers.value.get(newEventId)
    if (newMarker) {
      googleMapsService.highlightMarker(newMarker)
    }
  }
})

// Lifecycle
onMounted(async () => {
  setupGlobalEventListeners()
  await initializeMap()
})

onUnmounted(() => {
  clearMarkers()
  window.removeEventListener('view-event-details', () => {})
})
</script>

<style scoped>
.map-container {
  height: v-bind(height);
}
</style>