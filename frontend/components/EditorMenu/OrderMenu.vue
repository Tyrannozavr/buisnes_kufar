<template>
	<div class="flex flex-col gap-2">
		<UButton label="СЧЕТ на основании" color="neutral" variant="subtle" icon="i-lucide-file-plus"
			:disabled="activeButtons" @click="inDevelopment()" />
		<UButton label="ДОГОВОР ПОСТАВКИ на основании" color="neutral" variant="subtle" icon="i-lucide-file-plus"
			:disabled="activeButtons" @click="inDevelopment()" />
		<UButton label="Сопроводительные документы на основании" color="neutral" variant="subtle" icon="i-lucide-file-plus"
			:disabled="activeButtons" @click="inDevelopment()" />
		<UButton label="СЧЕТ-ФАКТУРУ на основании" color="neutral" variant="subtle" icon="i-lucide-file-plus"
			:disabled="activeButtons" @click="inDevelopment()" />
	</div>
</template>

<script setup lang="ts">
defineProps<{
	activeButtons: boolean
	inDevelopment: () => any
}>()
</script>

<style scoped></style>