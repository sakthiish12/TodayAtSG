import { Loader } from '@googlemaps/js-api-loader'
import type { Event, Category } from '@/types'
import type { MarkerData } from '@/stores/map'

interface MarkerClusterOptions {
  gridSize?: number
  maxZoom?: number
  minimumClusterSize?: number
  styles?: Array<{
    textColor: string
    textSize: number
    url: string
    height: number
    width: number
  }>
}

interface EventMarkerOptions {
  event: Event
  category?: Category
  onClick?: (event: Event) => void
  onHover?: (event: Event | null) => void
}

class GoogleMapsService {
  private loader: Loader
  private isLoaded = false
  private clusterer: any = null

  constructor() {
    this.loader = new Loader({
      apiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY || '',
      version: 'weekly',
      libraries: ['places', 'geometry']
    })
  }

  async initialize(): Promise<void> {
    if (this.isLoaded) return

    try {
      await this.loader.load()
      this.isLoaded = true
    } catch (error) {
      console.error('Failed to load Google Maps API:', error)
      throw new Error('Google Maps API failed to load')
    }
  }

  async createMap(
    element: HTMLElement,
    options: google.maps.MapOptions = {}
  ): Promise<google.maps.Map> {
    await this.initialize()

    const defaultOptions: google.maps.MapOptions = {
      center: { lat: 1.3521, lng: 103.8198 }, // Singapore
      zoom: 12,
      mapTypeId: google.maps.MapTypeId.ROADMAP,
      streetViewControl: false,
      mapTypeControl: true,
      fullscreenControl: true,
      zoomControl: true,
      styles: [
        {
          featureType: 'poi',
          elementType: 'labels',
          stylers: [{ visibility: 'off' }]
        }
      ]
    }

    return new google.maps.Map(element, {
      ...defaultOptions,
      ...options
    })
  }

  getCategoryIcon(category?: Category): string {
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

    const categoryName = category?.name?.toLowerCase() || 'default'
    return iconMap[categoryName] || '📍'
  }

  getCategoryColor(category?: Category): string {
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

    const categoryName = category?.name?.toLowerCase() || 'default'
    return colorMap[categoryName] || '#757575'
  }

  createEventMarker(
    map: google.maps.Map,
    options: EventMarkerOptions
  ): google.maps.Marker {
    const { event, category, onClick, onHover } = options
    
    const markerOptions: google.maps.MarkerOptions = {
      position: { lat: event.latitude, lng: event.longitude },
      map,
      title: event.title,
      icon: {
        path: google.maps.SymbolPath.CIRCLE,
        fillColor: this.getCategoryColor(category),
        fillOpacity: 0.8,
        strokeColor: '#ffffff',
        strokeWeight: 2,
        scale: 8
      },
      zIndex: 1
    }

    const marker = new google.maps.Marker(markerOptions)

    // Add click listener
    if (onClick) {
      marker.addListener('click', () => onClick(event))
    }

    // Add hover listeners
    if (onHover) {
      marker.addListener('mouseover', () => onHover(event))
      marker.addListener('mouseout', () => onHover(null))
    }

    return marker
  }

  createInfoWindow(event: Event, category?: Category): google.maps.InfoWindow {
    const rating = event.average_rating ? 
      `<div class="flex items-center mt-1">
        <span class="text-yellow-500">★</span>
        <span class="ml-1 text-sm text-gray-600">${event.average_rating.toFixed(1)} (${event.review_count || 0})</span>
      </div>` : ''

    const ageRestriction = event.age_restrictions ? 
      `<div class="text-xs text-gray-500 mt-1">${event.age_restrictions}</div>` : ''

    const content = `
      <div class="p-3 max-w-xs">
        <div class="flex items-start justify-between">
          <h3 class="font-semibold text-lg text-gray-900 pr-2">${event.title}</h3>
          <span class="inline-block px-2 py-1 text-xs rounded-full text-white" 
                style="background-color: ${this.getCategoryColor(category)}">
            ${category?.name || 'Event'}
          </span>
        </div>
        
        <div class="mt-2 text-sm text-gray-600">
          <div class="flex items-center">
            <span class="mr-1">📅</span>
            ${new Date(event.date).toLocaleDateString()} at ${event.time}
          </div>
          <div class="flex items-center mt-1">
            <span class="mr-1">📍</span>
            ${event.location}
          </div>
        </div>
        
        ${rating}
        ${ageRestriction}
        
        ${event.description ? 
          `<p class="mt-2 text-sm text-gray-700 line-clamp-2">${event.description}</p>` : 
          ''
        }
        
        <button class="mt-3 w-full bg-blue-600 text-white px-3 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
                onclick="window.dispatchEvent(new CustomEvent('view-event-details', { detail: { id: ${event.id} } }))">
          View Details
        </button>
      </div>
    `

    return new google.maps.InfoWindow({
      content,
      maxWidth: 300
    })
  }

  async initializeMarkerClusterer(
    map: google.maps.Map,
    markers: google.maps.Marker[],
    options: MarkerClusterOptions = {}
  ): Promise<any> {
    // Import MarkerClusterer dynamically
    const { MarkerClusterer } = await import('@googlemaps/markerclusterer')

    const defaultOptions = {
      gridSize: 60,
      maxZoom: 15,
      minimumClusterSize: 2,
      styles: [
        {
          textColor: 'white',
          textSize: 12,
          url: 'data:image/svg+xml;base64,' + btoa(`
            <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40">
              <circle cx="20" cy="20" r="18" fill="#4285F4" stroke="#ffffff" stroke-width="2"/>
            </svg>
          `),
          height: 40,
          width: 40
        },
        {
          textColor: 'white',
          textSize: 13,
          url: 'data:image/svg+xml;base64,' + btoa(`
            <svg xmlns="http://www.w3.org/2000/svg" width="50" height="50" viewBox="0 0 50 50">
              <circle cx="25" cy="25" r="23" fill="#EA4335" stroke="#ffffff" stroke-width="2"/>
            </svg>
          `),
          height: 50,
          width: 50
        },
        {
          textColor: 'white',
          textSize: 14,
          url: 'data:image/svg+xml;base64,' + btoa(`
            <svg xmlns="http://www.w3.org/2000/svg" width="60" height="60" viewBox="0 0 60 60">
              <circle cx="30" cy="30" r="28" fill="#FBBC04" stroke="#ffffff" stroke-width="2"/>
            </svg>
          `),
          height: 60,
          width: 60
        }
      ]
    }

    const clustererOptions = { ...defaultOptions, ...options }
    
    this.clusterer = new MarkerClusterer({ 
      map, 
      markers,
      ...clustererOptions
    })

    return this.clusterer
  }

  updateClusterer(markers: google.maps.Marker[]): void {
    if (this.clusterer) {
      this.clusterer.clearMarkers()
      this.clusterer.addMarkers(markers)
    }
  }

  clearClusterer(): void {
    if (this.clusterer) {
      this.clusterer.clearMarkers()
    }
  }

  async getCurrentLocation(): Promise<GeolocationPosition> {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation is not supported by this browser'))
        return
      }

      navigator.geolocation.getCurrentPosition(
        (position) => resolve(position),
        (error) => reject(error),
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 300000 // 5 minutes
        }
      )
    })
  }

  calculateDistance(
    lat1: number, 
    lng1: number, 
    lat2: number, 
    lng2: number
  ): number {
    const R = 6371 // Earth's radius in kilometers
    const dLat = this.toRadians(lat2 - lat1)
    const dLng = this.toRadians(lng2 - lng1)
    
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(this.toRadians(lat1)) * Math.cos(this.toRadians(lat2)) *
              Math.sin(dLng / 2) * Math.sin(dLng / 2)
              
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
    return R * c
  }

  private toRadians(degrees: number): number {
    return degrees * (Math.PI / 180)
  }

  async geocodeAddress(address: string): Promise<google.maps.GeocoderResult[]> {
    await this.initialize()
    
    const geocoder = new google.maps.Geocoder()
    
    return new Promise((resolve, reject) => {
      geocoder.geocode({ address }, (results, status) => {
        if (status === google.maps.GeocoderStatus.OK && results) {
          resolve(results)
        } else {
          reject(new Error(`Geocoding failed: ${status}`))
        }
      })
    })
  }

  async reverseGeocode(lat: number, lng: number): Promise<google.maps.GeocoderResult[]> {
    await this.initialize()
    
    const geocoder = new google.maps.Geocoder()
    
    return new Promise((resolve, reject) => {
      geocoder.geocode({ location: { lat, lng } }, (results, status) => {
        if (status === google.maps.GeocoderStatus.OK && results) {
          resolve(results)
        } else {
          reject(new Error(`Reverse geocoding failed: ${status}`))
        }
      })
    })
  }

  createSearchBox(input: HTMLInputElement, map: google.maps.Map): google.maps.places.SearchBox {
    const searchBox = new google.maps.places.SearchBox(input)

    // Bias the SearchBox results towards current map's viewport
    map.addListener('bounds_changed', () => {
      searchBox.setBounds(map.getBounds() as google.maps.LatLngBounds)
    })

    return searchBox
  }

  highlightMarker(marker: google.maps.Marker): void {
    marker.setIcon({
      path: google.maps.SymbolPath.CIRCLE,
      fillColor: '#FF5722',
      fillOpacity: 1,
      strokeColor: '#ffffff',
      strokeWeight: 3,
      scale: 12
    })
    marker.setZIndex(1000)
  }

  resetMarkerStyle(marker: google.maps.Marker, category?: Category): void {
    marker.setIcon({
      path: google.maps.SymbolPath.CIRCLE,
      fillColor: this.getCategoryColor(category),
      fillOpacity: 0.8,
      strokeColor: '#ffffff',
      strokeWeight: 2,
      scale: 8
    })
    marker.setZIndex(1)
  }
}

export const googleMapsService = new GoogleMapsService()