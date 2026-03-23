<template>
	<div>
		<textarea disabled class="w-full h-76 overflow-hidden resize-none">
Основные условия настоящего договора-счета № {{ billData.number || '—' }} от {{ normalizeDate(billData.date) || '—' }} г.
1. 	Предметом настоящего Счета-договора является поставка товарно-материальных ценностей (далее - "товар").
2. 	Оплата настоящего Счета-договора означает согласие Покупателя с условиями оплаты и поставки товара.	
3. 	Настоящий Счет-договор действителен в течение {{ billData.paymentTerms }} рабочих дней от даты его составления включительно. При отсутствии оплаты в указанный срок настоящий Счет-договор признается недействительным.
4. 	Поставщик обязан доставить оплаченный товар и передать его Покупателю в течение {{ billData.paymentTerms }} рабочих дней с момента зачисления оплаты на расчетный счет
5. 	Оплаченный товар доставляется Покупателю силами Поставщика
6. 	Оплата Счета-договора третьими лицами (сторонами), а также неполная (частичная) оплата Счета-договора не допускается. Покупатель не имеет права производить выборочную оплату позиций счета и требовать поставку товара по выбранным позициям.
7. 	Поставщик вправе не выполнять поставку товара до зачисления оплаты на расчетный счет.
8. 	Покупатель обязан принять оплаченный товар лично или через уполномоченного представителя. Передача товара осуществляется при предъявлении документа, удостоверяющего личность, и/или доверенности оформленной в установленном порядке.
9. 	Подписание Покупателем или его уполномоченным представителем товарной накладной означает согласие Покупателя с комплектностью и надлежащим качеством товара.
</textarea>
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

defineProps<{
	billData: BillData;
}>();
</script>
