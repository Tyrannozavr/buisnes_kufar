/**
 * Общая логика модалки «Точно хотите удалить?».
 * В шаблоне: <ConfirmDeleteModal v-model:open="deleteOpen" ... @confirm="confirmDelete" />
 */
export function useConfirmDelete() {
	const deleteOpen = ref(false)
	const deleteLoading = ref(false)
	const deleteTitle = ref('Подтверждение удаления')
	const deleteMessage = ref('Точно хотите удалить? Это действие нельзя отменить.')
	const deleteConfirmLabel = ref('Удалить')

	let pending: (() => void | Promise<void>) | null = null

	const askDelete = (options: {
		message?: string
		title?: string
		confirmLabel?: string
		onConfirm: () => void | Promise<void>
	}) => {
		deleteTitle.value = options.title ?? 'Подтверждение удаления'
		deleteMessage.value = options.message ?? 'Точно хотите удалить? Это действие нельзя отменить.'
		deleteConfirmLabel.value = options.confirmLabel ?? 'Удалить'
		pending = options.onConfirm
		deleteOpen.value = true
	}

	const confirmDelete = async () => {
		if (!pending) {
			deleteOpen.value = false
			return
		}
		deleteLoading.value = true
		try {
			await pending()
			deleteOpen.value = false
			pending = null
		} finally {
			deleteLoading.value = false
		}
	}

	const cancelDelete = () => {
		deleteOpen.value = false
		pending = null
	}

	return {
		deleteOpen,
		deleteLoading,
		deleteTitle,
		deleteMessage,
		deleteConfirmLabel,
		askDelete,
		confirmDelete,
		cancelDelete,
	}
}
