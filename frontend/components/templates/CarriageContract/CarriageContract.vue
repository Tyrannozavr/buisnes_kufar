<script setup lang="ts">
import { normalizeDate } from '~/utils/normalize'
import { formatLegalAddressForParty } from '~/utils/companyPartyLine'
import { useCarriageContractBlank } from '~/composables/useCarriageContractBlank'

/**
 * А4 бланк «Договор перевозки грузов» (§2).
 * Данные бланка — в transport_document.payload_json.
 */
const {
	documentId,
	number,
	dateIso,
	city,
	bodyHtml,
	customer,
	carrier,
	customerDetailsCheck,
	carrierDetailsCheck,
	loading,
	isDisabled,
	yellowInputClass,
	loadDealTrigger,
	loadDocument,
	bumpSlot,
} = useCarriageContractBlank()

const route = useRoute()

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

watch(
	[number, dateIso, city, bodyHtml, customer, carrier, customerDetailsCheck, carrierDetailsCheck],
	() => bumpSlot(),
	{ deep: true },
)
</script>

<template>
	<div id="carriageContract" class="text-sm leading-relaxed">
		<p v-if="loading" class="text-neutral-500 text-center py-8">Загрузка бланка…</p>
		<template v-else-if="!documentId">
			<p class="text-neutral-500 text-center py-8">
				Документ перевозки не привязан к сделке. Создайте его из колонки «Договор перевозки».
			</p>
		</template>
		<template v-else>
			<h1 class="text-center font-bold text-base mb-3">
				ДОГОВОР ПЕРЕВОЗКИ ГРУЗОВ №
				<input
					v-model="number"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="text-center font-bold w-28"
					aria-label="Номер договора"
				/>
			</h1>
			<div class="flex justify-between mb-3">
				<span>
					г.
					<input
						v-model="city"
						:disabled="isDisabled"
						:class="yellowInputClass"
						class="w-36"
						aria-label="Город"
					/>
				</span>
				<span>
					<input
						v-model="dateIso"
						type="date"
						:disabled="isDisabled"
						:class="yellowInputClass"
						aria-label="Дата договора"
					/>
					<span v-if="dateIso" class="ml-1">г.</span>
					<span v-else class="ml-1 text-neutral-400">«____» _______________ 20____г.</span>
				</span>
			</div>

			<!-- Заказчик: по ТЗ {position} {fio} / {foundation} {foundation_title} -->
			<p v-if="customer.companyType !== 'ИП'" class="mb-2">
				<input
					v-model="customer.fullName"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="w-full max-w-xl"
					placeholder="Полное название организации"
					aria-label="Заказчик — полное название"
				/>,
				далее — <span class="font-bold">«Заказчик»</span>, от имени которого действует
				<input
					v-model="customer.officialPosition"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="w-40"
					placeholder="Должность"
					aria-label="Должность заказчика"
					title="Должность"
				/>
				<input
					v-model="customer.officialName"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="w-48"
					placeholder="ФИО"
					aria-label="ФИО заказчика"
					title="ФИО"
				/>,
				действующего(ей) на основании
				<input
					v-model="customer.foundationKind"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="w-28"
					placeholder="Устава"
					aria-label="Документ основания"
					title="Документ основания (Устава / доверенности)"
				/>
				<input
					v-if="customer.foundationTitle || !/^устава$/i.test(customer.foundationKind)"
					v-model="customer.foundationTitle"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="w-40"
					placeholder="№ / дата"
					aria-label="Название документа основания"
					title="Только для доверенности и т.п.; при Уставе не нужно"
				/>, с одной стороны
			</p>
			<p v-else class="mb-2">
				<input
					v-model="customer.fullName"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="w-full max-w-xl"
				/>,
				далее — <span class="font-bold">«Заказчик»</span>, зарегистрированный в реестре
				индивидуальных предпринимателей под №
				<input
					v-model="customer.ogrn"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="w-40"
				/>
				с одной стороны
			</p>

			<!-- Перевозчик: по ТЗ {position} {fio} / {foundation} {foundation_title} -->
			<p v-if="carrier.companyType !== 'ИП'" class="mb-3">
				<input
					v-model="carrier.fullName"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="w-full max-w-xl"
					placeholder="Полное название организации"
					aria-label="Перевозчик — полное название"
				/>,
				далее — <span class="font-bold">«Перевозчик»</span>, от имени которого действует
				<input
					v-model="carrier.officialPosition"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="w-40"
					placeholder="Должность"
					aria-label="Должность перевозчика"
					title="Должность"
				/>
				<input
					v-model="carrier.officialName"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="w-48"
					placeholder="ФИО"
					aria-label="ФИО перевозчика"
					title="ФИО"
				/>,
				действующего(ей) на основании
				<input
					v-model="carrier.foundationKind"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="w-28"
					placeholder="Устава"
					aria-label="Документ основания"
					title="Документ основания (Устава / доверенности)"
				/>
				<input
					v-if="carrier.foundationTitle || !/^устава$/i.test(carrier.foundationKind)"
					v-model="carrier.foundationTitle"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="w-40"
					placeholder="№ / дата"
					aria-label="Название документа основания"
					title="Только для доверенности и т.п.; при Уставе не нужно"
				/>, с другой стороны, далее совместно именуемые «Стороны», заключили настоящий
				Договор перевозки грузов (далее — «Договор») о нижеследующем:
			</p>
			<p v-else class="mb-3">
				<input
					v-model="carrier.fullName"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="w-full max-w-xl"
				/>,
				далее — <span class="font-bold">«Перевозчик»</span>, зарегистрированный в реестре
				индивидуальных предпринимателей под №
				<input
					v-model="carrier.ogrn"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="w-40"
				/>
				с другой стороны, далее совместно именуемые «Стороны», заключили настоящий
				Договор перевозки грузов (далее — «Договор») о нижеследующем:
			</p>

			<!-- Тело -->
			<div
				class="carriage-contract-body border border-transparent mb-4"
				:class="{ 'pointer-events-none opacity-90': isDisabled }"
				v-html="bodyHtml"
			/>

			<!-- Реквизиты / подписи -->
			<table class="w-full table_without_border mt-4">
				<tr class="font-bold align-top">
					<td v-if="customerDetailsCheck" class="w-1/2 pr-2">ЗАКАЗЧИК:</td>
					<td v-if="carrierDetailsCheck" class="w-1/2 pl-2">ПЕРЕВОЗЧИК:</td>
				</tr>
				<tr class="align-top">
					<td v-if="customerDetailsCheck" class="pr-2">
						<p class="font-bold">{{ customer.fullName || '—' }}</p>
						<p>{{ formatLegalAddressForParty(customer.index, customer.legalAddress) }}</p>
						<p>ИНН {{ customer.inn }}</p>
						<p v-if="customer.kpp">КПП {{ customer.kpp }}</p>
						<p>Рас/счет № {{ customer.accountNumber }} в {{ customer.bankName }}</p>
						<p>{{ customer.correspondentBankAccount }}</p>
						<p>БИК {{ customer.bic }}</p>
						<p class="mt-3">________________ / {{ customer.officialName || '____________' }} /</p>
						<p>М.П.</p>
						<p class="text-neutral-500 text-xs">{{ normalizeDate(dateIso) ? `${normalizeDate(dateIso)} г.` : '' }}</p>
					</td>
					<td v-if="carrierDetailsCheck" class="pl-2">
						<p class="font-bold">{{ carrier.fullName || '—' }}</p>
						<p>{{ formatLegalAddressForParty(carrier.index, carrier.legalAddress) }}</p>
						<p>ИНН {{ carrier.inn }}</p>
						<p v-if="carrier.kpp">КПП {{ carrier.kpp }}</p>
						<p>Рас/счет № {{ carrier.accountNumber }} в {{ carrier.bankName }}</p>
						<p>{{ carrier.correspondentBankAccount }}</p>
						<p>БИК {{ carrier.bic }}</p>
						<p class="mt-3">________________ / {{ carrier.officialName || '____________' }} /</p>
						<p>М.П.</p>
						<p class="text-neutral-500 text-xs">{{ normalizeDate(dateIso) ? `${normalizeDate(dateIso)} г.` : '' }}</p>
					</td>
				</tr>
			</table>
		</template>
	</div>
</template>
