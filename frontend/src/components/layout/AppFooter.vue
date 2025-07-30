<template>
  <footer class="bg-gray-900 text-white">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
        <!-- About Section -->
        <div class="col-span-1 lg:col-span-2">
          <div class="flex items-center space-x-2 mb-4">
            <div class="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <span class="text-white font-bold text-sm">T</span>
            </div>
            <span class="text-xl font-bold">TodayAtSG</span>
          </div>
          <p class="text-gray-300 mb-4 max-w-md">
            Discover amazing events happening in Singapore. From concerts and festivals to DJ events and kids activities, find your next experience with our interactive map and comprehensive event listings.
          </p>
          <div class="flex space-x-4">
            <a href="#" class="text-gray-300 hover:text-white transition-colors">
              <span class="sr-only">Facebook</span>
              <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
              </svg>
            </a>
            <a href="#" class="text-gray-300 hover:text-white transition-colors">
              <span class="sr-only">Instagram</span>
              <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12.017 0C5.396 0 .029 5.367.029 11.987c0 6.62 5.367 11.987 11.988 11.987c6.62 0 11.987-5.367 11.987-11.987C24.014 5.367 18.637.001 12.017.001zM8.449 16.988c-1.297 0-2.348-1.051-2.348-2.348c0-1.297 1.051-2.348 2.348-2.348c1.297 0 2.348 1.051 2.348 2.348C10.797 15.937 9.746 16.988 8.449 16.988z"/>
              </svg>
            </a>
            <a href="#" class="text-gray-300 hover:text-white transition-colors">
              <span class="sr-only">Twitter</span>
              <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
              </svg>
            </a>
          </div>
        </div>

        <!-- Quick Links -->
        <div>
          <h3 class="text-lg font-semibold mb-4">Quick Links</h3>
          <ul class="space-y-2">
            <li>
              <RouterLink to="/events" class="text-gray-300 hover:text-white transition-colors">
                Browse Events
              </RouterLink>
            </li>
            <li>
              <RouterLink to="/map" class="text-gray-300 hover:text-white transition-colors">
                Map View
              </RouterLink>
            </li>
            <li>
              <RouterLink to="/categories" class="text-gray-300 hover:text-white transition-colors">
                Categories
              </RouterLink>
            </li>
            <li>
              <RouterLink to="/submit-event" class="text-gray-300 hover:text-white transition-colors">
                Submit Event
              </RouterLink>
            </li>
          </ul>
        </div>

        <!-- Support -->
        <div>
          <h3 class="text-lg font-semibold mb-4">Support</h3>
          <ul class="space-y-2">
            <li>
              <RouterLink to="/help" class="text-gray-300 hover:text-white transition-colors">
                Help Center
              </RouterLink>
            </li>
            <li>
              <RouterLink to="/contact" class="text-gray-300 hover:text-white transition-colors">
                Contact Us
              </RouterLink>
            </li>
            <li>
              <RouterLink to="/faq" class="text-gray-300 hover:text-white transition-colors">
                FAQ
              </RouterLink>
            </li>
            <li>
              <a href="mailto:support@todayatsg.com" class="text-gray-300 hover:text-white transition-colors">
                support@todayatsg.com
              </a>
            </li>
          </ul>
        </div>
      </div>

      <!-- Bottom Section -->
      <div class="mt-8 pt-8 border-t border-gray-800">
        <div class="flex flex-col md:flex-row justify-between items-center">
          <div class="flex flex-col md:flex-row items-center space-y-2 md:space-y-0 md:space-x-6">
            <p class="text-gray-300 text-sm">
              © {{ currentYear }} TodayAtSG. All rights reserved.
            </p>
            <div class="flex space-x-6 text-sm">
              <RouterLink to="/privacy" class="text-gray-300 hover:text-white transition-colors">
                Privacy Policy
              </RouterLink>
              <RouterLink to="/terms" class="text-gray-300 hover:text-white transition-colors">
                Terms of Service
              </RouterLink>
              <RouterLink to="/cookies" class="text-gray-300 hover:text-white transition-colors">
                Cookie Policy
              </RouterLink>
            </div>
          </div>
          
          <div class="mt-4 md:mt-0">
            <p class="text-gray-400 text-sm">
              Made with ❤️ in Singapore
            </p>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

const currentYear = computed(() => new Date().getFullYear())
</script>