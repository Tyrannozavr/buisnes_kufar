type FavoriteToggleOptions = {
	/** Лёгкий список id или полные объекты с id. */
	list: () => Promise<Array<{ id: number }> | { ids: number[] }>
	add: (id: number) => Promise<unknown>
	remove: (id: number) => Promise<unknown>
	addedTitle?: string
	removedTitle?: string
}

const toIdSet = (payload: Array<{ id: number }> | { ids: number[] }) => {
	if (Array.isArray(payload)) return new Set(payload.map(item => item.id))
	return new Set(payload.ids || [])
}

/** Общий тоггл избранного (ТС / заявки): оптимистичный UI + add/remove. */
export const useFavoriteToggle = (options: FavoriteToggleOptions) => {
	const toast = useToast()
	const favoriteIds = ref<Set<number>>(new Set())
	/** Только защита от даблклика — без спиннера на кнопке. */
	const inFlight = ref<Set<number>>(new Set())
	const pendingId = ref<number | null>(null)

	const isFavorite = (id: number) => favoriteIds.value.has(id)

	const loadFavoriteIds = async () => {
		try {
			favoriteIds.value = toIdSet(await options.list())
		} catch {
			// не блокируем основной экран
		}
	}

	const toggleFavorite = async (id: number) => {
		if (inFlight.value.has(id)) return
		const wasFavorite = isFavorite(id)

		const optimistic = new Set(favoriteIds.value)
		if (wasFavorite) optimistic.delete(id)
		else optimistic.add(id)
		favoriteIds.value = optimistic
		inFlight.value = new Set([...inFlight.value, id])

		try {
			if (wasFavorite) {
				await options.remove(id)
				toast.add({ title: options.removedTitle || 'Убрано из избранного', color: 'neutral' })
			} else {
				await options.add(id)
				toast.add({ title: options.addedTitle || 'Добавлено в избранное', color: 'success' })
			}
		} catch (e: any) {
			const reverted = new Set(favoriteIds.value)
			if (wasFavorite) reverted.add(id)
			else reverted.delete(id)
			favoriteIds.value = reverted
			toast.add({
				title: wasFavorite ? 'Не удалось убрать из избранного' : 'Не удалось добавить в избранное',
				description: e?.data?.detail || e?.message,
				color: 'error',
			})
		} finally {
			const next = new Set(inFlight.value)
			next.delete(id)
			inFlight.value = next
		}
	}

	return {
		favoriteIds,
		pendingId,
		isFavorite,
		loadFavoriteIds,
		toggleFavorite,
	}
}
