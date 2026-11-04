<script setup lang="ts">
import { useCreateTransportDocumentFromSales } from '~/composables/useCreateTransportDocumentFromSales'

/**
 * Модалки §1.3 «Создать документ» (колонка «Договор перевозки»).
 */
const {
	isTypeModalOpen,
	isAlertModalOpen,
	isPickerModalOpen,
	isBusy,
	selectedDocType,
	typeRadioItems,
	alertTitle,
	alertMessage,
	pickerShowContracts,
	carrierSelectItems,
	contractSelectItems,
	selectedCarrierId,
	selectedContractId,
	pickerCanChoose,
	pickerCanBind,
	confirmTypeSelect,
	confirmAlert,
	onCarrierChange,
	bindSelectedContract,
	createNewFromPicker,
	backFromPickerToTypes,
	closeAll,
} = useCreateTransportDocumentFromSales()

const modalUi = {
	overlay: 'fixed inset-0 bg-black/50',
	content: 'bg-white ring ring-default shadow-lg',
}
</script>

<template>
	<UModal
		v-model:open="isTypeModalOpen"
		title="Выберите тип документа"
		:ui="modalUi"
	>
		<template #body>
			<div class="flex flex-col gap-3">
				<URadioGroup
					v-model="selectedDocType"
					:items="typeRadioItems"
					:disabled="isBusy"
					orientation="vertical"
				/>
				<div class="flex flex-col gap-2 sm:flex-row">
					<UButton
						label="Создать"
						color="primary"
						class="w-full justify-center"
						:loading="isBusy"
						:disabled="isBusy || !selectedDocType"
						@click="confirmTypeSelect"
					/>
					<UButton
						label="Отмена"
						color="neutral"
						variant="subtle"
						class="w-full justify-center"
						@click="closeAll"
					/>
				</div>
			</div>
		</template>
	</UModal>

	<UModal
		v-model:open="isAlertModalOpen"
		:title="alertTitle || 'Внимание'"
		:ui="modalUi"
	>
		<template #body>
			<div class="flex flex-col gap-3">
				<p class="text-sm text-gray-600">
					{{ alertMessage }}
				</p>
				<UButton
					label="Понятно"
					color="primary"
					class="w-full justify-center"
					@click="confirmAlert"
				/>
			</div>
		</template>
	</UModal>

	<UModal
		v-model:open="isPickerModalOpen"
		:title="selectedDocType ? 'Выбор организации' : 'Договор перевозки'"
		:ui="modalUi"
	>
		<template #body>
			<div class="flex flex-col gap-3">
				<p class="text-sm text-gray-600">
					Слева — организации из раздела «Перевозчики».
					<template v-if="pickerShowContracts">
						Справа — договоры выбранной организации.
					</template>
					<template v-else>
						Список старых договоров не показывается (договор-заявка).
					</template>
				</p>
				<div
					class="grid gap-3"
					:class="pickerShowContracts ? 'sm:grid-cols-2' : 'sm:grid-cols-1'"
				>
					<div class="flex flex-col gap-1 min-w-0">
						<span class="text-xs font-medium text-gray-500">Организации</span>
						<USelect
							:disabled="isBusy"
							:items="carrierSelectItems"
							:model-value="selectedCarrierId ? String(selectedCarrierId) : undefined"
							placeholder="Выберите организацию"
							class="w-full"
							@update:model-value="onCarrierChange"
						/>
					</div>
					<div v-if="pickerShowContracts" class="flex flex-col gap-1 min-w-0">
						<span class="text-xs font-medium text-gray-500">Договоры</span>
						<USelect
							:disabled="isBusy || !selectedCarrierId"
							:items="contractSelectItems"
							:model-value="selectedContractId ? String(selectedContractId) : undefined"
							placeholder="Выберите договор"
							class="w-full"
							@update:model-value="(v: string) => { selectedContractId = v ? Number(v) : undefined }"
						/>
						<p
							v-if="selectedCarrierId && !contractSelectItems.length && !isBusy"
							class="text-xs text-amber-700"
						>
							Договоров пока нет — нажмите «Создать новый».
						</p>
						<p
							v-else-if="isBusy && selectedCarrierId"
							class="text-xs text-gray-500"
						>
							Загрузка договоров…
						</p>
					</div>
				</div>
				<div class="flex flex-col gap-2 sm:flex-row sm:flex-wrap">
					<UButton
						v-if="pickerShowContracts"
						label="Выбор"
						color="primary"
						class="w-full justify-center sm:w-auto sm:flex-1"
						:loading="isBusy"
						:disabled="!pickerCanBind"
						@click="bindSelectedContract"
					/>
					<UButton
						label="Создать новый"
						color="neutral"
						variant="subtle"
						class="w-full justify-center sm:w-auto sm:flex-1"
						:loading="isBusy"
						:disabled="!pickerCanChoose"
						@click="createNewFromPicker"
					/>
					<UButton
						label="Назад"
						color="neutral"
						variant="ghost"
						class="w-full justify-center sm:w-auto"
						@click="backFromPickerToTypes"
					/>
					<UButton
						label="Закрыть"
						color="neutral"
						variant="ghost"
						class="w-full justify-center sm:w-auto"
						@click="closeAll"
					/>
				</div>
			</div>
		</template>
	</UModal>
</template>
