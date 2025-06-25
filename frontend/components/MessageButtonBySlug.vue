<script setup lang="ts">
import { useUserStore } from '~/stores/user'
import { navigateToChatBySlug } from '~/composables/chat'
import { computed } from 'vue'

interface Props {
  companySlug: string
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
  // Сравниваем по slug или по названию компании
  return props.companySlug === userStore.companySlug || 
         (props.companyName && props.companyName === userStore.companyName)
})

// Показываем кнопку только если пользователь аутентифицирован и это не его компания
const shouldShowButton = computed(() => {
  return userStore.isAuthenticated && !isOwnCompany.value
})

const handleMessageClick = async () => {
  await navigateToChatBySlug(props.companySlug)
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