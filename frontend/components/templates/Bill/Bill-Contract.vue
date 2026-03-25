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
					<!-- 1 ТИП ОРГАНИЗАЦИИ «НАЗВАНИЕ ОРГАНИЗАЦИИ» -->
					<td>{{ billData.seller.companyName }}</td>
					<td>{{ billData.buyer.companyName }}</td>
				</tr>
				<tr>
					<!-- 2 ИНДЕКС, ЮРИДИЧЕСКИЙ АДРЕС-->
					<td>{{ billData.seller.index }} {{ billData.seller.legalAddress }}</td>
					<td>{{ billData.buyer.index }} {{ billData.buyer.legalAddress }}</td>
				</tr>
				<tr>
					<!-- 3 ИНН ИНН, КПП КПП -->
					<td>ИНН: {{ billData.seller.inn }} КПП: {{ billData.seller.kpp }}</td>
					<td>ИНН: {{ billData.buyer.inn }} КПП: {{ billData.buyer.kpp }}</td>
				</tr>
				<tr>
					<!-- 4 Рас/счет № РАСЧЕТНЫЙ СЧЕТ в	Рас/счет № РАСЧЕТНЫЙ СЧЕТ в
НАЗВАНИЕ БАНКА	НАЗВАНИЕ БАНКА
-->
					<td>Рас/счет №: {{ billData.seller.accountNumber }}</td>
					<td>Рас/счет №: {{ billData.buyer.accountNumber }}</td>
				</tr>
				<tr>
					<!-- 5 КОРР.СЧЕТ БАНКА -->
					<td>Корр/счет: {{ billData.seller.correspondentBankAccount }} <br> Банк: {{ billData.seller.bankName }}</td>
					<td>Корр/счет: {{ billData.buyer.correspondentBankAccount }} <br> Банк: {{ billData.buyer.bankName }}</td>
				</tr>
				<tr>
					<!-- 6 БИК-->
					<td>БИК: {{ billData.seller.bic }}</td>
					<td>БИК: {{ billData.buyer.bic }}</td>
				</tr>
				<!-- 7 -->
				<tr class="h-5">
				</tr>
				<!-- 8 ДОЛЖНОСТЬ	___	ФИО -->
				<tr v-for="official in billData.officials" :key="official.id">
					<td>
						<div>
							<div class="h-5 flex justify-between">
								<span class="block mr-5">{{ official.position }}</span>
								<span class="block mr-5">{{ official.name }}</span>
							</div>
							<div class="text-center text-xs border-t mr-5">(должность, подпись, ФИО)</div>
						</div>
					</td>
					<td>
						<div>
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

const { billData } = defineProps<{
	billData: BillData;
}>();
</script>
