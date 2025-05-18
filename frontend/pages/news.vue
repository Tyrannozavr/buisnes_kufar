<script setup lang="ts">
import {useNewsApi} from "~/api/news";
import type { NewsItem } from "~/types/news";

const { getAllNews } = useNewsApi();
const news = ref<NewsItem[]>([])

const {data: InitialData } = getAllNews()
news.value = InitialData.value ?? [];


</script>
<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">Новости</h1>

    <div class="space-y-8">

      <!-- Empty state -->
      <section v-if="!news || news.length === 0" class="bg-white rounded-lg p-6 shadow-sm">
        <p class="text-center text-gray-500">
          На данный момент новостей нет.
        </p>
      </section>

      <!-- News List -->
      <section v-else>
        <div class="space-y-6">
          <UCard
            v-for="item in news"
            :key="item.id"
            class="hover:shadow-lg transition-shadow"
          >
            <template #header>
              <h2 class="text-xl font-semibold">{{ item.title }}</h2>
              <p class="text-sm text-gray-500">{{ new Date(item.date).toLocaleDateString() }}</p>
            </template>

            <div class="space-y-4">
              <p class="text-gray-600">{{ item.content }}</p>
            </div>

            <template #footer>
              <div class="flex justify-end">
                <UButton
                  color="primary"
                  variant="ghost"
                  :to="`/news/${item.id}`"
                >
                  Читать полностью
                </UButton>
              </div>
            </template>
          </UCard>
        </div>
      </section>
    </div>
  </div>
</template>