import type { Component, VNode } from 'vue'
import { h } from 'vue'

export const TZ15_CREATE_DOC_LABEL = 'Создать документ'
export const TZ15_TABLE_LINK_CLASS = 'text-sky-500 text-wrap cursor-pointer'

type ExtraLine = {
	label: string
	onClick: () => void
}

type RenderTz15DocCellOptions = {
	UButton: Component
	docLabel?: string | null
	onView?: () => void
	onCreate?: () => void
	showCreate?: boolean
	extraLines?: ExtraLine[]
}

/** Ячейка документа ТЗ_15: существующий документ + «Создать документ» (§8.2). */
export function renderTz15DocCell(options: RenderTz15DocCellOptions): VNode {
	const {
		UButton,
		docLabel,
		onView,
		onCreate,
		showCreate = true,
		extraLines = [],
	} = options

	const children: VNode[] = []

	for (const line of extraLines) {
		children.push(
			h(
				UButton,
				{
					color: 'neutral',
					variant: 'ghost',
					label: line.label,
					class: TZ15_TABLE_LINK_CLASS,
					ui: { base: 'items-start cursor-pointer h-auto py-0.5' },
					onClick: line.onClick,
				},
			),
		)
	}

	if (docLabel) {
		children.push(
			h(
				UButton,
				{
					color: 'neutral',
					variant: 'ghost',
					label: docLabel,
					class: TZ15_TABLE_LINK_CLASS,
					ui: { base: 'items-start cursor-pointer h-auto py-0.5' },
					onClick: onView,
				},
			),
		)
	}

	if (showCreate && onCreate) {
		children.push(
			h(
				UButton,
				{
					color: 'neutral',
					variant: 'ghost',
					label: TZ15_CREATE_DOC_LABEL,
					class: TZ15_TABLE_LINK_CLASS,
					ui: { base: 'items-start cursor-pointer h-auto py-0.5' },
					onClick: onCreate,
				},
			),
		)
	}

	return h('div', { class: 'flex flex-col items-start gap-0.5 py-1' }, children)
}
