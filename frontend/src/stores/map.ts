import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Event, MapBounds, MapCenter } from '@/types'

export interface MarkerData {
  id: number
  position: google.maps.LatLngLiteral
  event: Event
  marker?: google.maps.Marker
  infoWindow?: google.maps.InfoWindow
}

export interface ClusterOptions {
  gridSize: number
  maxZoom: number
  minimumClusterSize: number
}

export const useMapStore = defineStore('map', () => {
  // State
  const map = ref<google.maps.Map | null>(null)
  const mapLoaded = ref(false)
  const isInitializing = ref(false)
  const error = ref<string | null>(null)
  
  // Map settings
  const center = ref<MapCenter>({
    lat: 1.3521, // Singapore latitude
    lng: 103.8198 // Singapore longitude
  })
  const zoom = ref(12)
  const bounds = ref<MapBounds | null>(null)
  
  // Markers and clustering
  const markers = ref<Map<number, MarkerData>>(new Map())
  const markerCluster = ref<any>(null) // MarkerClusterer instance
  const selectedMarker = ref<MarkerData | null>(null)
  const hoveredMarker = ref<MarkerData | null>(null)
  
  // User location
  const userLocation = ref<MapCenter | null>(null)
  const userLocationMarker = ref<google.maps.Marker | null>(null)
  const locationPermissionGranted = ref(false)
  
  // UI state
  const showUserLocation = ref(false)
  const followUserLocation = ref(false)
  const mapStyle = ref<'roadmap' | 'satellite' | 'hybrid' | 'terrain'>('roadmap')
  
  // Cluster options
  const clusterOptions = ref<ClusterOptions>({
    gridSize: 60,
    maxZoom: 15,
    minimumClusterSize: 2
  })

  // Getters
  const allMarkers = computed(() => Array.from(markers.value.values()))
  
  const markersInBounds = computed(() => {
    if (!bounds.value) return allMarkers.value
    
    return allMarkers.value.filter(marker => {
      const { lat, lng } = marker.position
      return (
        lat >= bounds.value!.south &&
        lat <= bounds.value!.north &&
        lng >= bounds.value!.west &&
        lng <= bounds.value!.east
      )
    })
  })
  
  const visibleEvents = computed(() => {
    return markersInBounds.value.map(marker => marker.event)
  })
  
  const selectedEvent = computed(() => selectedMarker.value?.event || null)

  // Actions
  function setMap(mapInstance: google.maps.Map) {
    map.value = mapInstance
    mapLoaded.value = true
    
    // Set up bounds change listener
    map.value.addListener('bounds_changed', () => {
      const mapBounds = map.value!.getBounds()
      if (mapBounds) {
        bounds.value = {
          north: mapBounds.getNorthEast().lat(),
          south: mapBounds.getSouthWest().lat(),
          east: mapBounds.getNorthEast().lng(),
          west: mapBounds.getSouthWest().lng()
        }
      }
    })
    
    // Set up zoom change listener
    map.value.addListener('zoom_changed', () => {
      zoom.value = map.value!.getZoom() || 12
    })
    
    // Set up center change listener
    map.value.addListener('center_changed', () => {
      const mapCenter = map.value!.getCenter()
      if (mapCenter) {
        center.value = {
          lat: mapCenter.lat(),
          lng: mapCenter.lng()
        }
      }
    })
  }

  function setMapBounds(newBounds: MapBounds) {
    bounds.value = newBounds
    
    if (map.value) {
      const bounds = new google.maps.LatLngBounds(
        { lat: newBounds.south, lng: newBounds.west },
        { lat: newBounds.north, lng: newBounds.east }
      )
      map.value.fitBounds(bounds)
    }
  }

  function setCenter(newCenter: MapCenter, newZoom?: number) {
    center.value = newCenter
    if (newZoom) zoom.value = newZoom
    
    if (map.value) {
      map.value.setCenter(newCenter)
      if (newZoom) map.value.setZoom(newZoom)
    }
  }

  function addMarker(event: Event): MarkerData {
    const markerData: MarkerData = {
      id: event.id,
      position: { lat: event.latitude, lng: event.longitude },
      event
    }
    
    markers.value.set(event.id, markerData)
    return markerData
  }

  function removeMarker(eventId: number) {
    const markerData = markers.value.get(eventId)
    if (markerData) {
      if (markerData.marker) {
        markerData.marker.setMap(null)
      }
      if (markerData.infoWindow) {
        markerData.infoWindow.close()
      }
      markers.value.delete(eventId)
    }
  }

  function clearMarkers() {
    markers.value.forEach(markerData => {
      if (markerData.marker) {
        markerData.marker.setMap(null)
      }
      if (markerData.infoWindow) {
        markerData.infoWindow.close()
      }
    })
    markers.value.clear()
    selectedMarker.value = null
    hoveredMarker.value = null
  }

  function selectMarker(eventId: number) {
    const markerData = markers.value.get(eventId)
    if (markerData) {
      selectedMarker.value = markerData
      
      // Center map on selected marker
      if (map.value) {
        map.value.panTo(markerData.position)
      }
    }
  }

  function hoverMarker(eventId: number | null) {
    hoveredMarker.value = eventId ? markers.value.get(eventId) || null : null
  }

  function setUserLocation(location: MapCenter) {
    userLocation.value = location
    locationPermissionGranted.value = true
    
    if (map.value && showUserLocation.value) {
      if (userLocationMarker.value) {
        userLocationMarker.value.setPosition(location)
      } else {
        userLocationMarker.value = new google.maps.Marker({
          position: location,
          map: map.value,
          title: 'Your Location',
          icon: {
            path: google.maps.SymbolPath.CIRCLE,
            fillColor: '#4285F4',
            fillOpacity: 1,
            strokeColor: '#ffffff',
            strokeWeight: 2,
            scale: 8
          }
        })
      }
      
      if (followUserLocation.value) {
        setCenter(location)
      }
    }
  }

  function toggleUserLocation() {
    showUserLocation.value = !showUserLocation.value
    
    if (showUserLocation.value && userLocation.value) {
      setUserLocation(userLocation.value)
    } else if (userLocationMarker.value) {
      userLocationMarker.value.setMap(null)
      userLocationMarker.value = null
    }
  }

  function toggleFollowUserLocation() {
    followUserLocation.value = !followUserLocation.value
    
    if (followUserLocation.value && userLocation.value) {
      setCenter(userLocation.value)
    }
  }

  function setMapStyle(style: 'roadmap' | 'satellite' | 'hybrid' | 'terrain') {
    mapStyle.value = style
    
    if (map.value) {
      map.value.setMapTypeId(style)
    }
  }

  function fitBoundsToMarkers() {
    if (!map.value || markers.value.size === 0) return
    
    const bounds = new google.maps.LatLngBounds()
    markers.value.forEach(markerData => {
      bounds.extend(markerData.position)
    })
    
    map.value.fitBounds(bounds)
  }

  function setClusterOptions(options: Partial<ClusterOptions>) {
    clusterOptions.value = { ...clusterOptions.value, ...options }
  }

  function setError(errorMessage: string | null) {
    error.value = errorMessage
  }

  function clearError() {
    error.value = null
  }

  function setInitializing(loading: boolean) {
    isInitializing.value = loading
  }

  return {
    // State
    map,
    mapLoaded,
    isInitializing,
    error,
    center,
    zoom,
    bounds,
    markers,
    markerCluster,
    selectedMarker,
    hoveredMarker,
    userLocation,
    userLocationMarker,
    locationPermissionGranted,
    showUserLocation,
    followUserLocation,
    mapStyle,
    clusterOptions,
    
    // Getters
    allMarkers,
    markersInBounds,
    visibleEvents,
    selectedEvent,
    
    // Actions
    setMap,
    setMapBounds,
    setCenter,
    addMarker,
    removeMarker,
    clearMarkers,
    selectMarker,
    hoverMarker,
    setUserLocation,
    toggleUserLocation,
    toggleFollowUserLocation,
    setMapStyle,
    fitBoundsToMarkers,
    setClusterOptions,
    setError,
    clearError,
    setInitializing
  }
})