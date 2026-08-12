/**
 * Enter в полях формы / модалки = клик по основной кнопке (Сохранить / Добавить / …).
 * Textarea и открытые выпадающие списки не перехватываем.
 */
function isMultilineField(el: EventTarget | null): boolean {
	if (!(el instanceof HTMLElement)) return false
	if (el.tagName === 'TEXTAREA') return true
	if (el.isContentEditable) return true
	return false
}

function isOpenPicker(el: EventTarget | null): boolean {
	if (!(el instanceof Element)) return false
	if (el.closest('[role="listbox"]')) return true
	if (el.closest('[role="menu"]')) return true
	if (el.closest('[data-reka-popper-content-wrapper]')) return true
	const expanded = el.closest('[aria-expanded="true"]')
	if (expanded && expanded !== el.closest('form')) return true
	return false
}

const PRIMARY_LABELS = [
	'сохранить',
	'добавить',
	'создать',
	'отправить',
	'применить',
	'далее',
	'найти',
	'войти',
	'зарегистрироваться',
	'подтвердить',
	'готово',
]

const CANCEL_LABELS = ['отмена', 'отменить', 'закрыть', 'назад', 'удалить']

function buttonLabel(btn: HTMLElement): string {
	return (btn.getAttribute('aria-label') || btn.textContent || '').trim().toLowerCase().replace(/\s+/g, ' ')
}

function findPrimaryButton(root: ParentNode): HTMLElement | null {
	const marked = root.querySelector(
		'button[data-form-primary]:not([disabled]), [data-form-primary] button:not([disabled])',
	) as HTMLElement | null
	if (marked) return marked

	const submit = root.querySelector('button[type="submit"]:not([disabled])') as HTMLElement | null
	if (submit) return submit

	const buttons = Array.from(root.querySelectorAll('button:not([disabled])')) as HTMLElement[]
	const matches = buttons.filter((btn) => {
		const text = buttonLabel(btn)
		if (!text) return false
		if (CANCEL_LABELS.some((c) => text.includes(c))) return false
		return PRIMARY_LABELS.some((l) => text.includes(l))
	})
	return matches.length ? matches[matches.length - 1] : null
}

function trySubmitFrom(target: HTMLElement): boolean {
	const form = target.closest('form')
	if (form instanceof HTMLFormElement) {
		if (typeof form.requestSubmit === 'function') form.requestSubmit()
		else form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }))
		return true
	}

	const dialog = target.closest('[role="dialog"]')
	if (dialog) {
		const btn = findPrimaryButton(dialog)
		if (btn) {
			btn.click()
			return true
		}
	}

	return false
}

export default defineNuxtPlugin(() => {
	if (!import.meta.client) return

	const onKeydown = (event: KeyboardEvent) => {
		if (event.key !== 'Enter' || event.defaultPrevented || event.isComposing) return
		if (event.altKey) return
		// Ctrl/Cmd+Enter в textarea — тоже сохранить
		const target = event.target
		if (isMultilineField(target) && !event.ctrlKey && !event.metaKey) return
		if (isOpenPicker(target)) return
		if (!(target instanceof HTMLElement)) return

		if (trySubmitFrom(target)) {
			event.preventDefault()
			event.stopPropagation()
		}
	}

	document.addEventListener('keydown', onKeydown, true)
})
