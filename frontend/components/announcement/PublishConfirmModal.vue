<script setup lang="ts">
defineProps<{
  open: boolean
  saving: boolean
  notifyOptions: {
    notify: boolean
    partners: boolean
    customers: boolean
    suppliers: boolean
  }
}>()

const emit = defineEmits<{
  close: []
  confirm: []
}>()
</script>

<template>
  <UModal :open="open" :ui="{ width: 'sm:max-w-md' }" @close="emit('close')">
    <template #content>
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900">Подтверждение публикации</h3>
            <UButton
                color="neutral"
                variant="ghost"
                icon="i-heroicons-x-mark"
                class="-my-1"
                @click="emit('close')"
            />
          </div>
        </template>

        <div class="py-4">
          <p class="text-gray-700">
            Вы уверены, что хотите опубликовать это объявление? После публикации оно станет доступно всем пользователям.
          </p>

          <div v-if="notifyOptions.notify" class="mt-4 p-3 bg-gray-50 rounded-lg">
            <p class="font-medium text-gray-700 mb-2">Будут отправлены уведомления:</p>
            <ul class="list-disc pl-5 text-sm text-gray-600">
              <li v-if="notifyOptions.partners">Партнерам</li>
              <li v-if="notifyOptions.customers">Покупателям</li>
              <li v-if="notifyOptions.suppliers">Поставщикам</li>
            </ul>
          </div>
        </div>

        <template #footer>
          <div class="flex justify-end gap-3">
            <UButton
                color="neutral"
                variant="outline"
                @click="emit('close')"
            >
              Отмена
            </UButton>
            <UButton
                color="success"
                :loading="saving"
                @click="emit('confirm')"
            >
              Опубликовать
            </UButton>
          </div>
        </template>
      </UCard>
    </template>
  </UModal>
</template>