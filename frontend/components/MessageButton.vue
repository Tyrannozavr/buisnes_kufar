<script setup lang="ts">
import { useUserStore } from '~/stores/user'
import { navigateToChatById } from '~/composables/chat'
import { computed } from 'vue'

interface Props {
  companyId: number
  companyName?: string
  variant?: 'soft' | 'ghost' | 'solid'
  size?: 'sm' | 'md' | 'lg'
  showIcon?: boolean
  customText?: string
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'soft',
  size: 'sm',
  showIcon: true,
  customText: 'Написать'
})

const userStore = useUserStore()

// Проверяем, что пользователь не смотрит на свою компанию
const isOwnCompany = computed(() => {
  if (!userStore.isAuthenticated) return false
  // Сравниваем по ID или по названию компании
  return props.companyId === userStore.companyId || 
         (props.companyName && props.companyName === userStore.companyName)
})

// Показываем кнопку только если пользователь аутентифицирован и это не его компания
const shouldShowButton = computed(() => {
  return userStore.isAuthenticated && !isOwnCompany.value
})

const handleMessageClick = async () => {
  await navigateToChatById(props.companyId)
}
</script>

<template>
  <UButton
    v-if="shouldShowButton"
    color="neutral"
    :variant="variant"
    :size="size"
    :icon="showIcon ? 'i-heroicons-envelope' : undefined"
    @click="handleMessageClick"
  >
    {{ customText }}
  </UButton>
</template> 