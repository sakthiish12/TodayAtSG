<template>
  <div class="max-w-4xl mx-auto p-6">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900">Submit New Event</h1>
      <p class="text-gray-600 mt-2">
        Share your amazing event with the Singapore community. All submissions are reviewed before publication.
      </p>
    </div>

    <!-- Success Message -->
    <div v-if="isSubmitted" class="bg-green-50 border border-green-200 rounded-lg p-6 mb-8">
      <div class="flex items-center">
        <Check class="h-6 w-6 text-green-600 mr-3" />
        <div>
          <h3 class="text-lg font-medium text-green-800">Event Submitted Successfully!</h3>
          <p class="text-green-700 mt-1">
            Your event has been submitted for review. You'll receive an email notification once it's approved.
          </p>
        </div>
      </div>
      <div class="mt-4 flex space-x-3">
        <button
          @click="resetForm"
          class="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors"
        >
          Submit Another Event
        </button>
        <router-link
          to="/dashboard"
          class="bg-white text-green-600 border border-green-600 px-4 py-2 rounded-md hover:bg-green-50 transition-colors"
        >
          View My Events
        </router-link>
      </div>
    </div>

    <!-- Form -->
    <form v-else @submit.prevent="handleSubmit" class="space-y-8">
      <!-- Error Display -->
      <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
        <div class="flex">
          <AlertCircle class="h-5 w-5 text-red-400 mr-3 mt-0.5" />
          <div>
            <h3 class="text-sm font-medium text-red-800">Submission Error</h3>
            <p class="text-sm text-red-700 mt-1">{{ error }}</p>
          </div>
        </div>
      </div>

      <!-- Basic Information -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-6">Basic Information</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Event Title -->
          <div class="md:col-span-2">
            <label for="title" class="block text-sm font-medium text-gray-700 mb-2">
              Event Title *
            </label>
            <input
              id="title"
              v-model="formData.title"
              type="text"
              required
              class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter your event title"
            />
          </div>
          
          <!-- Description -->
          <div class="md:col-span-2">
            <label for="description" class="block text-sm font-medium text-gray-700 mb-2">
              Description *
            </label>
            <textarea
              id="description"
              v-model="formData.description"
              rows="4"
              required
              class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              placeholder="Describe your event in detail..."
              maxlength="1000"
            ></textarea>
            <div class="text-sm text-gray-500 mt-1 text-right">
              {{ formData.description.length }}/1000
            </div>
          </div>
          
          <!-- Category -->
          <div>
            <label for="category" class="block text-sm font-medium text-gray-700 mb-2">
              Category *
            </label>
            <select
              id="category"
              v-model="formData.category_id"
              required
              class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select a category</option>
              <option
                v-for="category in categories"
                :key="category.id"
                :value="category.id"
              >
                {{ category.name }}
              </option>
            </select>
          </div>
          
          <!-- External URL -->
          <div>
            <label for="external_url" class="block text-sm font-medium text-gray-700 mb-2">
              Event Website/URL
            </label>
            <input
              id="external_url"
              v-model="formData.external_url"
              type="url"
              class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="https://example.com"
            />
          </div>
        </div>
      </div>

      <!-- Date & Time -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-6">Date & Time</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Date -->
          <div>
            <label for="date" class="block text-sm font-medium text-gray-700 mb-2">
              Event Date *
            </label>
            <input
              id="date"
              v-model="formData.date"
              type="date"
              required
              :min="minDate"
              class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <!-- Time -->
          <div>
            <label for="time" class="block text-sm font-medium text-gray-700 mb-2">
              Start Time *
            </label>
            <input
              id="time"
              v-model="formData.time"
              type="time"
              required
              class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      <!-- Location -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-6">Location</h2>
        
        <div class="space-y-6">
          <!-- Location Input -->
          <div>
            <label for="location" class="block text-sm font-medium text-gray-700 mb-2">
              Venue/Location *
            </label>
            <input
              id="location"
              v-model="formData.location"
              type="text"
              required
              class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter venue name or address"
              @input="handleLocationInput"
            />
            <p class="text-sm text-gray-500 mt-1">
              We'll automatically set the coordinates for map display.
            </p>
          </div>
          
          <!-- Manual Coordinates (Optional) -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label for="latitude" class="block text-sm font-medium text-gray-700 mb-2">
                Latitude (Optional)
              </label>
              <input
                id="latitude"
                v-model.number="formData.latitude"
                type="number"
                step="any"
                class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="1.2834"
              />
            </div>
            
            <div>
              <label for="longitude" class="block text-sm font-medium text-gray-700 mb-2">
                Longitude (Optional)
              </label>
              <input
                id="longitude"
                v-model.number="formData.longitude"
                type="number"
                step="any"
                class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="103.8607"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Additional Information -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-6">Additional Information</h2>
        
        <div class="space-y-6">
          <!-- Age Restrictions -->
          <div>
            <label for="age_restrictions" class="block text-sm font-medium text-gray-700 mb-2">
              Age Restrictions
            </label>
            <select
              id="age_restrictions"
              v-model="formData.age_restrictions"
              class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">No age restrictions</option>
              <option value="18+">18+ only</option>
              <option value="21+">21+ only</option>
              <option value="family_friendly">Family friendly</option>
              <option value="kids_only">Kids only</option>
            </select>
          </div>
          
          <!-- Tags -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Tags (Select all that apply)
            </label>
            <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
              <label
                v-for="tag in tags"
                :key="tag.id"
                class="flex items-center"
              >
                <input
                  v-model="formData.tag_ids"
                  :value="tag.id"
                  type="checkbox"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span class="ml-2 text-sm text-gray-700">{{ tag.name }}</span>
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- Terms and Submission -->
      <div class="bg-white rounded-lg shadow p-6">
        <div class="space-y-4">
          <!-- Terms Agreement -->
          <div class="flex items-start">
            <input
              id="terms"
              v-model="formData.agreeToTerms"
              type="checkbox"
              required
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded mt-1"
            />
            <label for="terms" class="ml-3 text-sm text-gray-700">
              I agree that the information provided is accurate and I have the right to submit this event. 
              I understand that all submissions are subject to review and approval.
            </label>
          </div>
          
          <!-- Review Notice -->
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div class="flex">
              <Info class="h-5 w-5 text-blue-400 mr-3 mt-0.5" />
              <div>
                <h4 class="text-sm font-medium text-blue-800">Review Process</h4>
                <p class="text-sm text-blue-700 mt-1">
                  Your event will be reviewed by our team within 24-48 hours. You'll receive an email notification 
                  once it's approved and published on the platform.
                </p>
              </div>
            </div>
          </div>
          
          <!-- Submit Button -->
          <div class="flex items-center justify-end space-x-4">
            <router-link
              to="/dashboard"
              class="px-6 py-3 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
            >
              Cancel
            </router-link>
            <button
              type="submit"
              :disabled="loading || !formData.agreeToTerms"
              class="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="loading" class="flex items-center">
                <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Submitting Event...
              </span>
              <span v-else>Submit Event for Review</span>
            </button>
          </div>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Check, AlertCircle, Info } from 'lucide-vue-next'
import { apiService } from '@/services/api'
import type { Category, Tag } from '@/types'

// State
const loading = ref(false)
const error = ref<string | null>(null)
const isSubmitted = ref(false)
const categories = ref<Category[]>([])
const tags = ref<Tag[]>([])

// Form data
const formData = ref({
  title: '',
  description: '',
  date: '',
  time: '',
  location: '',
  latitude: null as number | null,
  longitude: null as number | null,
  category_id: '',
  age_restrictions: '',
  external_url: '',
  tag_ids: [] as number[],
  agreeToTerms: false
})

// Computed
const minDate = computed(() => {
  const today = new Date()
  return today.toISOString().split('T')[0]
})

// Methods
async function loadFormData() {
  try {
    const [categoriesData, tagsData] = await Promise.all([
      apiService.getCategories(),
      apiService.getTags()
    ])
    
    categories.value = categoriesData
    tags.value = tagsData
  } catch (err: any) {
    console.error('Failed to load form data:', err)
  }
}

function handleLocationInput() {
  // In a real implementation, you might want to integrate with a geocoding service
  // to automatically set coordinates based on the location input
  console.log('Location input changed:', formData.value.location)
}

async function handleSubmit() {
  try {
    loading.value = true
    error.value = null
    
    // Prepare submission data
    const eventData = {
      title: formData.value.title,
      description: formData.value.description,
      date: formData.value.date,
      time: formData.value.time,
      location: formData.value.location,
      latitude: formData.value.latitude || 1.2834, // Default to Singapore center
      longitude: formData.value.longitude || 103.8607,
      category_id: parseInt(formData.value.category_id),
      age_restrictions: formData.value.age_restrictions || undefined,
      external_url: formData.value.external_url || undefined,
      tag_ids: formData.value.tag_ids
    }
    
    // Submit event
    await apiService.createEvent(eventData)
    
    isSubmitted.value = true
  } catch (err: any) {
    let errorMessage = 'Failed to submit event'
    if (err.response?.data?.detail) {
      const detail = err.response.data.detail
      if (Array.isArray(detail)) {
        errorMessage = detail[0]?.msg || errorMessage
      } else {
        errorMessage = detail
      }
    }
    
    error.value = errorMessage
  } finally {
    loading.value = false
  }
}

function resetForm() {
  formData.value = {
    title: '',
    description: '',
    date: '',
    time: '',
    location: '',
    latitude: null,
    longitude: null,
    category_id: '',
    age_restrictions: '',
    external_url: '',
    tag_ids: [],
    agreeToTerms: false
  }
  
  isSubmitted.value = false
  error.value = null
}

// Lifecycle
onMounted(() => {
  loadFormData()
})
</script>