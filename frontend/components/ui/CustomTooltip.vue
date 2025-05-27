<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  text: string
}>()

const isVisible = ref(false)

const showInfo = () => {
  isVisible.value = true
}

const hideInfo = () => {
  isVisible.value = false
}
</script>

<template>
  <div class="info-container">
    <div
      class="info-trigger"
      @mouseenter="showInfo"
      @mouseleave="hideInfo"
    >
      <slot />
    </div>
    <Transition name="fade">
      <div
        v-show="isVisible"
        class="info-content"
      >
        {{ text }}
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.info-container {
  position: relative;
  display: inline-block;
}

.info-trigger {
  display: inline-flex;
  align-items: center;
}

.info-content {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  background-color: #1f2937;
  color: white;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  line-height: 1.25rem;
  width: max-content;
  max-width: 20rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  margin-top: 0.5rem;
  white-space: normal;
  text-align: center;
}

.info-content::before {
  content: '';
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 6px solid transparent;
  border-bottom-color: #1f2937;
}

/* Анимации */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translate(-50%, -10px);
}
</style> 
