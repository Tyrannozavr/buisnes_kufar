<script setup lang="ts">
import type { Review } from '~/types/review'

interface CompanyReviewsProps {
  reviews: Review[]
}

defineProps<CompanyReviewsProps>()
</script>

<template>
  <div class="mt-6">
    <UCard>
      <template #header>
        <div class="flex justify-between items-center">
          <h2 class="text-xl font-semibold">Отзывы о компании</h2>
          <UButton
            color="primary"
            variant="soft"
            to="/reviews/create"
          >
            Оставить отзыв
          </UButton>
        </div>
      </template>
      
      <div class="space-y-6">
        <div
          v-for="review in reviews"
          :key="review.id"
          class="p-4 bg-gray-50 rounded-lg"
        >
          <div class="flex justify-between items-start mb-4">
            <div>
              <h3 class="font-medium">{{ review.authorName }}</h3>
              <p class="text-sm text-gray-500">{{ review.date }}</p>
            </div>
            <div class="flex items-center">
              <UIcon
                v-for="i in 5"
                :key="i"
                :name="i <= review.rating ? 'i-heroicons-star-solid' : 'i-heroicons-star-outline'"
                class="text-yellow-400"
              />
            </div>
          </div>
          
          <p class="text-gray-600">{{ review.text }}</p>
          
          <div
            v-if="review.images && review.images.length > 0"
            class="mt-4 grid grid-cols-4 gap-2"
          >
            <img
              v-for="image in review.images"
              :key="image"
              :src="image"
              :alt="review.authorName"
              class="w-full h-24 object-cover rounded-lg"
            />
          </div>
          
          <div class="mt-4 flex justify-end space-x-2">
            <UButton
              color="neutral"
              variant="soft"
              size="xs"
              @click="() => {}"
            >
              Ответить
            </UButton>
            <UButton
              color="neutral"
              variant="soft"
              size="xs"
              @click="() => {}"
            >
              Пожаловаться
            </UButton>
          </div>
        </div>
        
        <div
          v-if="reviews.length === 0"
          class="text-center py-8"
        >
          <UIcon
            name="i-heroicons-chat-bubble-left-right"
            class="mx-auto h-12 w-12 text-gray-400"
          />
          <p class="mt-2 text-gray-500">Пока нет отзывов</p>
        </div>
      </div>
    </UCard>
  </div>
</template> 