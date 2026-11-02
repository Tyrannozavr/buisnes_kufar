<template>
	<!-- Заказ / Счёт / Договор перевозки (§2): живой бланк с жёлтыми input -->
	<div
		v-if="activeTab === '0' || activeTab === '1' || activeTab === '5'"
		class="a4-background"
	>
		<div class="a4-pages">
			<div class="a4-page_container">
				<div ref="liveDocumentRef" class="a4-page_document">
					<slot />
				</div>
			</div>
		</div>
	</div>

	<div v-else>
		<div ref="slotContainerRef" class="a4-page_slot">
			<slot />
		</div>

		<div class="a4-background">
			<div class="a4-pages">
				<div ref="previewDocumentRef" class="a4-page_document">
					<vue-document-editor 
						v-model:content="htmlContent" 
						:editable="false" 
						:do_not_break="(element) => element.tagName === 'TABLE' || element.tagName === 'TR' || element.tagName === 'TD' || element.tagName === 'TH'"
						:overlay="coverLetterCheck && activeTab === '2' ? renderOverlay : undefined"
						:page_margins="'15mm 10mm 15mm 20mm'"
					/>
				</div>

			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
//Пришел к выводу, что наиболее оптимальный вариант - это использовать vue-document-editor для разделения страниц только длинных компонентов без сложной логики
//Первые два компонента иммитируют страницу а4, только не по высоте (будут всегда одностраничными)
import VueDocumentEditor from "vue-document-editor"
import { Editor } from "~/constants/keys"
import { TemplateElement } from "~/constants/keys"
import { usePdfGenerator } from "~/composables/usePdfGenerator"

const activeTab = useTypedState(Editor.ACTIVE_TAB, () => ref("0"))
const htmlContent = ref([""])
const slotContainerRef = ref<HTMLElement | null>(null)
const previewDocumentRef = ref<HTMLElement | null>(null)
const liveDocumentRef = ref<HTMLElement | null>(null)
const { replaceTextareasAndInputs } = usePdfGenerator()

//supply contract
const supplyContractHTML = useTypedState(TemplateElement.SUPPLY_CONTRACT)
const specificationHTML = useTypedState(TemplateElement.SPECIFICATION)
const coverLetterCheck = useTypedState(Editor.COVER_LETTER_CHECK)
const supplierDetailsCheck = useTypedState(Editor.SUPPLIER_DETAILS_CHECK)
const buyerDetailsCheck = useTypedState(Editor.BUYER_DETAILS_CHECK)
const supplyContractType = useTypedState(Editor.SUPPLY_CONTRACT_TYPE)
const supplyContractOfficialsSeller = useTypedState(Editor.SUPPLY_CONTRACT_OFFICIALS_SELLER, () => ref([]))
const supplyContractSlotRevision = useTypedState(Editor.SUPPLY_CONTRACT_SLOT_REVISION, () => ref(0))
const supplyContractPreviewElement = useTypedState(Editor.SUPPLY_CONTRACT_PREVIEW_ELEMENT, () => ref(null))
const carriageContractSlotRevision = useTypedState(Editor.CARRIAGE_CONTRACT_SLOT_REVISION, () => ref(0))
const isDisabled = useTypedState(Editor.IS_DISABLED)

const fillHtmlContentFromSlot = () => {
	if (!import.meta.client || !slotContainerRef.value) return

	// innerHTML не содержит .value у input/textarea — только span/div с текстом
	const cloneWithText = replaceTextareasAndInputs(slotContainerRef.value)
	htmlContent.value = [cloneWithText.innerHTML]
	cloneWithText.remove()
}

// Делаем зависимость от переменных, меняющих значения внутри слота
watch(
	[
		supplyContractHTML,
		specificationHTML,
		slotContainerRef,
		supplierDetailsCheck,
		buyerDetailsCheck,
		supplyContractType,
		supplyContractOfficialsSeller,
		supplyContractSlotRevision,
		carriageContractSlotRevision,
		isDisabled,
	],
	() => {
		// Используем nextTick, чтобы дождаться, когда Vue отрендерит компоненты в слоте
		nextTick(() => {
			fillHtmlContentFromSlot()
		})
	},
	{ deep: true, immediate: true }
)

watch(
	[activeTab, previewDocumentRef, liveDocumentRef, htmlContent],
	() => {
		if (activeTab.value === "2") {
			supplyContractPreviewElement.value = previewDocumentRef.value
			return
		}
		// Печать/поиск договора перевозки — с живого бланка
		if (activeTab.value === "5") {
			supplyContractPreviewElement.value = liveDocumentRef.value
			return
		}
		supplyContractPreviewElement.value = null
	},
	{ immediate: true, flush: "post" }
)

// overlay для колонтитула supply contract
const renderOverlay = (page: number, total: number) => `
	<div style="display:flex;flex-direction:column;height:100%;justify-content:flex-end;">
		<div style="display: flex; justify-content: space-around; position: relative; top: 7mm; text-align:center;font-size:12px;color: #666;margin-top: 10px;">
			<span>Поставщик:_______________</span>
			<span>Покупатель:_______________</span>
		</div>
	</div>
`
</script>

<style scoped>
.a4-page_slot {
	display: none;
	position: absolute;
	top: 0;
	left: -99999px;
	width: 100%;
	height: 100%;
	z-index: 1000;
}

.a4-background {
	--page-border: none;
	--page-box-shadow: none;
	--page-border-radius: 0;
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
