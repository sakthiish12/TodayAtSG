import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/map',
      name: 'map',
      component: () => import('../views/MapView.vue'),
      meta: {
        title: 'Event Map - TodayAtSG',
        description: 'Discover events in Singapore on an interactive map'
      }
    },
    {
      path: '/events',
      name: 'events',
      component: () => import('../views/EventListView.vue'),
      meta: {
        title: 'Events - TodayAtSG',
        description: 'Browse all events happening in Singapore'
      }
    },
    {
      path: '/events/:id',
      name: 'event-detail',
      component: () => import('../views/EventDetailView.vue'),
      props: true,
      meta: {
        title: 'Event Details - TodayAtSG',
        description: 'View detailed information about this event'
      }
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
      meta: {
        title: 'About - TodayAtSG',
        description: 'Learn more about TodayAtSG'
      }
    },
    // Authentication routes
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
      meta: {
        title: 'Profile - TodayAtSG',
        description: 'Manage your account settings',
        requiresAuth: true
      }
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue'),
      meta: {
        title: 'Dashboard - TodayAtSG',
        description: 'Your personal dashboard',
        requiresAuth: true
      }
    },
    {
      path: '/submit-event',
      name: 'submit-event',
      component: () => import('../views/SubmitEventView.vue'),
      meta: {
        title: 'Submit Event - TodayAtSG',
        description: 'Submit a new event',
        requiresAuth: true,
        requiresOrganizer: true
      }
    },
    {
      path: '/reset-password',
      name: 'reset-password',
      component: () => import('../views/PasswordResetView.vue'),
      meta: {
        title: 'Reset Password - TodayAtSG',
        description: 'Reset your password',
        requiresGuest: true
      }
    },
    {
      // Redirect old paths
      path: '/event/:id',
      redirect: to => `/events/${to.params.id}`
    },
    {
      // 404 catch-all
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('../views/NotFoundView.vue'),
      meta: {
        title: 'Page Not Found - TodayAtSG'
      }
    }
  ],
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Initialize auth if not already done
  if (!authStore.user && localStorage.getItem('access_token')) {
    authStore.initializeAuth()
    // Try to get current user to validate token
    try {
      await authStore.getCurrentUser()
    } catch (error) {
      // Token is invalid, logout
      await authStore.logout()
    }
  }
  
  // Set page title
  if (to.meta.title) {
    document.title = to.meta.title as string
  }
  
  // Set meta description
  if (to.meta.description) {
    const metaDescription = document.querySelector('meta[name="description"]')
    if (metaDescription) {
      metaDescription.setAttribute('content', to.meta.description as string)
    }
  }
  
  // Check authentication requirements
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // Store the intended destination
    sessionStorage.setItem('redirectAfterLogin', to.fullPath)
    next('/')
    return
  }
  
  // Check if route requires guest (not authenticated)
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next('/')
    return
  }
  
  // Check if route requires event organizer
  if (to.meta.requiresOrganizer && !authStore.isEventOrganizer) {
    next('/')
    return
  }
  
  next()
})

export default router
