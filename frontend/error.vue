<script setup lang="ts">
import type { NuxtError } from '#app'

const props = defineProps<{
	error: NuxtError
}>()

const statusCode = computed(() => props.error?.statusCode || 500)
const title = computed(() => {
	if (statusCode.value === 404) return 'Страница не найдена'
	return 'Произошла ошибка'
})
const description = computed(() => {
	if (statusCode.value === 404) {
		return 'К сожалению, запрашиваемая страница не существует или была перемещена.'
	}
	return props.error?.message || 'Что-то пошло не так. Попробуйте обновить страницу.'
})

const goHome = () => clearError({ redirect: '/' })
</script>

<template>
	<UContainer>
		<div class="min-h-[60vh] flex flex-col items-center justify-center text-center py-12">
			<h1 class="text-6xl font-bold text-gray-900 mb-4">{{ statusCode }}</h1>
			<h2 class="text-2xl font-semibold text-gray-700 mb-6">{{ title }}</h2>
			<p class="text-gray-600 mb-8 max-w-md">
				{{ description }}
			</p>
			<div class="flex flex-col sm:flex-row gap-4">
				<UButton color="primary" size="lg" class="cursor-pointer" @click="goHome">
					Вернуться на главную
				</UButton>
				<UButton to="/catalog/products" color="neutral" size="lg" class="cursor-pointer">
					Перейти в каталог
				</UButton>
			</div>
		</div>
	</UContainer>
</template>
