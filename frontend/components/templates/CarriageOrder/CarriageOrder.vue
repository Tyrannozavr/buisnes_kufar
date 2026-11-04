<script setup lang="ts">
import { normalizeDate } from '~/utils/normalize'
import { formatLegalAddressForParty } from '~/utils/companyPartyLine'
import { useCarriageOrderBlank } from '~/composables/useCarriageOrderBlank'
import CargoTransportTable from '~/components/templates/CarriageApplication/CargoTransportTable.vue'
import { sanitizeRichHtml } from '~/utils/sanitizeRichHtml'
import YellowDateField from '~/components/ui/YellowDateField.vue'

/** А4 бланк «Договор-заявка» (§4.1). */
const {
	documentId,
	number,
	dateIso,
	city,
	preambleDate,
	customer,
	carrier,
	extraTermsHtml,
	customerDetailsCheck,
	carrierDetailsCheck,
	tableRows,
	loading,
	isDisabled,
	yellowInputClass,
	redReadonlyClass,
	introStatic,
	loadDealTrigger,
	loadDocument,
	bumpSlot,
} = useCarriageOrderBlank()

const route = useRoute()
const safeExtraTermsHtml = computed(() => sanitizeRichHtml(extraTermsHtml.value))

const titleDateLabel = computed(() => {
	const n = normalizeDate(dateIso.value)
	return n || '«____» _______________ 20____'
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

watch(
	[
		number,
		dateIso,
		city,
		preambleDate,
		customer,
		carrier,
		extraTermsHtml,
		customerDetailsCheck,
		carrierDetailsCheck,
		tableRows,
	],
	() => bumpSlot(),
	{ deep: true },
)
</script>

<template>
	<div id="carriageOrder" class="text-sm leading-relaxed">
		<p v-if="loading" class="text-neutral-500 text-center py-8">Загрузка бланка…</p>
		<template v-else-if="!documentId">
			<p class="text-neutral-500 text-center py-8">
				Договор-заявка не привязан к сделке. Создайте его из колонки «Договор перевозки».
			</p>
		</template>
		<template v-else>
			<h1 class="text-center font-bold text-base mb-1">
				ДОГОВОР-ЗАЯВКА №
				<span :class="redReadonlyClass">{{ number || '______' }}</span>
			</h1>
			<p class="text-center mb-3">
				от
				<span :class="redReadonlyClass">{{ titleDateLabel }}</span>
				г.
			</p>

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
					<YellowDateField
						v-model="preambleDate"
						:disabled="isDisabled"
						aria-label="Дата преамбулы"
					/>
				</span>
			</div>

			<p v-if="customer.companyType !== 'ИП'" class="mb-2">
				<input
					v-model="customer.fullName"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="w-full max-w-xl"
					placeholder="Полное название организации"
				/>,
				далее — <span class="font-bold text-red-600">«Заказчик»</span>, от имени которого действует
				<input v-model="customer.officialPosition" :disabled="isDisabled" :class="yellowInputClass" class="w-40" placeholder="Должность" />
				<input v-model="customer.officialName" :disabled="isDisabled" :class="yellowInputClass" class="w-48" placeholder="ФИО" />,
				действующего(ей) на основании
				<input v-model="customer.foundationKind" :disabled="isDisabled" :class="yellowInputClass" class="w-28" placeholder="Устава" />
				<input
					v-if="customer.foundationTitle || !/^устава$/i.test(customer.foundationKind)"
					v-model="customer.foundationTitle"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="w-40"
					placeholder="№ / дата"
				/>, с одной стороны
			</p>
			<p v-else class="mb-2">
				<input v-model="customer.fullName" :disabled="isDisabled" :class="yellowInputClass" class="w-full max-w-xl" />,
				далее — <span class="font-bold text-red-600">«Заказчик»</span>, зарегистрированный в реестре
				индивидуальных предпринимателей под №
				<input v-model="customer.ogrn" :disabled="isDisabled" :class="yellowInputClass" class="w-40" />
				с одной стороны
			</p>

			<p v-if="carrier.companyType !== 'ИП'" class="mb-3">
				<input
					v-model="carrier.fullName"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="w-full max-w-xl"
					placeholder="Полное название организации"
				/>,
				далее — <span class="font-bold text-red-600">«Перевозчик»</span>, от имени которого действует
				<input v-model="carrier.officialPosition" :disabled="isDisabled" :class="yellowInputClass" class="w-40" placeholder="Должность" />
				<input v-model="carrier.officialName" :disabled="isDisabled" :class="yellowInputClass" class="w-48" placeholder="ФИО" />,
				действующего(ей) на основании
				<input v-model="carrier.foundationKind" :disabled="isDisabled" :class="yellowInputClass" class="w-28" placeholder="Устава" />
				<input
					v-if="carrier.foundationTitle || !/^устава$/i.test(carrier.foundationKind)"
					v-model="carrier.foundationTitle"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="w-40"
					placeholder="№ / дата"
				/>, с другой стороны, далее совместно именуемые «Стороны», заключили настоящий
				договор-заявку о нижеследующем:
			</p>
			<p v-else class="mb-3">
				<input v-model="carrier.fullName" :disabled="isDisabled" :class="yellowInputClass" class="w-full max-w-xl" />,
				далее — <span class="font-bold text-red-600">«Перевозчик»</span>, зарегистрированный в реестре
				индивидуальных предпринимателей под №
				<input v-model="carrier.ogrn" :disabled="isDisabled" :class="yellowInputClass" class="w-40" />
				с другой стороны, далее совместно именуемые «Стороны», заключили настоящий
				договор-заявку о нижеследующем:
			</p>

			<p class="mb-3 italic text-neutral-700">{{ introStatic }}</p>

			<CargoTransportTable :rows="tableRows" />

			<div
				class="my-4 rounded border border-neutral-300 bg-neutral-100 p-3 pointer-events-none"
				aria-label="Дополнительные условия"
			>
				<p class="font-semibold mb-2">ДОПОЛНИТЕЛЬНЫЕ УСЛОВИЯ</p>
				<div class="prose prose-sm max-w-none" v-html="safeExtraTermsHtml" />
			</div>

			<table class="w-full table_without_border mt-4">
				<tr class="font-bold align-top">
					<td v-if="customerDetailsCheck" class="w-1/2 pr-2">ЗАКАЗЧИК:</td>
					<td v-if="carrierDetailsCheck" class="w-1/2 pl-2">ПЕРЕВОЗЧИК:</td>
				</tr>
				<tr class="align-top">
					<td v-if="customerDetailsCheck" class="pr-2 space-y-1">
						<p class="font-bold">
							<input v-model="customer.fullName" :disabled="isDisabled" :class="yellowInputClass" class="w-full" />
						</p>
						<p>
							<input
								v-model="customer.legalAddress"
								:disabled="isDisabled"
								:class="yellowInputClass"
								class="w-full"
								:placeholder="formatLegalAddressForParty(customer.index, '')"
							/>
						</p>
						<p>
							ИНН
							<input v-model="customer.inn" :disabled="isDisabled" :class="yellowInputClass" class="w-28" />
							<span v-if="customer.kpp || !isDisabled">
								КПП
								<input v-model="customer.kpp" :disabled="isDisabled" :class="yellowInputClass" class="w-28" />
							</span>
						</p>
						<p>
							р/с
							<input v-model="customer.accountNumber" :disabled="isDisabled" :class="yellowInputClass" class="w-40" />
							в
							<input v-model="customer.bankName" :disabled="isDisabled" :class="yellowInputClass" class="w-40" />
						</p>
						<p>
							корр.
							<input v-model="customer.correspondentBankAccount" :disabled="isDisabled" :class="yellowInputClass" class="w-40" />
							БИК
							<input v-model="customer.bic" :disabled="isDisabled" :class="yellowInputClass" class="w-28" />
						</p>
						<p class="mt-3">
							<input v-model="customer.officialPosition" :disabled="isDisabled" :class="yellowInputClass" class="w-40" placeholder="Должность" />
						</p>
						<p>
							________________ /
							<input v-model="customer.officialName" :disabled="isDisabled" :class="yellowInputClass" class="w-40" placeholder="ФИО" />
							/
						</p>
						<p>М.П.</p>
					</td>
					<td v-if="carrierDetailsCheck" class="pl-2 space-y-1">
						<p class="font-bold">
							<input v-model="carrier.fullName" :disabled="isDisabled" :class="yellowInputClass" class="w-full" />
						</p>
						<p>
							<input v-model="carrier.legalAddress" :disabled="isDisabled" :class="yellowInputClass" class="w-full" />
						</p>
						<p>
							ИНН
							<input v-model="carrier.inn" :disabled="isDisabled" :class="yellowInputClass" class="w-28" />
							<span v-if="carrier.kpp || !isDisabled">
								КПП
								<input v-model="carrier.kpp" :disabled="isDisabled" :class="yellowInputClass" class="w-28" />
							</span>
						</p>
						<p>
							р/с
							<input v-model="carrier.accountNumber" :disabled="isDisabled" :class="yellowInputClass" class="w-40" />
							в
							<input v-model="carrier.bankName" :disabled="isDisabled" :class="yellowInputClass" class="w-40" />
						</p>
						<p>
							корр.
							<input v-model="carrier.correspondentBankAccount" :disabled="isDisabled" :class="yellowInputClass" class="w-40" />
							БИК
							<input v-model="carrier.bic" :disabled="isDisabled" :class="yellowInputClass" class="w-28" />
						</p>
						<p class="mt-3">
							<input v-model="carrier.officialPosition" :disabled="isDisabled" :class="yellowInputClass" class="w-40" placeholder="Должность" />
						</p>
						<p>
							________________ /
							<input v-model="carrier.officialName" :disabled="isDisabled" :class="yellowInputClass" class="w-40" placeholder="ФИО" />
							/
						</p>
						<p>М.П.</p>
					</td>
				</tr>
			</table>
		</template>
	</div>
</template>
