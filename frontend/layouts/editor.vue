<template>
	<AppLayout>
		<div class="flex flex-row justify-between">

			<!-- template -->
			<div class="w-2/3 mr-5 p-3">
				<Editor @tabIndex="getTabs" @orderBlob="getOrderBlob">
					<slot />
				</Editor>
			</div>
			<!-- editor -->
			<div class="basis-1/3">
				<UCard variant="subtle" class="  top-26">

					<div class="flex flex-col justify-between gap-5">
							<div class="w-full">
								<UButton label="Заполнить данными" icon="i-lucide-file-input" class="w-full justify-center"/>
							</div>
							<div class="flex flex-col gap-2">
								<UButton label="Создать СЧЕТ на основании" color="neutral" variant="subtle" icon="i-lucide-file-plus"/>
								<UButton label="Создать ДОГОВОР ПОСТАВКИ на основании" color="neutral" variant="subtle" icon="i-lucide-file-plus"/>
								<UButton label="Создать Сопроводительные документы на основании" color="neutral" variant="subtle" icon="i-lucide-file-plus"/>
								<UButton label="Создать СЧЕТ-ФАКТУРУ на основании" color="neutral" variant="subtle" icon="i-lucide-file-plus"/>
							</div>
							<div class="flex flex-row justify-between">
								<UButton label="Поиск" icon="i-lucide-search" class="p-3"/>
								<UButton label="Печать" icon="i-lucide-printer" class="p-3"/>
								<UButton label="DOC" @click="downloadCurrentBlob(tabIndex, orderDocxBlob, billDocxBlob)" icon="i-lucide-dock" class="p-3"/>
								<UButton label="PDF" icon="i-lucide-dock" class="p-3"/>
							</div>
							<div class="flex flex-col gap-2">
								<UButton label="Редактировать" icon="i-lucide-file-pen" color="neutral" variant="subtle"/>
								<UButton label="Удалить данные" icon="i-lucide-trash-2" color="neutral" variant="subtle"/>
							</div>
							<div>
								<UButton label="Сохранить документ" icon="i-lucide-save" size="xl" class="w-full justify-center"/>
							</div>
						<div class="flex flex-col gap-2 text-center ">
							<p>Фото/Сканы документа</p>
							<UButton label="Выберите файл" icon="i-lucide-folder-search" color="neutral" variant="subtle" size="xl" class="justify-center"/>
						</div>
						<div class="flex flex-row justify-between">
							<UButton label="Отправить контрагенту и сохранить" size="xl" class="w-full justify-center"/>
							<!-- <UButton label="Сохранить"/> -->
						</div>
					</div>

				</UCard>
			</div>
		
	</div>
	</AppLayout>
</template>

<script setup lang="ts">
import AppLayout from '~/components/layout/AppLayout.vue';
import Editor from '~/pages/profile/contracts/editor.vue';
import { useDocxGenerator } from '~/composables/useDocxGenerator';

const {generateDocxOrder, downloadBlob} = useDocxGenerator()

let tabIndex: string
function getTabs(activeTab: string): void {
	tabIndex = activeTab
}

let orderDocxBlob: Blob
function getOrderBlob(blob: Blob): void {
	orderDocxBlob = blob
}

let billDocxBlob: Blob

const downloadCurrentBlob = (tabIndex: string, orderDocxBlob: Blob, billDocxBlob: Blob): void => {
	if (tabIndex === '0') {
		downloadBlob(orderDocxBlob, 'Order.docx')
	} else if (tabIndex === '1') {
		downloadBlob(billDocxBlob, 'Bill.docx')
	}
}



</script>

<style scoped>
/* div UButton {
	margin: 3px;
}
div {
	margin: 5px;
} */
</style>