<template>
  <div class="bg-white rounded-lg shadow-md overflow-hidden animate-pulse">
    <!-- Event image placeholder -->
    <div class="h-48 sm:h-40 md:h-48 bg-gray-200"></div>
    
    <!-- Event content -->
    <div class="p-4">
      <!-- Category and time skeleton -->
      <div class="flex items-center justify-between mb-2">
        <div class="h-6 bg-gray-200 rounded-full w-20"></div>
        <div class="h-4 bg-gray-200 rounded w-16"></div>
      </div>
      
      <!-- Event title skeleton -->
      <div class="space-y-2 mb-3">
        <div class="h-6 bg-gray-200 rounded w-full"></div>
        <div class="h-6 bg-gray-200 rounded w-3/4"></div>
      </div>
      
      <!-- Event description skeleton -->
      <div class="space-y-2 mb-3">
        <div class="h-4 bg-gray-200 rounded w-full"></div>
        <div class="h-4 bg-gray-200 rounded w-5/6"></div>
      </div>
      
      <!-- Location skeleton -->
      <div class="flex items-center mb-3">
        <div class="h-4 w-4 bg-gray-200 rounded mr-2"></div>
        <div class="h-4 bg-gray-200 rounded flex-1"></div>
      </div>
      
      <!-- Rating skeleton -->
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center">
          <div class="flex space-x-1 mr-2">
            <div v-for="i in 5" :key="i" class="h-4 w-4 bg-gray-200 rounded"></div>
          </div>
          <div class="h-4 bg-gray-200 rounded w-8"></div>
        </div>
        <div class="h-4 bg-gray-200 rounded w-16"></div>
      </div>
      
      <!-- Tags skeleton -->
      <div class="flex flex-wrap gap-1 mb-3">
        <div class="h-6 bg-gray-200 rounded-full w-16"></div>
        <div class="h-6 bg-gray-200 rounded-full w-20"></div>
        <div class="h-6 bg-gray-200 rounded-full w-12"></div>
      </div>
      
      <!-- Action buttons skeleton -->
      <div class="flex items-center justify-between pt-2 border-t border-gray-100">
        <div class="h-4 bg-gray-200 rounded w-20"></div>
        <div class="flex items-center gap-2">
          <div class="h-8 w-8 bg-gray-200 rounded"></div>
          <div class="h-8 w-8 bg-gray-200 rounded"></div>
          <div class="h-8 w-8 bg-gray-200 rounded"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// No props needed for skeleton
</script>