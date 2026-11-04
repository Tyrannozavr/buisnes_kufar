<script setup lang="ts">
import { normalizeDate } from '~/utils/normalize'
import { formatLegalAddressForParty } from '~/utils/companyPartyLine'
import { useCarriageApplicationBlank } from '~/composables/useCarriageApplicationBlank'
import CargoTransportTable from '~/components/templates/CarriageApplication/CargoTransportTable.vue'
import { sanitizeRichHtml } from '~/utils/sanitizeRichHtml'

/**
 * А4 бланк «Заявка к договору перевозки» (§3.1–§3.3).
 */
const {
	documentId,
	number,
	dateIso,
	parentId,
	parentNumber,
	parentDateIso,
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
	dealId,
	loadDealTrigger,
	loadDocument,
	bumpSlot,
} = useCarriageApplicationBlank()

const route = useRoute()
const router = useRouter()

const parentDateLabel = computed(() => {
	const n = normalizeDate(parentDateIso.value)
	return n || '«____» _______________ 20____'
})

const appDateLabel = computed(() => {
	const n = normalizeDate(dateIso.value)
	return n || '«____» _______________ 20____'
})

const safeExtraTermsHtml = computed(() => sanitizeRichHtml(extraTermsHtml.value))

const openParentContract = () => {
	if (!parentId.value || !dealId.value) return
	const role = String(route.query.role || 'seller')
	void router.push({
		path: '/profile/editor',
		query: {
			dealId: String(dealId.value),
			role,
			transportDocType: 'carriage_contract',
			transportDocId: String(parentId.value),
		},
		hash: '#contract',
	})
}

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
		parentNumber,
		parentDateIso,
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
	<div id="carriageApplication" class="text-sm leading-relaxed">
		<p v-if="loading" class="text-neutral-500 text-center py-8">Загрузка бланка…</p>
		<template v-else-if="!documentId">
			<p class="text-neutral-500 text-center py-8">
				Заявка не привязана к сделке. Создайте её из колонки «Договор перевозки»
				(тип «Заявка к договору»).
			</p>
		</template>
		<template v-else>
			<!-- §3.1 шапка: родитель + номер заявки (красные); номер договора — ссылка -->
			<p class="text-center mb-1">
				Приложение к Договору перевозки грузов №
				<button
					v-if="parentId && parentNumber"
					type="button"
					class="text-red-600 font-semibold underline underline-offset-2 hover:text-red-700"
					:title="`Открыть договор № ${parentNumber}`"
					@click="openParentContract"
				>
					{{ parentNumber }}
				</button>
				<span v-else :class="redReadonlyClass">{{ parentNumber || '___' }}</span>
				от
				<span :class="redReadonlyClass">{{ parentDateLabel }}</span>
				г.
			</p>
			<h1 class="text-center font-bold text-base mb-1">
				ЗАЯВКА НА ПЕРЕВОЗКУ ГРУЗОВ №
				<span :class="redReadonlyClass">{{ number || '___' }}</span>
			</h1>
			<p class="text-center mb-4">
				от
				<span :class="redReadonlyClass">{{ appDateLabel }}</span>
				г.
			</p>

			<!-- §3.3 шапка Заказчик / Перевозчик (жёлтые) -->
			<p class="mb-2">
				<span class="font-semibold">Заказчик:</span>
				<input
					v-model="customer.fullName"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="w-full max-w-xl mt-1"
					placeholder="ОПФ, название"
					aria-label="Заказчик"
				/>
			</p>
			<p class="mb-1 text-xs text-neutral-600">ИНН / КПП / адрес</p>
			<p class="mb-3 flex flex-wrap gap-1">
				<input
					v-model="customer.inn"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="w-28"
					placeholder="ИНН"
					aria-label="ИНН заказчика"
				/>
				<input
					v-model="customer.kpp"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="w-28"
					placeholder="КПП"
					aria-label="КПП заказчика"
				/>
				<input
					v-model="customer.index"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="w-20"
					placeholder="Индекс"
					aria-label="Индекс заказчика"
				/>
				<input
					v-model="customer.legalAddress"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="flex-1 min-w-[12rem]"
					placeholder="Юридический адрес"
					aria-label="Адрес заказчика"
				/>
			</p>

			<p class="mb-2">
				<span class="font-semibold">Перевозчик:</span>
				<input
					v-model="carrier.fullName"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="w-full max-w-xl mt-1"
					placeholder="ОПФ, название"
					aria-label="Перевозчик"
				/>
			</p>
			<p class="mb-1 text-xs text-neutral-600">ИНН / КПП / адрес</p>
			<p class="mb-4 flex flex-wrap gap-1">
				<input
					v-model="carrier.inn"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="w-28"
					placeholder="ИНН"
					aria-label="ИНН перевозчика"
				/>
				<input
					v-model="carrier.kpp"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="w-28"
					placeholder="КПП"
					aria-label="КПП перевозчика"
				/>
				<input
					v-model="carrier.index"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="w-20"
					placeholder="Индекс"
					aria-label="Индекс перевозчика"
				/>
				<input
					v-model="carrier.legalAddress"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="flex-1 min-w-[12rem]"
					placeholder="Юридический адрес"
					aria-label="Адрес перевозчика"
				/>
			</p>

			<!-- §3.2 серая таблица -->
			<CargoTransportTable :rows="tableRows" />

			<!-- §3.2 доп. условия (серый блок, правка только через меню) -->
			<div
				class="my-4 rounded border border-neutral-300 bg-neutral-100 p-3 pointer-events-none"
				aria-label="Дополнительные условия"
			>
				<div class="prose prose-sm max-w-none" v-html="safeExtraTermsHtml" />
			</div>

			<!-- §3.3 реквизиты / подписи -->
			<table class="w-full table_without_border mt-4">
				<tr class="font-bold align-top">
					<td v-if="customerDetailsCheck" class="w-1/2 pr-2">ЗАКАЗЧИК:</td>
					<td v-if="carrierDetailsCheck" class="w-1/2 pl-2">ПЕРЕВОЗЧИК:</td>
				</tr>
				<tr class="align-top">
					<td v-if="customerDetailsCheck" class="pr-2 space-y-1">
						<p class="font-bold">
							<input
								v-model="customer.fullName"
								:disabled="isDisabled"
								:class="yellowInputClass"
								class="w-full"
							/>
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
							<input
								v-model="customer.officialPosition"
								:disabled="isDisabled"
								:class="yellowInputClass"
								class="w-40"
								placeholder="Должность"
							/>
						</p>
						<p>
							________________ /
							<input
								v-model="customer.officialName"
								:disabled="isDisabled"
								:class="yellowInputClass"
								class="w-40"
								placeholder="ФИО"
							/>
							/
						</p>
						<p>М.П.</p>
					</td>
					<td v-if="carrierDetailsCheck" class="pl-2 space-y-1">
						<p class="font-bold">
							<input
								v-model="carrier.fullName"
								:disabled="isDisabled"
								:class="yellowInputClass"
								class="w-full"
							/>
						</p>
						<p>
							<input
								v-model="carrier.legalAddress"
								:disabled="isDisabled"
								:class="yellowInputClass"
								class="w-full"
							/>
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
							<input
								v-model="carrier.officialPosition"
								:disabled="isDisabled"
								:class="yellowInputClass"
								class="w-40"
								placeholder="Должность"
							/>
						</p>
						<p>
							________________ /
							<input
								v-model="carrier.officialName"
								:disabled="isDisabled"
								:class="yellowInputClass"
								class="w-40"
								placeholder="ФИО"
							/>
							/
						</p>
						<p>М.П.</p>
					</td>
				</tr>
			</table>
		</template>
	</div>
</template>
