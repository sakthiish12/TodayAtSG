import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiService } from '@/services/api'
import type { Event, Category, Tag, EventFilters, PaginatedResponse } from '@/types'

export const useEventsStore = defineStore('events', () => {
  // State
  const events = ref<Event[]>([])
  const categories = ref<Category[]>([])
  const tags = ref<Tag[]>([])
  const currentEvent = ref<Event | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const pagination = ref({
    total: 0,
    page: 1,
    per_page: 20,
    pages: 0
  })
  const filters = ref<EventFilters>({})

  // Getters
  const eventsWithCategories = computed(() => {
    return events.value.map(event => ({
      ...event,
      category: categories.value.find(cat => cat.id === event.category_id)
    }))
  })

  const eventsByCategory = computed(() => {
    const grouped: Record<string, Event[]> = {}
    eventsWithCategories.value.forEach(event => {
      const categoryName = event.category?.name || 'Uncategorized'
      if (!grouped[categoryName]) {
        grouped[categoryName] = []
      }
      grouped[categoryName].push(event)
    })
    return grouped
  })

  const upcomingEvents = computed(() => {
    const now = new Date()
    return eventsWithCategories.value
      .filter(event => new Date(event.date) >= now)
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
  })

  const featuredEvents = computed(() => {
    return eventsWithCategories.value
      .filter(event => event.average_rating && event.average_rating >= 4)
      .sort((a, b) => (b.average_rating || 0) - (a.average_rating || 0))
      .slice(0, 6)
  })

  // Actions
  async function fetchEvents(newFilters?: EventFilters) {
    try {
      loading.value = true
      error.value = null
      
      if (newFilters) {
        filters.value = { ...filters.value, ...newFilters }
      }
      
      const response: PaginatedResponse<Event> = await apiService.getEvents(filters.value)
      
      events.value = response.data
      pagination.value = {
        total: response.total,
        page: response.page,
        per_page: response.per_page,
        pages: response.pages
      }
      
      return response
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch events'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchEvent(id: number) {
    try {
      loading.value = true
      error.value = null
      
      const event = await apiService.getEvent(id)
      currentEvent.value = event
      
      return event
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch event'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createEvent(eventData: Partial<Event>) {
    try {
      loading.value = true
      error.value = null
      
      const event = await apiService.createEvent(eventData)
      events.value.unshift(event)
      
      return event
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to create event'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateEvent(id: number, eventData: Partial<Event>) {
    try {
      loading.value = true
      error.value = null
      
      const event = await apiService.updateEvent(id, eventData)
      const index = events.value.findIndex(e => e.id === id)
      if (index !== -1) {
        events.value[index] = event
      }
      
      if (currentEvent.value?.id === id) {
        currentEvent.value = event
      }
      
      return event
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to update event'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteEvent(id: number) {
    try {
      loading.value = true
      error.value = null
      
      await apiService.deleteEvent(id)
      events.value = events.value.filter(e => e.id !== id)
      
      if (currentEvent.value?.id === id) {
        currentEvent.value = null
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to delete event'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchCategories() {
    try {
      const response = await apiService.getCategories()
      categories.value = response
      return response
    } catch (err: any) {
      console.error('Failed to fetch categories:', err)
      return []
    }
  }

  async function fetchTags() {
    try {
      const response = await apiService.getTags()
      tags.value = response
      return response
    } catch (err: any) {
      console.error('Failed to fetch tags:', err)
      return []
    }
  }

  function updateFilters(newFilters: Partial<EventFilters>) {
    filters.value = { ...filters.value, ...newFilters }
  }

  function clearFilters() {
    filters.value = {}
  }

  function clearError() {
    error.value = null
  }

  return {
    // State
    events,
    categories,
    tags,
    currentEvent,
    loading,
    error,
    pagination,
    filters,
    
    // Getters
    eventsWithCategories,
    eventsByCategory,
    upcomingEvents,
    featuredEvents,
    
    // Actions
    fetchEvents,
    fetchEvent,
    createEvent,
    updateEvent,
    deleteEvent,
    fetchCategories,
    fetchTags,
    updateFilters,
    clearFilters,
    clearError
  }
})