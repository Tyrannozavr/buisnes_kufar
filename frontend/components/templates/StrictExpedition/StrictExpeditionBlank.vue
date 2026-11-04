<script setup lang="ts">
import { normalizeDate } from '~/utils/normalize'
import { useStrictExpeditionBlank } from '~/composables/useStrictExpeditionBlank'
import {
	STRICT_EXPEDITION_TITLES,
	formatStrictPartyBlock,
	type StrictExpeditionDocType,
} from '~/utils/strictExpeditionDefaults'

const props = defineProps<{ docType: StrictExpeditionDocType }>()

const {
	documentId,
	number,
	dateIso,
	parentNumber,
	parentDateIso,
	payload,
	loading,
	redReadonlyClass,
	loadDealTrigger,
	loadDocument,
	bumpSlot,
} = useStrictExpeditionBlank()

const route = useRoute()

const parentDateLabel = computed(() => {
	const n = normalizeDate(parentDateIso.value)
	return n || '«____» _______________ 20____'
})
const docDateLabel = computed(() => {
	const n = normalizeDate(dateIso.value)
	return n || '«____» _______________ 20____'
})

const title = computed(() => STRICT_EXPEDITION_TITLES[props.docType])

type Row = { n?: string | number; label: string; value: string }
const rows = computed((): Row[] => {
	const p = payload.value
	const base: Row[] = [
		{ n: 1, label: 'Дата', value: docDateLabel.value },
		{ n: 2, label: 'Номер', value: number.value || '—' },
	]
	if (props.docType === 'forwarder_assignment') {
		return [
			...base,
			{ n: 3, label: 'Грузоотправитель', value: formatStrictPartyBlock(p.shipper) },
			{ n: 4, label: 'Клиент', value: formatStrictPartyBlock(p.client) },
			{ n: 5, label: 'Грузополучатель', value: formatStrictPartyBlock(p.consignee) },
			{ n: 6, label: 'Экспедитор', value: formatStrictPartyBlock(p.forwarder) },
			{ n: 7, label: 'Уведомить о прибытии груза', value: p.notifyParty || '—' },
			{ n: 8, label: 'Страна происхождения груза', value: p.originCountry || '—' },
			{ n: 9, label: 'Товары готовы к отправке (место, дата)', value: p.readyToShip || '—' },
			{ n: 10, label: 'Вид транспорта', value: p.transportMode || '—' },
			{ n: 11, label: 'Пункт назначения', value: p.destination || '—' },
			{ n: 12, label: 'Страхование', value: p.insurance || '—' },
			{ n: 13, label: 'Товарный код', value: p.commodityCode || '—' },
			{ n: 14, label: 'Маркировка', value: p.marking || '—' },
			{ n: 15, label: 'Количество мест, вид упаковки', value: p.placesPackaging || '—' },
			{ n: 16, label: 'Вес брутто / нетто, кг', value: p.weightGrossNet || '—' },
			{ n: 17, label: 'Объём', value: p.volume || '—' },
			{ n: 18, label: 'Стоимость', value: p.value || '—' },
			{ n: 19, label: 'Размер упаковки', value: p.packageSize || '—' },
			{ n: 20, label: 'Требуемые документы', value: p.requiredDocs || '—' },
			{ n: 21, label: 'Особые отметки', value: p.notes || '—' },
			{
				n: 22,
				label: 'Подпись клиента',
				value: [p.signaturePosition, p.signatureName].filter(Boolean).join(' / ') || '—',
			},
		]
	}
	if (props.docType === 'forwarder_receipt') {
		return [
			...base,
			{ n: 3, label: 'Грузоотправитель', value: formatStrictPartyBlock(p.shipper) },
			{ n: 4, label: 'Клиент', value: formatStrictPartyBlock(p.client) },
			{ n: 5, label: 'Экспедитор', value: formatStrictPartyBlock(p.forwarder) },
			{ n: 6, label: 'Страна происхождения груза', value: p.originCountry || '—' },
			{ n: 7, label: 'Товарный код', value: p.commodityCode || '—' },
			{ n: 8, label: 'Маркировка', value: p.marking || '—' },
			{ n: 9, label: 'Количество мест, вид упаковки', value: p.placesPackaging || '—' },
			{ n: 10, label: 'Вес брутто / нетто, кг', value: p.weightGrossNet || '—' },
			{ n: 11, label: 'Объём', value: p.volume || '—' },
			{ n: 12, label: 'Стоимость', value: p.value || '—' },
			{ n: 13, label: 'Размер упаковки', value: p.packageSize || '—' },
			{ n: 14, label: 'Условия', value: p.terms || '—' },
			{ n: 15, label: 'Особые отметки', value: p.notes || '—' },
			{
				n: 16,
				label: 'Подпись клиента',
				value: [p.signaturePosition, p.signatureName].filter(Boolean).join(' / ') || '—',
			},
		]
	}
	return [
		...base,
		{ n: 3, label: 'Клиент', value: formatStrictPartyBlock(p.client) },
		{ n: 4, label: 'Экспедитор', value: formatStrictPartyBlock(p.forwarder) },
		{ n: 5, label: 'Склад', value: p.warehouse || '—' },
		{ n: 6, label: 'Страна происхождения груза', value: p.originCountry || '—' },
		{ n: 7, label: 'Страхование', value: p.insurance || '—' },
		{ n: 8, label: 'Товарный код', value: p.commodityCode || '—' },
		{ n: 9, label: 'Маркировка', value: p.marking || '—' },
		{ n: 10, label: 'Количество мест, вид упаковки', value: p.placesPackaging || '—' },
		{ n: 11, label: 'Вес брутто / нетто, кг', value: p.weightGrossNet || '—' },
		{ n: 12, label: 'Объём', value: p.volume || '—' },
		{ n: 13, label: 'Стоимость', value: p.value || '—' },
		{ n: 14, label: 'Размер упаковки', value: p.packageSize || '—' },
		{ n: 15, label: 'Условия', value: p.terms || '—' },
		{ n: 16, label: 'Особые отметки', value: p.notes || '—' },
		{
			n: 17,
			label: 'Подпись экспедитора',
			value: [p.signaturePosition, p.signatureName].filter(Boolean).join(' / ') || '—',
		},
	]
})

watch(
	() => [
		route.query.dealId,
		route.query.transportDocId,
		route.query.transportDocType,
		loadDealTrigger.value,
	],
	() => {
		void loadDocument()
	},
	{ immediate: true },
)

watch([number, dateIso, parentNumber, parentDateIso, payload], () => bumpSlot(), { deep: true })
</script>

<template>
	<div :id="`strictExpedition-${docType}`" class="text-sm leading-relaxed pointer-events-none">
		<p v-if="loading" class="text-neutral-500 text-center py-8 pointer-events-auto">Загрузка бланка…</p>
		<template v-else-if="!documentId">
			<p class="text-neutral-500 text-center py-8 pointer-events-auto">
				Документ не привязан. Создайте его из колонки «Договор перевозки» (нужен договор экспедиции).
			</p>
		</template>
		<template v-else>
			<p
				v-if="docType === 'warehouse_receipt'"
				class="text-center text-xs text-neutral-600 mb-2"
			>
				Приложение № 3 к приказу Минтранса РФ от 11 февраля 2008 г. № 23
			</p>
			<p class="text-center mb-1">
				Приложение к Договору транспортной экспедиции №
				<span :class="redReadonlyClass">{{ parentNumber || '___' }}</span>
				от
				<span :class="redReadonlyClass">{{ parentDateLabel }}</span>
				г.
			</p>
			<h1 class="text-center font-bold text-base mb-4">{{ title }}</h1>

			<table class="w-full border-collapse text-sm">
				<tbody>
					<tr v-for="(row, idx) in rows" :key="idx" class="align-top border-b border-neutral-200">
						<td class="py-1.5 pr-2 w-8 text-neutral-500">{{ row.n }}</td>
						<td class="py-1.5 pr-3 w-2/5 font-medium text-neutral-800">{{ row.label }}</td>
						<td class="py-1.5 whitespace-pre-line text-neutral-900">{{ row.value }}</td>
					</tr>
				</tbody>
			</table>
		</template>
	</div>
</template>
