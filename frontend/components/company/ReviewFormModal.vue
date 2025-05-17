<script setup lang="ts">
const props = defineProps<{
  isOpen: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'submit', data: { rating: number; text: string }): void
}>()

const rating = ref(0)
const text = ref('')

const handleSubmit = () => {
  if (rating.value && text.value.trim()) {
    emit('submit', {
      rating: rating.value,
      text: text.value.trim()
    })
    // Reset form
    rating.value = 0
    text.value = ''
  }
}

// Watch for modal close to reset form
watch(() => props.isOpen, (newValue) => {
  if (!newValue) {
    rating.value = 0
    text.value = ''
  }
})
</script>

<template>
  <UModal
    :open="isOpen"
    :outside-close="true"
    @close="emit('close')"
  >
    <template #content>
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold">Оставить отзыв</h3>
            <UButton
              color="neutral"
              variant="ghost"
              icon="i-heroicons-x-mark"
              @click="emit('close')"
            />
          </div>
        </template>

        <div class="space-y-4">
          <!-- Rating -->
          <UFormField label="Оценка" class="space-y-2">
            <div class="flex items-center gap-1">
              <UIcon
                v-for="i in 5"
                :key="i"
                :name="i <= rating ? 'i-heroicons-star-solid' : 'i-heroicons-star'"
                class="text-yellow-400 w-8 h-8 cursor-pointer"
                @click="rating = i"
              />
            </div>
          </UFormField>

          <!-- Review text -->
          <div class="space-y-2">
            <UFormField label="Текст отзыва">
              <UTextarea
                  class="w-full"
                  v-model="text"
                  placeholder="Расскажите о вашем опыте..."
                  :rows="4"
              />
            </UFormField>

          </div>
        </div>

        <template #footer>
          <div class="flex justify-end gap-2">
            <UButton
              color="neutral"
              variant="soft"
              @click="emit('close')"
            >
              Отмена
            </UButton>
            <UButton
              color="primary"
              :disabled="!rating || !text.trim()"
              @click="handleSubmit"
            >
              Отправить
            </UButton>
          </div>
        </template>
      </UCard>
    </template>
  </UModal>
</template>