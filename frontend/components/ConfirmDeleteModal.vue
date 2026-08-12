<script setup lang="ts">
const open = defineModel<boolean>('open', { default: false })

withDefaults(
	defineProps<{
		title?: string
		message?: string
		confirmLabel?: string
		cancelLabel?: string
		loading?: boolean
	}>(),
	{
		title: 'Подтверждение удаления',
		message: 'Точно хотите удалить? Это действие нельзя отменить.',
		confirmLabel: 'Удалить',
		cancelLabel: 'Отмена',
		loading: false,
	},
)

const emit = defineEmits<{
	confirm: []
	cancel: []
}>()

const onCancel = () => {
	open.value = false
	emit('cancel')
}

const onConfirm = () => {
	emit('confirm')
}
</script>

<template>
	<UModal v-model:open="open" :title="title">
		<template #body>
			<div class="space-y-4 p-1 sm:p-2">
				<p class="text-gray-600 whitespace-pre-line">
					{{ message }}
				</p>
				<div class="flex justify-end gap-2">
					<UButton
						color="neutral"
						variant="outline"
						:disabled="loading"
						:label="cancelLabel"
						@click="onCancel"
					/>
					<UButton
						color="error"
						:loading="loading"
						:label="confirmLabel"
						@click="onConfirm"
					/>
				</div>
			</div>
		</template>
	</UModal>
</template>
