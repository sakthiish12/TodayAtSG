import { ref, computed, onMounted, onUnmounted } from 'vue'
import { googleMapsService } from '@/services/googleMaps'

export interface GeolocationPosition {
  lat: number
  lng: number
  accuracy?: number
  timestamp: number
}

export interface GeolocationError {
  code: number
  message: string
}

export interface UseGeolocationOptions {
  enableHighAccuracy?: boolean
  timeout?: number
  maximumAge?: number
  immediate?: boolean
  watchPosition?: boolean
}

export function useGeolocation(options: UseGeolocationOptions = {}) {
  const {
    enableHighAccuracy = true,
    timeout = 15000,
    maximumAge = 300000, // 5 minutes
    immediate = true,
    watchPosition = false
  } = options

  // State
  const position = ref<GeolocationPosition | null>(null)
  const error = ref<GeolocationError | null>(null)
  const loading = ref(false)
  const supported = ref(false)
  const permissionStatus = ref<'granted' | 'denied' | 'prompt' | 'unknown'>('unknown')
  
  // Watch ID for continuous tracking
  let watchId: number | null = null

  // Computed
  const isAvailable = computed(() => supported.value && position.value !== null)
  const hasPermission = computed(() => permissionStatus.value === 'granted')
  const isError = computed(() => error.value !== null)

  // Methods
  function checkSupport(): boolean {
    const isSupported = 'geolocation' in navigator
    supported.value = isSupported
    return isSupported
  }

  async function checkPermission(): Promise<'granted' | 'denied' | 'prompt' | 'unknown'> {
    if (!supported.value) {
      permissionStatus.value = 'unknown'
      return 'unknown'
    }

    try {
      // Check if permissions API is supported
      if ('permissions' in navigator) {
        const permission = await navigator.permissions.query({ name: 'geolocation' })
        permissionStatus.value = permission.state as 'granted' | 'denied' | 'prompt'
        
        // Listen for permission changes
        permission.addEventListener('change', () => {
          permissionStatus.value = permission.state as 'granted' | 'denied' | 'prompt'
        })
        
        return permission.state as 'granted' | 'denied' | 'prompt'
      } else {
        // Fallback for browsers without permissions API
        permissionStatus.value = 'prompt'
        return 'prompt'
      }
    } catch (err) {
      console.warn('Failed to check geolocation permission:', err)
      permissionStatus.value = 'unknown'
      return 'unknown'
    }
  }

  function getCurrentPosition(): Promise<GeolocationPosition> {
    return new Promise((resolve, reject) => {
      if (!supported.value) {
        const geoError: GeolocationError = {
          code: 0,
          message: 'Geolocation is not supported by this browser'
        }
        reject(geoError)
        return
      }

      loading.value = true
      error.value = null

      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const geoPosition: GeolocationPosition = {
            lat: pos.coords.latitude,
            lng: pos.coords.longitude,
            accuracy: pos.coords.accuracy,
            timestamp: pos.timestamp
          }
          
          position.value = geoPosition
          loading.value = false
          resolve(geoPosition)
        },
        (err) => {
          const geoError: GeolocationError = {
            code: err.code,
            message: getErrorMessage(err.code)
          }
          
          error.value = geoError
          loading.value = false
          reject(geoError)
        },
        {
          enableHighAccuracy,
          timeout,
          maximumAge
        }
      )
    })
  }

  function startWatching(): number | null {
    if (!supported.value || watchId !== null) {
      return watchId
    }

    watchId = navigator.geolocation.watchPosition(
      (pos) => {
        const geoPosition: GeolocationPosition = {
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
          accuracy: pos.coords.accuracy,
          timestamp: pos.timestamp
        }
        
        position.value = geoPosition
        error.value = null
      },
      (err) => {
        const geoError: GeolocationError = {
          code: err.code,
          message: getErrorMessage(err.code)
        }
        
        error.value = geoError
      },
      {
        enableHighAccuracy,
        timeout,
        maximumAge
      }
    )

    return watchId
  }

  function stopWatching(): void {
    if (watchId !== null) {
      navigator.geolocation.clearWatch(watchId)
      watchId = null
    }
  }

  function clearError(): void {
    error.value = null
  }

  function getErrorMessage(code: number): string {
    switch (code) {
      case 1: // PERMISSION_DENIED
        return 'Location access denied by user'
      case 2: // POSITION_UNAVAILABLE
        return 'Location information is unavailable'
      case 3: // TIMEOUT
        return 'Location request timed out'
      default:
        return 'An unknown error occurred while retrieving location'
    }
  }

  function calculateDistance(
    lat1: number,
    lng1: number,
    lat2: number,
    lng2: number
  ): number {
    return googleMapsService.calculateDistance(lat1, lng1, lat2, lng2)
  }

  function getDistanceToPosition(targetLat: number, targetLng: number): number | null {
    if (!position.value) return null
    
    return calculateDistance(
      position.value.lat,
      position.value.lng,
      targetLat,
      targetLng
    )
  }

  async function getCurrentLocationWithFallback(): Promise<GeolocationPosition> {
    try {
      return await getCurrentPosition()
    } catch (err) {
      console.warn('Failed to get precise location, trying with lower accuracy:', err)
      
      // Try again with lower accuracy requirements
      return new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(
          (pos) => {
            const geoPosition: GeolocationPosition = {
              lat: pos.coords.latitude,
              lng: pos.coords.longitude,
              accuracy: pos.coords.accuracy,
              timestamp: pos.timestamp
            }
            
            position.value = geoPosition
            resolve(geoPosition)
          },
          (fallbackErr) => {
            const geoError: GeolocationError = {
              code: fallbackErr.code,
              message: getErrorMessage(fallbackErr.code)
            }
            reject(geoError)
          },
          {
            enableHighAccuracy: false,
            timeout: timeout * 2,
            maximumAge: maximumAge * 2
          }
        )
      })
    }
  }

  function isPositionStale(maxAge: number = maximumAge): boolean {
    if (!position.value) return true
    
    const now = Date.now()
    return (now - position.value.timestamp) > maxAge
  }

  async function refreshPosition(): Promise<GeolocationPosition> {
    return await getCurrentPosition()
  }

  // Auto-initialize
  onMounted(async () => {
    checkSupport()
    await checkPermission()
    
    if (immediate && supported.value) {
      try {
        await getCurrentPosition()
      } catch (err) {
        // Silently fail on mount, user can manually request location
      }
    }
    
    if (watchPosition && supported.value) {
      startWatching()
    }
  })

  onUnmounted(() => {
    stopWatching()
  })

  return {
    // State
    position,
    error,
    loading,
    supported,
    permissionStatus,
    
    // Computed
    isAvailable,
    hasPermission,
    isError,
    
    // Methods
    getCurrentPosition,
    getCurrentLocationWithFallback,
    refreshPosition,
    startWatching,
    stopWatching,
    checkSupport,
    checkPermission,
    clearError,
    calculateDistance,
    getDistanceToPosition,
    isPositionStale
  }
}