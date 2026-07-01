<script setup lang="ts">
defineProps<{
	count: string | number
}>()
</script>

<template>
	<UBadge
		:label="count"
		color="primary"
		variant="solid"
		class="chat-unread-badge"
	/>
</template>

<style>
.chat-unread-badge {
	min-width: calc(1.125rem - 1mm) !important;
	height: calc(1.125rem - 1mm) !important;
	padding-left: calc(0.25rem - 0.5mm) !important;
	padding-right: calc(0.25rem - 0.5mm) !important;
	font-size: calc(0.6875rem - 1mm) !important;
	line-height: 1 !important;
	border-radius: 9999px !important;
	justify-content: center;
}
</style>
