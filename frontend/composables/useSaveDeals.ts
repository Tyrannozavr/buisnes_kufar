import { Editor } from "~/constants/keys"
import { useTypedState } from "~/composables/useTypedState"

//Хранит функцию для завершения сохранения сделок в store
let savingResolve: (() => void) | null = null

/**
 * Начало и завершение сохранения сделок в store 
 */
export const useSaveDeals = () => {
	// Состояние сохранения сделок в store (true - сохранение в процессе, false - сохранение завершено)
	const saveState = useTypedState(Editor.SAVE_STATE, () => ref(false))

	/**
	 * Завершение сохранения сделок.
	 * Вызывается в компоненте после успешного сохранения сделок в store.
	 */
	const completeSave = (): void => {
		if (!savingResolve) return

		savingResolve()
		savingResolve = null
		saveState.value = false
	}

	/**
	 * Начало сохранения сделок в store.
	 * Вызывается в меню редактора при нажатии на кнопку сохранения.
	 */
	const startSave = async (): Promise<void> => {
		return new Promise((resolve) => {
			savingResolve = resolve
			saveState.value = true
		})
	}

	return {
		startSave,
		completeSave,
		saveState
	}
}
