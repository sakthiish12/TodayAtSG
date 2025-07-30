<template>
  <div
    class="animate-pulse"
    :class="[
      rounded && 'rounded-lg',
      className
    ]"
  >
    <div
      class="bg-gray-200"
      :class="[
        rounded && 'rounded-lg',
        `h-${height}`,
        width ? `w-${width}` : 'w-full'
      ]"
      :style="customStyle"
    ></div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  height?: string
  width?: string
  rounded?: boolean
  className?: string
  customStyle?: Record<string, string>
}

withDefaults(defineProps<Props>(), {
  height: '4',
  width: '',
  rounded: true,
  className: '',
  customStyle: () => ({})
})
</script>