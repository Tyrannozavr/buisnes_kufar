<script setup lang="ts">
import type { Review } from '~/types/review'
import ReviewFormModal from './ReviewFormModal.vue'

const props = defineProps<{
  reviews: Review[]
}>()

const emit = defineEmits<{
  (e: 'submit-review', data: { rating: number; text: string }): void
}>()

const showReviewForm = ref(false)

const openReviewForm = () => {
  showReviewForm.value = true
}

const closeReviewForm = () => {
  showReviewForm.value = false
}

const handleSubmitReview = (data: { rating: number; text: string }) => {
  emit('submit-review', data)
  closeReviewForm()
}
</script>

<template>
  <div class="mt-6">
    <UCard>
      <template #header>
        <div class="flex justify-between items-center">
          <h2 class="text-xl font-semibold">Отзывы</h2>
          <UButton
            color="primary"
            variant="soft"
            @click="openReviewForm"
          >
            Оставить отзыв
          </UButton>
        </div>
      </template>

      <div class="space-y-4">
        <div
          v-for="review in reviews"
          :key="review.id"
          class="border-b pb-4 last:border-b-0 last:pb-0"
        >
          <div class="flex justify-between items-start mb-2">
            <div>
              <h3 class="font-medium">{{ review.userName }}</h3>
              <p class="text-sm text-gray-500">{{ review.date }}</p>
            </div>
            <div class="flex items-center gap-1">
              <UIcon
                v-for="i in 5"
                :key="i"
                :name="i <= review.rating ? 'i-heroicons-star-solid' : 'i-heroicons-star'"
                class="text-yellow-400"
              />
            </div>
          </div>
          <p class="text-gray-700">{{ review.text }}</p>
          <div
            v-if="review.images?.length"
            class="mt-2 flex gap-2"
          >
            <NuxtImg
              v-for="image in review.images"
              :key="image"
              :src="image"
              :alt="review.userName"
              class="w-20 h-20 object-cover rounded"
            />
          </div>
        </div>
      </div>
    </UCard>

    <ReviewFormModal
      :is-open="showReviewForm"
      @close="closeReviewForm"
      @submit="handleSubmitReview"
    />
  </div>
</template> 