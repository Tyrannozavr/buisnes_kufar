<script setup lang="ts">
defineProps<{
	active: boolean
	loading?: boolean
}>()

defineEmits<{
	click: []
}>()
</script>

<template>
	<UButton
		:color="active ? 'success' : 'primary'"
		:variant="active ? 'soft' : 'solid'"
		:label="active ? 'Уже в избранном' : 'В избранное'"
		:loading="loading"
		class="cursor-pointer"
		@click="$emit('click')"
	/>
</template>
