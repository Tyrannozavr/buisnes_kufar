<template>
	<div class="a4-background">
		<div v-if="isDev" class="a4-dev-badge">
			Страниц: {{ pageCount }}
		</div>
		<!-- Страницы, куда телепортируем контент -->
		<div ref="documentRoot" class="a4-pages">
			<div v-for="n in pageCount" :key="n" class="a4-page_container">
				<div class="a4-page_document" :ref="(el) => setPageBody(el, n - 1)"></div>
			</div>
		</div>

		<!-- Измерительный контейнер (offscreen), сюда временно телепортируем контент для вычисления разбиения -->
		<div ref="measureRoot" class="a4-measure" aria-hidden="true">
			<div class="a4-page_container">
				<div class="a4-page_document" ref="measureBody"></div>
			</div>
		</div>

		<!-- Важно: разбиение делаем через Teleport, чтобы Vue продолжал управлять DOM (реактивность "живая") -->
		<div v-if="isMounted" class="a4-teleports">
			<Teleport v-for="(node, i) in getSlotNodes()" :key="i" :to="getTeleportTarget(i)">
				<div class="a4-item" :ref="(el) => setItemEl(el, i)">
					<VNodeRenderer :node="node" />
				</div>
			</Teleport>
		</div>
	</div>

</template>

<script setup lang="ts">
import { Comment, Teleport, defineComponent, nextTick, onBeforeUnmount, onMounted, ref, useSlots } from 'vue'
import type { VNode } from 'vue'

const documentRoot = ref<HTMLElement | null>(null)
const measureRoot = ref<HTMLElement | null>(null)
const measureBody = ref<HTMLElement | null>(null)

const pageBodies = ref<HTMLElement[]>([])
const pageCount = ref(1)
const isDev = import.meta.env.DEV
const isMounted = ref(false)
const isInteracting = ref(false)
let pendingPaginate = false
let suppressMutations = false

// Рендерер VNode (нужен, чтобы безопасно рисовать VNode из slots.default())
const VNodeRenderer = defineComponent({
	name: 'VNodeRenderer',
	props: {
		node: { type: Object as () => VNode, required: true },
	},
	setup(props) {
		return () => props.node
	},
})

function setPageBody(el: Element | null, idx: number) {
	if (!el) return
	pageBodies.value[idx] = el as HTMLElement
}

const slots = useSlots()

const getSlotNodes = (): VNode[] => {
	const raw = (slots.default?.() ?? []).filter((n) => n && n.type !== Comment) as VNode[]

	// Частый кейс: в слоте один wrapper (например <div>), а делить нужно его детей.
	// Осторожно: разворачиваем только если есть массив детей.
	if (raw.length === 1) {
		const only = raw[0] as any
		const children = only?.children
		if (Array.isArray(children) && children.length) {
			return children as VNode[]
		}
	}

	return raw
}

// Куда телепортировать каждый item (индекс -> номер страницы)
const itemToPage = ref<number[]>([])

const itemEls = ref<(HTMLElement | null)[]>([])
function setItemEl(el: Element | null, idx: number) {
	itemEls.value[idx] = (el as HTMLElement) || null
}

const getAvailableHeight = (body: HTMLElement | null) => {
	if (!body) return 0
	const container = body.parentElement as HTMLElement | null
	if (!container) return 0
	const cs = window.getComputedStyle(container)
	const pt = Number.parseFloat(cs.paddingTop || '0') || 0
	const pb = Number.parseFloat(cs.paddingBottom || '0') || 0
	return container.getBoundingClientRect().height - pt - pb
}

let scheduled = false
const schedulePaginate = () => {
	// Во время редактирования не трогаем DOM: иначе фокус/ввод "ломаются".
	if (hasFocusInsideDocument()) {
		pendingPaginate = true
		return
	}
	if (scheduled) return
	scheduled = true
	requestAnimationFrame(() => {
		scheduled = false
		void paginate()
	})
}

const hasFocusInsideDocument = () => {
	const root = documentRoot.value
	if (!root) return false
	const active = document.activeElement
	return !!active && root.contains(active)
}

async function paginate() {
	if (isPaginating) return
	if (hasFocusInsideDocument()) {
		pendingPaginate = true
		return
	}
	isPaginating = true
	try {
		suppressMutations = true
		const nodes = getSlotNodes()
		if (!nodes.length) return
		if (!measureBody.value) return

		// 1) Переводим в режим измерения: все элементы телепортируются в measureBody
		itemToPage.value = new Array(nodes.length).fill(-1)
		await nextTick()
		await nextTick()

		const maxH = getAvailableHeight(measureBody.value)
		if (!maxH) return

		const els = itemEls.value.slice(0, nodes.length).filter(Boolean) as HTMLElement[]
		if (els.length !== nodes.length) return

		// 2) Считаем разбиение по высоте (индексы -> страницы)
		const pageFor: number[] = new Array(nodes.length).fill(0)
		let currentPage = 0
		let currentH = 0

		for (let i = 0; i < els.length; i++) {
			const el = els[i]
			const h = el.getBoundingClientRect().height
			const safeH = Number.isFinite(h) && h > 0 ? h : 1

			if (i === 0 || currentH + safeH <= maxH) {
				pageFor[i] = currentPage
				currentH += safeH
			} else {
				currentPage += 1
				pageFor[i] = currentPage
				currentH = safeH
			}
		}

		const newPageCount = Math.max(1, currentPage + 1)
		if (pageCount.value !== newPageCount) {
			pageCount.value = newPageCount
			await nextTick()
		}

		// 3) Переводим в режим отображения: телепортируем в соответствующие pageBodies
		itemToPage.value = pageFor
		await nextTick()
	} finally {
		isPaginating = false
		// Дадим DOM успокоиться, чтобы MutationObserver не зацикливал перепагинацию
		setTimeout(() => {
			suppressMutations = false
		}, 50)
	}
}

let isPaginating = false
let mutationObserver: MutationObserver | null = null

onMounted(async () => {
	isMounted.value = true

	await nextTick()
	await paginate()

	// Если меняется структура документа (например, добавили строки в таблицу) — перепагинируем.
	mutationObserver = new MutationObserver(() => {
		if (isPaginating || suppressMutations) return
		schedulePaginate()
	})
	if (documentRoot.value) {
		mutationObserver.observe(documentRoot.value, { subtree: true, childList: true })
		// Фокус внутри документа = пользователь редактирует => не дергаем пагинацию
		documentRoot.value.addEventListener(
			'focusin',
			() => {
				isInteracting.value = true
			},
			true
		)
		documentRoot.value.addEventListener(
			'focusout',
			() => {
				// На blur проверяем: если фокуса внутри больше нет — можно перепагинировать
				setTimeout(() => {
					isInteracting.value = hasFocusInsideDocument()
					if (!isInteracting.value && pendingPaginate) {
						pendingPaginate = false
						schedulePaginate()
					}
				}, 0)
			},
			true
		)
	}
	window.addEventListener('resize', schedulePaginate)
})

onBeforeUnmount(() => {
	mutationObserver?.disconnect()
	window.removeEventListener('resize', schedulePaginate)
})

const getTeleportTarget = (idx: number) => {
	// Пока измеряем (itemToPage = -1) или если страница ещё не готова — рендерим в measureBody.
	const pageIdx = itemToPage.value[idx]
	const body = pageIdx >= 0 ? pageBodies.value[pageIdx] : null
	return body ?? measureBody.value ?? document.body
}

defineExpose({
	getDocumentEl: () => documentRoot.value,
})
</script>

<style scoped>
.a4-background {
	background-color: #e0e0e0;
	padding: 20px;
	position: relative;
}

.a4-dev-badge {
	position: sticky;
	top: 8px;
	z-index: 5;
	display: inline-block;
	padding: 6px 10px;
	margin: 0 auto 12px;
	background: rgba(0, 0, 0, 0.75);
	color: #fff;
	border-radius: 8px;
	font-size: 12px;
	width: fit-content;
}

.a4-pages {
	display: flex;
	flex-direction: column;
	gap: 20px;
}

.a4-page_container {
	height: 297mm;
	width: 210mm;
	background: white;
	margin: 0 auto;
	padding: 10mm;
	box-sizing: border-box;
	box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
	overflow: hidden;
}

.a4-page_document {
	font-size: 14px;
	font-family: serif;
}

.a4-measure {
	position: absolute;
	left: -99999px;
	top: 0;
	visibility: hidden; /* сохраняет layout для измерений */
}

.a4-item {
	/* предотвращаем margin-collapse дочерних блоков, чтобы высота измерялась корректно */
	display: flow-root;
}
</style>