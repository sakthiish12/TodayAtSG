<template>
  <div class="bg-white rounded-lg shadow-md p-4">
    <!-- Filter header -->
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-900">Filters</h3>
      <button
        v-if="hasActiveFilters"
        @click="clearAllFilters"
        class="text-sm text-red-600 hover:text-red-700 transition-colors"
      >
        Clear All
      </button>
    </div>
    
    <!-- Search input -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Search Events
      </label>
      <div class="relative">
        <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search by title, description, or location..."
          class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          @input="debouncedSearch"
        />
        <button
          v-if="searchQuery"
          @click="clearSearch"
          class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
        >
          <X class="w-4 h-4" />
        </button>
      </div>
    </div>
    
    <!-- Date filters -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Date Range
      </label>
      
      <!-- Quick date filters -->
      <div class="grid grid-cols-2 gap-2 mb-3">
        <button
          v-for="quickFilter in quickDateFilters"
          :key="quickFilter.value"
          @click="setQuickDateFilter(quickFilter.value)"
          class="px-3 py-2 text-sm rounded-lg border transition-colors"
          :class="[
            selectedQuickDate === quickFilter.value
              ? 'bg-blue-600 text-white border-blue-600'
              : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
          ]"
        >
          {{ quickFilter.label }}
        </button>
      </div>
      
      <!-- Custom date range -->
      <div class="grid grid-cols-2 gap-2">
        <div>
          <label class="block text-xs text-gray-500 mb-1">From</label>
          <input
            v-model="dateFrom"
            type="date"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            @change="updateDateFilters"
          />
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-1">To</label>
          <input
            v-model="dateTo"
            type="date"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            @change="updateDateFilters"
          />
        </div>
      </div>
    </div>
    
    <!-- Categories filter -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Categories
      </label>
      <div class="space-y-2 max-h-40 overflow-y-auto">
        <label
          v-for="category in categories"
          :key="category.id"
          class="flex items-center cursor-pointer"
        >
          <input
            :value="category.id"
            v-model="selectedCategories"
            type="checkbox"
            class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            @change="updateCategoryFilters"
          />
          <span class="ml-2 text-sm text-gray-700">
            {{ category.name }}
          </span>
          <span 
            class="ml-auto text-xs text-gray-500"
            v-if="getCategoryCount(category.id)"
          >
            {{ getCategoryCount(category.id) }}
          </span>
        </label>
      </div>
    </div>
    
    <!-- Tags filter -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Tags
      </label>
      <div class="relative mb-2">
        <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          v-model="tagSearch"
          type="text"
          placeholder="Search tags..."
          class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>
      <div class="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
        <button
          v-for="tag in filteredTags"
          :key="tag.id"
          @click="toggleTag(tag.id)"
          class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium transition-colors"
          :class="[
            selectedTags.includes(tag.id)
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          ]"
        >
          {{ tag.name }}
          <X
            v-if="selectedTags.includes(tag.id)"
            class="w-3 h-3 ml-1"
          />
        </button>
      </div>
    </div>
    
    <!-- Location filter -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Location
      </label>
      
      <!-- Distance filter -->
      <div class="mb-3">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm text-gray-700">Distance from me</span>
          <span class="text-sm font-medium text-blue-600">
            {{ distance === 50 ? '50+ km' : `${distance} km` }}
          </span>
        </div>
        <input
          v-model="distance"
          type="range"
          min="1"
          max="50"
          step="1"
          class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          :class="{ 'opacity-50 cursor-not-allowed': !userLocation }"
          :disabled="!userLocation"
          @input="updateLocationFilters"
        />
        <div class="flex justify-between text-xs text-gray-500 mt-1">
          <span>1km</span>
          <span>50km+</span>
        </div>
      </div>
      
      <!-- Location search -->
      <div class="relative">
        <MapPin class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          v-model="locationSearch"
          type="text"
          placeholder="Search by location..."
          class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          @input="debouncedLocationSearch"
        />
        <button
          v-if="locationSearch"
          @click="clearLocationSearch"
          class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
        >
          <X class="w-4 h-4" />
        </button>
      </div>
    </div>
    
    <!-- Age restrictions filter -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Age Restrictions
      </label>
      <select
        v-model="ageRestriction"
        class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        @change="updateAgeFilter"
      >
        <option value="">All ages</option>
        <option value="18+">18+ only</option>
        <option value="21+">21+ only</option>
        <option value="Family friendly">Family friendly</option>
        <option value="Kids only">Kids only</option>
      </select>
    </div>
    
    <!-- Apply filters button (mobile) -->
    <div class="md:hidden">
      <button
        @click="$emit('apply')"
        class="w-full bg-blue-600 text-white px-4 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
      >
        Apply Filters
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { 
  Search, 
  X, 
  MapPin 
} from 'lucide-vue-next'
import { useEventsStore } from '@/stores/events'
import { useMapStore } from '@/stores/map'
import { useDebounceFn } from '@vueuse/core'
import type { EventFilters } from '@/types'

const emit = defineEmits<{
  filtersChanged: [filters: EventFilters]
  apply: []
}>()

// Stores
const eventsStore = useEventsStore()
const mapStore = useMapStore()
const { categories, tags, eventsWithCategories } = storeToRefs(eventsStore)
const { userLocation } = storeToRefs(mapStore)

// State
const searchQuery = ref('')
const selectedCategories = ref<number[]>([])
const selectedTags = ref<number[]>([])
const dateFrom = ref('')
const dateTo = ref('')
const selectedQuickDate = ref('')
const distance = ref(10)
const locationSearch = ref('')
const ageRestriction = ref('')
const tagSearch = ref('')

// Quick date filter options
const quickDateFilters = ref([
  { label: 'Today', value: 'today' },
  { label: 'Tomorrow', value: 'tomorrow' },
  { label: 'This Week', value: 'this_week' },
  { label: 'This Month', value: 'this_month' }
])

// Computed
const filteredTags = computed(() => {
  if (!tagSearch.value) return tags.value
  
  return tags.value.filter(tag =>
    tag.name.toLowerCase().includes(tagSearch.value.toLowerCase())
  )
})

const hasActiveFilters = computed(() => {
  return searchQuery.value ||
         selectedCategories.value.length > 0 ||
         selectedTags.value.length > 0 ||
         dateFrom.value ||
         dateTo.value ||
         locationSearch.value ||
         ageRestriction.value ||
         (userLocation.value && distance.value < 50)
})

// Debounced functions
const debouncedSearch = useDebounceFn(() => {
  updateFilters()
}, 500)

const debouncedLocationSearch = useDebounceFn(() => {
  updateFilters()
}, 500)

// Methods
function updateFilters() {
  const filters: EventFilters = {}
  
  if (searchQuery.value) {
    filters.search = searchQuery.value
  }
  
  if (selectedCategories.value.length > 0) {
    filters.category_ids = selectedCategories.value
  }
  
  if (selectedTags.value.length > 0) {
    filters.tag_ids = selectedTags.value
  }
  
  if (dateFrom.value) {
    filters.date_from = dateFrom.value
  }
  
  if (dateTo.value) {
    filters.date_to = dateTo.value
  }
  
  if (locationSearch.value) {
    filters.location = locationSearch.value
  }
  
  if (userLocation.value && distance.value < 50) {
    filters.latitude = userLocation.value.lat
    filters.longitude = userLocation.value.lng
    filters.radius = distance.value
  }
  
  if (ageRestriction.value) {
    filters.age_restriction = ageRestriction.value
  }
  
  emit('filtersChanged', filters)
}

function setQuickDateFilter(value: string) {
  selectedQuickDate.value = value
  
  const today = new Date()
  const tomorrow = new Date(today)
  tomorrow.setDate(tomorrow.getDate() + 1)
  
  switch (value) {
    case 'today':
      dateFrom.value = today.toISOString().split('T')[0]
      dateTo.value = today.toISOString().split('T')[0]
      break
    case 'tomorrow':
      dateFrom.value = tomorrow.toISOString().split('T')[0]
      dateTo.value = tomorrow.toISOString().split('T')[0]
      break
    case 'this_week':
      const weekStart = new Date(today)
      weekStart.setDate(today.getDate() - today.getDay())
      const weekEnd = new Date(weekStart)
      weekEnd.setDate(weekStart.getDate() + 6)
      dateFrom.value = weekStart.toISOString().split('T')[0]
      dateTo.value = weekEnd.toISOString().split('T')[0]
      break
    case 'this_month':
      const monthStart = new Date(today.getFullYear(), today.getMonth(), 1)
      const monthEnd = new Date(today.getFullYear(), today.getMonth() + 1, 0)
      dateFrom.value = monthStart.toISOString().split('T')[0]
      dateTo.value = monthEnd.toISOString().split('T')[0]
      break
  }
  
  updateFilters()
}

function updateDateFilters() {
  selectedQuickDate.value = ''
  updateFilters()
}

function updateCategoryFilters() {
  updateFilters()
}

function updateLocationFilters() {
  updateFilters()
}

function updateAgeFilter() {
  updateFilters()
}

function toggleTag(tagId: number) {
  const index = selectedTags.value.indexOf(tagId)
  if (index > -1) {
    selectedTags.value.splice(index, 1)
  } else {
    selectedTags.value.push(tagId)
  }
  updateFilters()
}

function getCategoryCount(categoryId: number): number {
  return eventsWithCategories.value.filter(event => 
    event.category_id === categoryId
  ).length
}

function clearSearch() {
  searchQuery.value = ''
  updateFilters()
}

function clearLocationSearch() {
  locationSearch.value = ''
  updateFilters()
}

function clearAllFilters() {
  searchQuery.value = ''
  selectedCategories.value = []
  selectedTags.value = []
  dateFrom.value = ''
  dateTo.value = ''
  selectedQuickDate.value = ''
  distance.value = 10
  locationSearch.value = ''
  ageRestriction.value = ''
  tagSearch.value = ''
  
  updateFilters()
}

// Load initial data
onMounted(async () => {
  await eventsStore.fetchCategories()
  await eventsStore.fetchTags()
})
</script>