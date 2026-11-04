<script setup lang="ts">
import { useStrictExpeditionBlank } from '~/composables/useStrictExpeditionBlank'
import {
	STRICT_EXPEDITION_TITLES,
	TRANSPORT_MODES,
	type StrictExpeditionDocType,
} from '~/utils/strictExpeditionDefaults'

const props = defineProps<{ docType: StrictExpeditionDocType }>()

const {
	documentId,
	payload,
	loading,
	saving,
	dialogOpen,
	currentDeal,
	fillFromLk,
	openDialog,
	applyDialog,
	setClientFromRole,
	listBuyerReceivingAddresses,
} = useStrictExpeditionBlank()

const title = computed(() => STRICT_EXPEDITION_TITLES[props.docType])
const destinationOptions = ref<string[]>([])
const clientRole = ref<'seller' | 'buyer'>('seller')

watch(dialogOpen, async (open) => {
	if (!open) return
	destinationOptions.value = await listBuyerReceivingAddresses()
	const src = payload.value.client.source
	if (src === 'buyer' || src === 'seller') clientRole.value = src
})

watch(clientRole, (role) => {
	setClientFromRole(role)
})

const fillDisabled = computed(() => {
	if (!documentId.value) return 'Документ не выбран'
	if (loading.value) return 'Идёт загрузка…'
	return ''
})
</script>

<template>
	<div class="flex flex-col gap-3">
		<p class="text-sm font-semibold text-center">{{ title }}</p>
		<p class="text-xs text-neutral-500 text-center">
			Строгий бланк: значения только через диалог / «Заполнить данными»
		</p>

		<UTooltip :text="fillDisabled" :disabled="!fillDisabled">
			<span class="block w-full" :class="{ 'cursor-not-allowed': fillDisabled }">
				<UButton
					label="Заполнить данными"
					icon="i-lucide-database"
					color="primary"
					variant="soft"
					class="w-full justify-center"
					:disabled="Boolean(fillDisabled)"
					:loading="loading"
					@click="fillFromLk"
				/>
			</span>
		</UTooltip>

		<UButton
			label="Редактировать данные документа"
			icon="i-lucide-form"
			color="neutral"
			variant="subtle"
			class="w-full justify-center"
			:disabled="!documentId"
			@click="openDialog"
		/>

		<p v-if="saving" class="text-xs text-neutral-500 text-center">Сохранение…</p>

		<UModal v-model:open="dialogOpen" :title="`Данные: ${title}`">
			<template #body>
				<div class="flex flex-col gap-3 max-h-[65vh] overflow-y-auto pr-1">
					<UFormField label="Клиент (поставщик / покупатель)">
						<USelect
							v-model="clientRole"
							:items="[
								{ label: `Поставщик: ${currentDeal?.seller?.companyName || '—'}`, value: 'seller' },
								{ label: `Покупатель: ${currentDeal?.buyer?.companyName || '—'}`, value: 'buyer' },
							]"
						/>
					</UFormField>

					<template v-if="docType !== 'warehouse_receipt'">
						<UFormField label="Грузоотправитель (название)">
							<UInput v-model="payload.shipper.fullName" />
						</UFormField>
						<div class="grid grid-cols-2 gap-2">
							<UFormField label="Индекс">
								<UInput v-model="payload.shipper.index" />
							</UFormField>
							<UFormField label="ИНН">
								<UInput v-model="payload.shipper.inn" />
							</UFormField>
						</div>
						<UFormField label="Адрес грузоотправителя">
							<UInput v-model="payload.shipper.legalAddress" />
						</UFormField>
					</template>

					<UFormField label="Клиент (название)">
						<UInput v-model="payload.client.fullName" />
					</UFormField>
					<div class="grid grid-cols-2 gap-2">
						<UFormField label="Индекс клиента">
							<UInput v-model="payload.client.index" />
						</UFormField>
						<UFormField label="ИНН клиента">
							<UInput v-model="payload.client.inn" />
						</UFormField>
					</div>
					<UFormField label="Адрес клиента">
						<UInput v-model="payload.client.legalAddress" />
					</UFormField>

					<template v-if="docType === 'forwarder_assignment'">
						<UFormField label="Грузополучатель">
							<UInput v-model="payload.consignee.fullName" />
						</UFormField>
						<div class="grid grid-cols-2 gap-2">
							<UFormField label="Индекс">
								<UInput v-model="payload.consignee.index" />
							</UFormField>
							<UFormField label="ИНН">
								<UInput v-model="payload.consignee.inn" />
							</UFormField>
						</div>
						<UFormField label="Адрес грузополучателя">
							<UInput v-model="payload.consignee.legalAddress" />
						</UFormField>
					</template>

					<UFormField label="Экспедитор">
						<UInput v-model="payload.forwarder.fullName" />
					</UFormField>
					<div class="grid grid-cols-2 gap-2">
						<UFormField label="Индекс">
							<UInput v-model="payload.forwarder.index" />
						</UFormField>
						<UFormField label="ИНН">
							<UInput v-model="payload.forwarder.inn" />
						</UFormField>
					</div>
					<UFormField label="Адрес экспедитора">
						<UInput v-model="payload.forwarder.legalAddress" />
					</UFormField>

					<template v-if="docType === 'warehouse_receipt'">
						<UFormField label="Склад">
							<UInput v-model="payload.warehouse" placeholder="Адрес / наименование склада" />
						</UFormField>
					</template>

					<template v-if="docType === 'forwarder_assignment'">
						<UFormField label="Уведомить о прибытии">
							<UInput v-model="payload.notifyParty" />
						</UFormField>
						<UFormField label="Товары готовы к отправке">
							<UInput v-model="payload.readyToShip" />
						</UFormField>
						<UFormField label="Вид транспорта">
							<USelect
								v-model="payload.transportMode"
								:items="TRANSPORT_MODES.map((m) => ({ label: m, value: m }))"
							/>
						</UFormField>
						<UFormField label="Пункт назначения">
							<USelect
								v-if="destinationOptions.length"
								v-model="payload.destination"
								:items="destinationOptions.map((a) => ({ label: a, value: a }))"
								placeholder="Адрес приёма покупателя"
							/>
							<UInput v-else v-model="payload.destination" placeholder="Адрес вручную" />
						</UFormField>
						<UFormField label="Страхование">
							<UInput v-model="payload.insurance" />
						</UFormField>
						<UFormField label="Требуемые документы">
							<UInput v-model="payload.requiredDocs" />
						</UFormField>
					</template>

					<template v-if="docType === 'warehouse_receipt'">
						<UFormField label="Страхование">
							<UInput v-model="payload.insurance" />
						</UFormField>
					</template>

					<UFormField label="Страна происхождения">
						<UInput v-model="payload.originCountry" />
					</UFormField>
					<UFormField label="Товарный код">
						<UInput v-model="payload.commodityCode" />
					</UFormField>
					<UFormField label="Маркировка">
						<UInput v-model="payload.marking" />
					</UFormField>
					<UFormField label="Кол-во мест, упаковка">
						<UInput v-model="payload.placesPackaging" />
					</UFormField>
					<UFormField label="Вес брутто / нетто, кг">
						<UInput v-model="payload.weightGrossNet" />
					</UFormField>
					<UFormField label="Объём">
						<UInput v-model="payload.volume" />
					</UFormField>
					<UFormField label="Стоимость">
						<UInput v-model="payload.value" />
					</UFormField>
					<UFormField label="Размер упаковки">
						<UInput v-model="payload.packageSize" />
					</UFormField>

					<template v-if="docType !== 'forwarder_assignment'">
						<UFormField label="Условия">
							<UInput v-model="payload.terms" />
						</UFormField>
					</template>

					<UFormField label="Особые отметки">
						<UInput v-model="payload.notes" />
					</UFormField>

					<div class="grid grid-cols-2 gap-2">
						<UFormField
							:label="docType === 'warehouse_receipt' ? 'Должность экспедитора' : 'Должность клиента'"
						>
							<UInput v-model="payload.signaturePosition" />
						</UFormField>
						<UFormField
							:label="docType === 'warehouse_receipt' ? 'ФИО экспедитора' : 'ФИО клиента'"
						>
							<UInput v-model="payload.signatureName" />
						</UFormField>
					</div>
				</div>
			</template>
			<template #footer>
				<div class="flex gap-2 w-full">
					<UButton
						label="Отмена"
						color="neutral"
						variant="subtle"
						class="w-1/2"
						@click="dialogOpen = false"
					/>
					<UButton label="Сохранить на бланк" color="primary" class="w-1/2" @click="applyDialog" />
				</div>
			</template>
		</UModal>
	</div>
</template>
