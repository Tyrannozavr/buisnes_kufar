<template>
	<div v-if="activeTab === '0' || activeTab === '1'" class="a4-background">
		<div  class="a4-pages">
			<div class="a4-page_container">
				<div class="a4-page_document">
					<slot />
				</div>
			</div>
		</div>
	</div> 

		<div v-else >
			<div ref="slotContainerRef" class="a4-page_slot">
				<slot />
			</div>

			<div class="a4-background">
				<div class="a4-pages">
						<div class="a4-page_document">
							<vue-document-editor v-model:content="htmlContent" />
						</div>
					</div>
				</div>
			</div>
		
</template>

<script setup lang="ts">
//Пришел к выводу, что наиболее оптимальный вариант - это использовать vue-document-editor для разделения страниц только длинных компонентов без сложной логики 
//Первые два компонента иммитируют страницу а4, только не по высоте (будут всегда одностраничными)
import VueDocumentEditor from 'vue-document-editor'
import { Editor } from '~/constants/keys'

const activeTab = useTypedState(Editor.ACTIVE_TAB, () => ref('0'))
const htmlContent = ref([''])
const slotContainerRef = ref<HTMLElement | null>(null)

	
const fillHtmlContentFromSlot = () => {
	if (!slotContainerRef.value) return
	
	htmlContent.value = [slotContainerRef.value.innerHTML]
}

onMounted(() => {
	fillHtmlContentFromSlot()
	console.log('htmlContent', htmlContent.value)
	console.dir(slotContainerRef.value)
})
</script>

<style scoped>
:root {
  --page-background: #d1d1d1; /* Pages background */
  --page-box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); /* Pages box-shadow */
  --page-border: none; /* Pages border */
  --page-border-radius: none; /* Pages border-radius */
}

.a4-page_slot {
	display: none;
	position: absolute;
	top: 0;
	left:-99999px;
	width: 100%;
	height: 100%;
	z-index: 1000;
}

.a4-background {
	background-color: #d1d1d1;
	position: relative;
}

.a4-pages {
	display: flex;
	flex-direction: column;
	gap: 20px;
}

.a4-page_container {
	max-height: auto;
	min-height: 297mm;
	width: 210mm;
	background: white;
	margin: 20px;
	padding: 10mm;
	box-sizing: border-box;
	box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
	overflow: hidden;
}

.a4-page_document {
	font-size: 14px;
	font-family: serif;
}

</style>