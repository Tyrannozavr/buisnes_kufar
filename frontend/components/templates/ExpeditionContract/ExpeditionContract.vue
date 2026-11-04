<script setup lang="ts">
import { formatLegalAddressForParty } from '~/utils/companyPartyLine'
import { useExpeditionContractBlank } from '~/composables/useExpeditionContractBlank'
import { sanitizeRichHtml } from '~/utils/sanitizeRichHtml'
import YellowDateField from '~/components/ui/YellowDateField.vue'

/** А4 бланк «Договор транспортной экспедиции» (§4.2). */
const {
	documentId,
	number,
	dateIso,
	city,
	bodyHtml,
	client,
	forwarder,
	clientDetailsCheck,
	forwarderDetailsCheck,
	loading,
	isDisabled,
	yellowInputClass,
	loadDealTrigger,
	loadDocument,
	bumpSlot,
} = useExpeditionContractBlank()

const route = useRoute()
const safeBodyHtml = computed(() => sanitizeRichHtml(bodyHtml.value))

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
	[number, dateIso, city, bodyHtml, client, forwarder, clientDetailsCheck, forwarderDetailsCheck],
	() => bumpSlot(),
	{ deep: true },
)
</script>

<template>
	<div id="expeditionContract" class="text-sm leading-relaxed">
		<p v-if="loading" class="text-neutral-500 text-center py-8">Загрузка бланка…</p>
		<template v-else-if="!documentId">
			<p class="text-neutral-500 text-center py-8">
				Договор экспедиции не привязан к сделке. Создайте его из колонки «Договор перевозки».
			</p>
		</template>
		<template v-else>
			<h1 class="text-center font-bold text-base mb-3">
				ДОГОВОР ТРАНСПОРТНОЙ ЭКСПЕДИЦИИ №
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
					<YellowDateField
						v-model="dateIso"
						:disabled="isDisabled"
						aria-label="Дата договора"
					/>
				</span>
			</div>

			<p v-if="client.companyType !== 'ИП'" class="mb-2">
				<input
					v-model="client.fullName"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="w-full max-w-xl"
					placeholder="Полное название организации"
				/>,
				далее — <span class="font-bold text-red-600">«Клиент»</span>, от имени которого действует
				<input v-model="client.officialPosition" :disabled="isDisabled" :class="yellowInputClass" class="w-40" placeholder="Должность" />
				<input v-model="client.officialName" :disabled="isDisabled" :class="yellowInputClass" class="w-48" placeholder="ФИО" />,
				действующего(ей) на основании
				<input v-model="client.foundationKind" :disabled="isDisabled" :class="yellowInputClass" class="w-28" placeholder="Устава" />
				<input
					v-if="client.foundationTitle || !/^устава$/i.test(client.foundationKind)"
					v-model="client.foundationTitle"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="w-40"
					placeholder="№ / дата"
				/>, с одной стороны
			</p>
			<p v-else class="mb-2">
				<input v-model="client.fullName" :disabled="isDisabled" :class="yellowInputClass" class="w-full max-w-xl" />,
				далее — <span class="font-bold text-red-600">«Клиент»</span>, зарегистрированный в реестре
				индивидуальных предпринимателей под №
				<input v-model="client.ogrn" :disabled="isDisabled" :class="yellowInputClass" class="w-40" />
				с одной стороны
			</p>

			<p v-if="forwarder.companyType !== 'ИП'" class="mb-3">
				<input
					v-model="forwarder.fullName"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="w-full max-w-xl"
					placeholder="Полное название организации"
				/>,
				далее — <span class="font-bold text-red-600">«Экспедитор»</span>, от имени которого действует
				<input v-model="forwarder.officialPosition" :disabled="isDisabled" :class="yellowInputClass" class="w-40" placeholder="Должность" />
				<input v-model="forwarder.officialName" :disabled="isDisabled" :class="yellowInputClass" class="w-48" placeholder="ФИО" />,
				действующего(ей) на основании
				<input v-model="forwarder.foundationKind" :disabled="isDisabled" :class="yellowInputClass" class="w-28" placeholder="Устава" />
				<input
					v-if="forwarder.foundationTitle || !/^устава$/i.test(forwarder.foundationKind)"
					v-model="forwarder.foundationTitle"
					:disabled="isDisabled"
					:class="yellowInputClass"
					class="w-40"
					placeholder="№ / дата"
				/>, с другой стороны, далее совместно именуемые «Стороны», заключили настоящий
				Договор транспортной экспедиции (далее — «Договор») о нижеследующем:
			</p>
			<p v-else class="mb-3">
				<input v-model="forwarder.fullName" :disabled="isDisabled" :class="yellowInputClass" class="w-full max-w-xl" />,
				далее — <span class="font-bold text-red-600">«Экспедитор»</span>, зарегистрированный в реестре
				индивидуальных предпринимателей под №
				<input v-model="forwarder.ogrn" :disabled="isDisabled" :class="yellowInputClass" class="w-40" />
				с другой стороны, далее совместно именуемые «Стороны», заключили настоящий
				Договор транспортной экспедиции (далее — «Договор») о нижеследующем:
			</p>

			<div
				class="expedition-contract-body border border-transparent mb-4"
				:class="{ 'pointer-events-none opacity-90': isDisabled }"
				v-html="safeBodyHtml"
			/>

			<table class="w-full table_without_border mt-4">
				<tr class="font-bold align-top">
					<td v-if="clientDetailsCheck" class="w-1/2 pr-2">КЛИЕНТ:</td>
					<td v-if="forwarderDetailsCheck" class="w-1/2 pl-2">ЭКСПЕДИТОР:</td>
				</tr>
				<tr class="align-top">
					<td v-if="clientDetailsCheck" class="pr-2">
						<p class="font-bold">{{ client.fullName || '—' }}</p>
						<p>{{ formatLegalAddressForParty(client.index, client.legalAddress) }}</p>
						<p>ИНН {{ client.inn }}</p>
						<p v-if="client.kpp">КПП {{ client.kpp }}</p>
						<p>Рас/счет № {{ client.accountNumber }} в {{ client.bankName }}</p>
						<p>{{ client.correspondentBankAccount }}</p>
						<p>БИК {{ client.bic }}</p>
						<p class="mt-3">________________ / {{ client.officialName || '____________' }} /</p>
						<p>М.П.</p>
						<p class="text-xs mt-1">
							<YellowDateField
								v-model="dateIso"
								:disabled="isDisabled"
								aria-label="Дата договора (клиент)"
							/>
						</p>
					</td>
					<td v-if="forwarderDetailsCheck" class="pl-2">
						<p class="font-bold">{{ forwarder.fullName || '—' }}</p>
						<p>{{ formatLegalAddressForParty(forwarder.index, forwarder.legalAddress) }}</p>
						<p>ИНН {{ forwarder.inn }}</p>
						<p v-if="forwarder.kpp">КПП {{ forwarder.kpp }}</p>
						<p>Рас/счет № {{ forwarder.accountNumber }} в {{ forwarder.bankName }}</p>
						<p>{{ forwarder.correspondentBankAccount }}</p>
						<p>БИК {{ forwarder.bic }}</p>
						<p class="mt-3">________________ / {{ forwarder.officialName || '____________' }} /</p>
						<p>М.П.</p>
						<p class="text-xs mt-1">
							<YellowDateField
								v-model="dateIso"
								:disabled="isDisabled"
								aria-label="Дата договора (экспедитор)"
							/>
						</p>
					</td>
				</tr>
			</table>
		</template>
	</div>
</template>
