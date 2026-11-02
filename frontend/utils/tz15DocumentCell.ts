import type { Component, VNode } from 'vue'
import { h } from 'vue'

export const TZ15_CREATE_DOC_LABEL = 'Создать документ'
export const TZ15_TABLE_LINK_CLASS = 'text-sky-500 cursor-pointer text-left'

type ExtraLine = {
	label: string
	onClick: () => void
	tone?: 'muted' | 'default'
}

type RenderTz15DocCellOptions = {
	UButton: Component
	docLabel?: string | null
	/** Подписи документов (обычно одна сводная строка) */
	docLabels?: string[]
	/** Полный текст для title (договор / заявка / перевозчик) */
	docTitle?: string | null
	onView?: () => void
	onCreate?: () => void
	showCreate?: boolean
	createLabel?: string
	extraLines?: ExtraLine[]
}

/** Ячейка документа ТЗ_15: существующий документ + «Создать документ» (§8.2). */
export function renderTz15DocCell(options: RenderTz15DocCellOptions): VNode {
	const {
		UButton,
		docLabel,
		docLabels,
		docTitle,
		onView,
		onCreate,
		showCreate = true,
		createLabel = TZ15_CREATE_DOC_LABEL,
		extraLines = [],
	} = options

	const children: VNode[] = []
	const labels = docLabels?.length
		? docLabels
		: docLabel
			? [docLabel]
			: []

	for (const line of extraLines) {
		children.push(
			h(
				UButton,
				{
					color: 'neutral',
					variant: 'ghost',
					label: line.label,
					title: line.label,
					class: [
						TZ15_TABLE_LINK_CLASS,
						'whitespace-normal',
						line.tone === 'muted' ? 'text-neutral-500' : '',
					].filter(Boolean).join(' '),
					ui: { base: 'items-start cursor-pointer h-auto py-0.5 max-w-full' },
					onClick: line.onClick,
				},
			),
		)
	}

	for (const label of labels) {
		children.push(
			h(
				UButton,
				{
					color: 'neutral',
					variant: 'ghost',
					label,
					title: docTitle || label,
					class: `${TZ15_TABLE_LINK_CLASS} whitespace-normal break-words`,
					ui: { base: 'items-start cursor-pointer h-auto py-0.5 max-w-full' },
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
					label: createLabel,
					title: createLabel,
					class: `${TZ15_TABLE_LINK_CLASS} whitespace-normal`,
					ui: { base: 'items-start cursor-pointer h-auto py-0.5 max-w-full' },
					onClick: onCreate,
				},
			),
		)
	}

	return h(
		'div',
		{ class: 'flex flex-col items-start gap-0.5 py-1 min-w-[14rem] max-w-[22rem]' },
		children,
	)
}
