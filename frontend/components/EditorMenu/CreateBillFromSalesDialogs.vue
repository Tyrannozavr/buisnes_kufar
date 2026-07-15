<script setup lang="ts">
import { useCreateBillFromSales } from "~/composables/useCreateBillFromSales"

/**
 * Модалки §3.1 «Создать счет» — общие для таблицы Продажи и вкладки «Счет» в редакторе.
 */
const {
	isNoContractModalOpen,
	isContractSelectModalOpen,
	contractSelectItems,
	selectedContractValue,
	isBusy,
	confirmCreateWithoutContract,
	confirmCreateWithSelectedContract,
	cancelDialogs,
} = useCreateBillFromSales()
</script>

<template>
	<UModal v-model:open="isNoContractModalOpen" title="Создать счёт">
		<template #body>
			<div class="flex flex-col gap-3">
				<p class="text-sm text-gray-600">
					С данным контрагентом нет договоров. Создать счёт без основания?
				</p>
				<div class="flex flex-col gap-2 sm:flex-row">
					<UButton
						label="Да"
						color="primary"
						class="w-full justify-center"
						:loading="isBusy"
						:disabled="isBusy"
						@click="confirmCreateWithoutContract"
					/>
					<UButton
						label="Нет"
						color="neutral"
						variant="subtle"
						class="w-full justify-center"
						:disabled="isBusy"
						@click="cancelDialogs"
					/>
				</div>
			</div>
		</template>
	</UModal>

	<UModal v-model:open="isContractSelectModalOpen" title="Создать счёт">
		<template #body>
			<div class="flex flex-col gap-3">
				<p class="text-sm text-gray-600">
					Выберите договор с данным покупателем или создайте счёт без основания.
				</p>
				<USelect
					:disabled="isBusy"
					:items="contractSelectItems"
					:model-value="selectedContractValue"
					placeholder="Выберите договор"
					@update:model-value="(value: string) => { selectedContractValue = value }"
				/>
				<div class="flex flex-col gap-2 sm:flex-row">
					<UButton
						label="Создать счёт"
						color="primary"
						class="w-full justify-center"
						:loading="isBusy"
						:disabled="isBusy || !selectedContractValue"
						@click="confirmCreateWithSelectedContract"
					/>
					<UButton
						label="Отмена"
						color="neutral"
						variant="subtle"
						class="w-full justify-center"
						:disabled="isBusy"
						@click="cancelDialogs"
					/>
				</div>
			</div>
		</template>
	</UModal>
</template>
