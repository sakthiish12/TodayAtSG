<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import AppNavigation from '@/components/layout/AppNavigation.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

onMounted(() => {
  // Initialize auth state from localStorage
  authStore.initializeAuth()
})
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <AppNavigation />
    
    <main class="flex-1">
      <RouterView />
    </main>
    
    <AppFooter />
  </div>
</template>

<style scoped>
/* Additional custom styles can be added here */
</style>
