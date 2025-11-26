<template>
	<div class="a4-background">
		<div class="a4-page_container">
			<div class="a4-page_document">
				<slot></slot>
			</div>
		</div>
	</div>

</template>

<!-- <script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
	element: HTMLElement | null
}>()

const element: Ref<HTMLElement | null> = ref(null)
const pages: Ref<HTMLElement[][]> = ref([])

if (props.element) {
	element.value = props.element
}

//split elments on pages
const splitElements = (pageElement: HTMLElement): HTMLElement[][] => {
	const pages: HTMLElement[][] = []
	const contentMaxHeight = 1016;
	let currentPage: HTMLElement[] = []
	let currentHeight = 0

	if (pageElement.children[0]) {
		const childrenList = Array.from(pageElement.children?.[0].children) as HTMLElement[]

		childrenList.forEach((el: HTMLElement) => {
			const elHeight = el.offsetHeight

			if (elHeight + currentHeight <= contentMaxHeight) {
				currentHeight += elHeight
				currentPage.push(el)
			} else {
				pages.push(currentPage)
				currentPage = [el]
				currentHeight = elHeight
			}
		})

		pages.push(currentPage)
	}
	return pages
}

//observer
const elementHeight = ref(0)

watch(element, (el) => {
	if (!el) return

	const observer = new ResizeObserver(entries => {
		if (entries[0]) {
			elementHeight.value = entries[0].contentRect.height
		}
	})
	observer.observe(el)

	onUnmounted(() => observer.disconnect())
}, { immediate: true, deep: true })


watch(elementHeight, (height) => {
	console.log('Высота изменилась:', height)
	const pagesQuantity = Math.ceil((elementHeight.value) / 1046)
	console.log('Количество необходимых страниц: ', pagesQuantity)
})

</script> -->

<style scoped>
.a4-background {
	background-color: #e0e0e0;
	padding: 20px;
}

.a4-background .a4-page_container {
	height: 297mm;
	width: 210mm;
	background: white;
	margin: 0 auto;
	padding: 10mm;
	box-sizing: border-box;
	box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.a4-page_container .a4-page_document {
	font-size: 14px;
	font-family: serif;
}
</style>