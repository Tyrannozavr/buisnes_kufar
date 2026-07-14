<template>
	<div>
		<div class="w-full field-sizing-content resize-none">
			<p
				v-for="(line, idx) in visibleTermsLines"
				:key="`ct-${idx}-${line.slice(0, 24)}`"
			>
				{{ replaceFields(line, billData, 'bill-contract') }}
			</p>
		</div>
	</div>

	<br>
	<hr class="border-2">
	<br>

	<div>
		<table class="w-full table-fixed border-separate border-spacing-x-4 border-spacing-y-0">
			<tbody>
				<tr>
					<td v-if="supplierDetailsCheck" class="w-1/2 align-top break-words">{{ billData.seller.companyName }}</td>
					<td v-if="buyerDetailsCheck" class="w-1/2 align-top break-words">{{ billData.buyer.companyName }}</td>
				</tr>
				<tr>
					<td v-if="supplierDetailsCheck" class="align-top break-words">{{ billData.seller.index }} {{ billData.seller.legalAddress }}</td>
					<td v-if="buyerDetailsCheck" class="align-top break-words">{{ billData.buyer.index }} {{ billData.buyer.legalAddress }}</td>
				</tr>
				<tr>
					<td v-if="supplierDetailsCheck" class="align-top">ИНН: {{ billData.seller.inn }} КПП: {{ billData.seller.kpp }}</td>
					<td v-if="buyerDetailsCheck" class="align-top">ИНН: {{ billData.buyer.inn }} КПП: {{ billData.buyer.kpp }}</td>
				</tr>
				<tr>
					<td v-if="supplierDetailsCheck" class="align-top break-words">Рас/счет №: {{ billData.seller.accountNumber || '' }}</td>
					<td v-if="buyerDetailsCheck" class="align-top break-words">Рас/счет №: {{ billData.buyer.accountNumber || '' }}</td>
				</tr>
				<tr>
					<td v-if="supplierDetailsCheck" class="align-top break-words">Корр/счет: {{ billData.seller.correspondentBankAccount || '' }}</td>
					<td v-if="buyerDetailsCheck" class="align-top break-words">Корр/счет: {{ billData.buyer.correspondentBankAccount || '' }}</td>
				</tr>
				<tr>
					<td v-if="supplierDetailsCheck" class="align-top break-words">Банк: {{ billData.seller.bankName || '' }}</td>
					<td v-if="buyerDetailsCheck" class="align-top break-words">Банк: {{ billData.buyer.bankName || '' }}</td>
				</tr>
				<tr>
					<td v-if="supplierDetailsCheck" class="align-top">БИК: {{ billData.seller.bic || '' }}</td>
					<td v-if="buyerDetailsCheck" class="align-top">БИК: {{ billData.buyer.bic || '' }}</td>
				</tr>
				<tr>
					<td v-if="supplierDetailsCheck" class="h-4"></td>
					<td v-if="buyerDetailsCheck" class="h-4"></td>
				</tr>
				<tr v-for="official in billData.officials" :key="official.id">
					<td v-if="supplierDetailsCheck" class="w-1/2 align-top">
						<div class="flex flex-col gap-1">
							<p class="text-sm leading-snug">{{ official.position }}</p>
							<!-- место под подпись — не сжимать текст в h-5 -->
							<div class="min-h-8"></div>
							<div class="border-t border-neutral-800 pt-1">
								<p class="text-sm leading-snug break-words">{{ official.name }}</p>
								<p class="text-center text-xs text-neutral-500">(должность, подпись, ФИО)</p>
							</div>
						</div>
					</td>
					<td v-if="buyerDetailsCheck" class="w-1/2 align-top">
						<div class="flex flex-col gap-1">
							<p class="text-sm leading-snug invisible select-none" aria-hidden="true">
								{{ official.position || '—' }}
							</p>
							<div class="min-h-8"></div>
							<div class="border-t border-neutral-800 pt-1">
								<p class="text-sm leading-snug break-words">&nbsp;</p>
								<p class="text-center text-xs text-neutral-500">(должность, подпись, ФИО)</p>
							</div>
						</div>
					</td>
				</tr>
				<tr v-if="billData.officials.length === 0">
					<td v-if="supplierDetailsCheck" class="w-1/2 align-top">
						<div class="flex flex-col gap-1">
							<div class="min-h-10"></div>
							<div class="border-t border-neutral-800 pt-1">
								<p class="text-center text-xs text-neutral-500">(должность, подпись, ФИО)</p>
							</div>
						</div>
					</td>
					<td v-if="buyerDetailsCheck" class="w-1/2 align-top">
						<div class="flex flex-col gap-1">
							<div class="min-h-10"></div>
							<div class="border-t border-neutral-800 pt-1">
								<p class="text-center text-xs text-neutral-500">(должность, подпись, ФИО)</p>
							</div>
						</div>
					</td>
				</tr>
			</tbody>
		</table>
	</div>
</template>

<script setup lang="ts">
import type { BillData } from '~/types/bill'
import { filterTermsLinesByChecks, replaceFields } from '~/utils/replace'

const props = withDefaults(defineProps<{
	billData: BillData
	supplierDetailsCheck?: boolean
	buyerDetailsCheck?: boolean
	paymentTermsCheckContract?: boolean
	deliveryTermsCheckContract?: boolean
}>(), {
	supplierDetailsCheck: true,
	buyerDetailsCheck: true,
	paymentTermsCheckContract: true,
	deliveryTermsCheckContract: true,
})

const visibleTermsLines = computed(() =>
	filterTermsLinesByChecks(props.billData.contractTermsTextContract || '', {
		includePayment: props.paymentTermsCheckContract !== false,
		includeDelivery: props.deliveryTermsCheckContract !== false,
	}),
)
</script>
