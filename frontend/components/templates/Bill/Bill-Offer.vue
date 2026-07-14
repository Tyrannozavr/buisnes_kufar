<template>
	<div>
		<div v-if="additionalInfoCheckOffer" class="w-full mb-4">
			<p
				v-for="(line, idx) in additionalInfoOffer.split('\n')"
				:key="`ai-${idx}-${line.slice(0, 24)}`"
			>
				{{ replaceFields(line, billData, 'bill-offer') }}
			</p>
		</div>

		<div v-if="visibleTermsLines.length" class="w-full">
			<p class="underline">Условия счета-оферты:</p>
			<div>
				<p
					v-for="(line, idx) in visibleTermsLines"
					:key="`ct-${idx}-${line.slice(0, 24)}`"
				>
					{{ replaceFields(line, billData, 'bill-offer') }}
				</p>
			</div>
		</div>

		<div class="w-2/5 mt-6">
			<div class="h-5"></div>
			<div class="text-center text-xs border-t">(должность, подпись, ФИО)</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import type { BillData } from '~/types/bill'
import { filterTermsLinesByChecks, replaceFields } from '~/utils/replace'

const props = defineProps<{
	billData: BillData
	additionalInfoCheckOffer: boolean
	paymentTermsCheckOffer?: boolean
}>()

const additionalInfoOffer = computed(() => props.billData.additionalInfoOffer || '')

const visibleTermsLines = computed(() =>
	filterTermsLinesByChecks(props.billData.contractTermsTextOffer || '', {
		includePayment: props.paymentTermsCheckOffer !== false,
		includeDelivery: true,
	}),
)
</script>
