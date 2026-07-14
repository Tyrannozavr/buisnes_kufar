<template>
	<div>
		<div class="w-full field-sizing-content resize-none">
			<p v-if="billData.contractTermsTextContract" v-for="line in billData.contractTermsTextContract.split('\n')" :key="line">{{ replaceFields(line, billData) }}</p>
		</div>
	</div>

	<br>
	<hr class="border-2">
	<br>

	<div>
		<table class="w-full table-fixed">
			<tbody>
				<tr>
					<td v-if="supplierDetailsCheck">{{ billData.seller.companyName }}</td>
					<td v-if="buyerDetailsCheck">{{ billData.buyer.companyName }}</td>
				</tr>
				<tr>
					<td v-if="supplierDetailsCheck">{{ billData.seller.index }} {{ billData.seller.legalAddress }}</td>
					<td v-if="buyerDetailsCheck">{{ billData.buyer.index }} {{ billData.buyer.legalAddress }}</td>
				</tr>
				<tr>
					<td v-if="supplierDetailsCheck">ИНН: {{ billData.seller.inn }} КПП: {{ billData.seller.kpp }}</td>
					<td v-if="buyerDetailsCheck">ИНН: {{ billData.buyer.inn }} КПП: {{ billData.buyer.kpp }}</td>
				</tr>
				<tr>
					<td v-if="supplierDetailsCheck">Рас/счет №: {{ billData.seller.accountNumber }}</td>
					<td v-if="buyerDetailsCheck">Рас/счет №: {{ billData.buyer.accountNumber }}</td>
				</tr>
				<tr>
					<td v-if="supplierDetailsCheck">Корр/счет: {{ billData.seller.correspondentBankAccount }} <br> Банк: {{ billData.seller.bankName }}</td>
					<td v-if="buyerDetailsCheck">Корр/счет: {{ billData.buyer.correspondentBankAccount }} <br> Банк: {{ billData.buyer.bankName }}</td>
				</tr>
				<tr>
					<td v-if="supplierDetailsCheck">БИК: {{ billData.seller.bic }}</td>
					<td v-if="buyerDetailsCheck">БИК: {{ billData.buyer.bic }}</td>
				</tr>
				<tr class="h-5">
				</tr>
				<tr v-for="official in billData.officials" :key="official.id">
					<td v-if="supplierDetailsCheck">
						<div>
							<div class="h-5 flex justify-between">
								<span class="block mr-5">{{ official.position }}</span>
								<span class="block mr-5">{{ official.name }}</span>
							</div>
							<div class="text-center text-xs border-t mr-5">(должность, подпись, ФИО)</div>
						</div>
					</td>
					<td v-if="buyerDetailsCheck">
						<div>
							<div class="h-5"></div>
							<div class="text-center text-xs border-t">(должность, подпись, ФИО)</div>
						</div>
					</td>
				</tr>
				<tr v-if="billData.officials.length === 0">
					<td v-if="supplierDetailsCheck">
						<div class="mr-5">
								<div class="h-5"></div>
								<div class="text-center text-xs border-t">(должность, подпись, ФИО)</div>
						</div>
					</td>
					<td v-if="buyerDetailsCheck">
						<div class="mr-5">
							<div class="h-5"></div>
							<div class="text-center text-xs border-t">(должность, подпись, ФИО)</div>
						</div>
					</td>
				</tr>
			</tbody>
		</table>
	</div>
</template>

<script setup lang="ts">
import type { BillData } from '~/types/bill';

withDefaults(defineProps<{
	billData: BillData
	supplierDetailsCheck?: boolean
	buyerDetailsCheck?: boolean
}>(), {
	supplierDetailsCheck: true,
	buyerDetailsCheck: true,
})
</script>
