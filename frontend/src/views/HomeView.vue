<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Map, 
  List, 
  Search, 
  MapPin, 
  Calendar, 
  Star,
  ArrowRight 
} from 'lucide-vue-next'

const router = useRouter()

// Auto-redirect to map view for better UX
onMounted(() => {
  // Redirect to map view after a short delay
  setTimeout(() => {
    router.push('/map')
  }, 2000)
})

function goToMap() {
  router.push('/map')
}

function goToEvents() {
  router.push('/events')
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 flex items-center justify-center">
    <div class="text-center text-white px-4">
      <!-- Logo and title -->
      <div class="mb-8">
        <div class="w-24 h-24 bg-white bg-opacity-20 rounded-full flex items-center justify-center mx-auto mb-6 backdrop-blur-sm">
          <span class="text-4xl font-bold text-white">SG</span>
        </div>
        <h1 class="text-5xl md:text-7xl font-bold mb-4">
          TodayAtSG
        </h1>
        <p class="text-xl md:text-2xl text-blue-100 mb-8">
          Discover amazing events happening in Singapore
        </p>
      </div>
      
      <!-- Feature highlights -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12 max-w-4xl mx-auto">
        <div class="bg-white bg-opacity-10 backdrop-blur-sm rounded-lg p-6">
          <Map class="w-12 h-12 mx-auto mb-4 text-blue-200" />
          <h3 class="text-lg font-semibold mb-2">Interactive Map</h3>
          <p class="text-blue-100 text-sm">
            Explore events on an interactive map with clustering and filtering
          </p>
        </div>
        
        <div class="bg-white bg-opacity-10 backdrop-blur-sm rounded-lg p-6">
          <Search class="w-12 h-12 mx-auto mb-4 text-purple-200" />
          <h3 class="text-lg font-semibold mb-2">Smart Search</h3>
          <p class="text-blue-100 text-sm">
            Find events by location, category, or keywords with intelligent suggestions
          </p>
        </div>
        
        <div class="bg-white bg-opacity-10 backdrop-blur-sm rounded-lg p-6">
          <Star class="w-12 h-12 mx-auto mb-4 text-pink-200" />
          <h3 class="text-lg font-semibold mb-2">Reviews & Ratings</h3>
          <p class="text-blue-100 text-sm">
            Read reviews and rate events to help others discover great experiences
          </p>
        </div>
      </div>
      
      <!-- CTA buttons -->
      <div class="flex flex-col sm:flex-row gap-4 justify-center mb-8">
        <button
          @click="goToMap"
          class="bg-white text-blue-600 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-blue-50 transition-colors flex items-center justify-center"
        >
          <Map class="w-6 h-6 mr-2" />
          Explore Map
          <ArrowRight class="w-5 h-5 ml-2" />
        </button>
        
        <button
          @click="goToEvents"
          class="bg-transparent border-2 border-white text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-white hover:text-blue-600 transition-colors flex items-center justify-center"
        >
          <List class="w-6 h-6 mr-2" />
          Browse Events
        </button>
      </div>
      
      <!-- Auto-redirect message -->
      <div class="text-blue-200 text-sm">
        <div class="flex items-center justify-center">
          <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
          Redirecting to map view...
        </div>
      </div>
    </div>
  </div>
</template>
