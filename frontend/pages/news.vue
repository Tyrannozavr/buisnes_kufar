<script setup lang="ts">
import {useNewsApi} from "~/api/news";

const {getAllNews} = useNewsApi();

const {data: news, pending, error} = await getAllNews()
</script>

<template>
  <div class="container mx-auto">
    <h1 class="text-3xl font-bold mb-8">Новости</h1>

    <div class="space-y-8">
      <!-- Loading state -->
      <section v-if="pending" class="bg-white rounded-lg p-6 shadow-sm">
        <p class="text-center text-gray-500">
          Загрузка новостей...
        </p>
      </section>

      <!-- Error state -->
      <section v-else-if="error" class="bg-white rounded-lg p-6 shadow-sm">
        <p class="text-center text-red-500">
          Произошла ошибка при загрузке новостей. Пожалуйста, попробуйте позже.
        </p>
      </section>

      <!-- Empty state -->
      <section v-else-if="!news || news.length === 0" class="bg-white rounded-lg p-6 shadow-sm">
        <p class="text-center text-gray-500">
          На данный момент новостей нет.
        </p>
      </section>

      <!-- News List -->
      <section v-else>
        <div class="space-y-6">
          <NewsCard
            v-for="item in news"
            :key="item.id"
            :item="item"
          />
        </div>
      </section>
    </div>
  </div>
</template>