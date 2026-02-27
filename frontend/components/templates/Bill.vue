<template>
	<div class="font-sans text-l text-justify text-pretty w-full">
		<div v-if="error" class="mb-2 text-red-600 text-sm">{{ error }}</div>
		<div v-if="dealId" class="mb-2 flex gap-2 items-center">
			<UButton
				size="sm"
				:loading="saving"
				:disabled="loading"
				@click="save()"
			>
				Сохранить документ
			</UButton>
			<span v-if="updatedAt" class="text-gray-500 text-sm">Сохранено: {{ updatedAt }}</span>
		</div>

		<table class="p-3 w-full border-2 border-black">
			<tbody>
				<tr>
					<td colspan="4" rowspan="1">
						<textarea placeholder="OФП, Название компании, город" :disabled="isDisabled" class="w-full" v-model="payload.ofpCompany"/>
						<br />
						<br />
						<br />
						<br />
					</td>
					<td class="border">БИК</td>
					<td>
						<textarea placeholder="номер БИК" :disabled="isDisabled" class="w-full" v-model="payload.bik"/>
					</td>
				</tr>

				<tr class="border-b-2 black">
					<td colspan="4" class="border">
						<textarea placeholder="Банк получателя" :disabled="isDisabled" class="w-full" v-model="payload.bankName"/>
					</td>
					<td class="border">Сч. №</td>
					<td>
						<textarea placeholder="номер счёта" :disabled="isDisabled" class="w-full" v-model="payload.accountNumber"/>
					</td>
				</tr>

				<tr>
					<td class="border">ИНН</td>
					<td class="border">
						<textarea placeholder="ИНН" :disabled="isDisabled" class="w-full" v-model="payload.inn"/>
					</td>
					<td class="border">КПП</td>
					<td class="border">
						<textarea placeholder="КПП" :disabled="isDisabled" class="w-full" v-model="payload.kpp"/>
					</td>
					<td rowspan="3" class="border">Сч. №</td>
					<td rowspan="3">
						<textarea placeholder="Расчетный счёт" :disabled="isDisabled" class="w-full" v-model="payload.settlementAccount"/>
					</td>
				</tr>

				<tr>
					<td colspan="4">
						<textarea placeholder="ОФП, Название компании" :disabled="isDisabled" class="w-full" v-model="payload.companyName"/>
						<br>
						<br>
						<br>
					</td>
				</tr>

				<tr>
					<td colspan="4" class="border">
						<textarea placeholder="Получатель" :disabled="isDisabled" class="w-full" v-model="payload.recipient"/>
					</td>
				</tr>
			</tbody>
		</table>

		<h2 class="font-bold text-2xl">Счёт на оплату № {{ billNumber || '—' }} от {{ billDateFormatted }} г.</h2>
		<hr class="border-2">
		<br>
		<table>
			<tbody>
			<tr>
				<td>
					<p>Поставщик 
						<br>
						(исполнитель):</p>
				</td>
				<td>
					<textarea placeholder="Поставщик" :disabled="isDisabled" class="w-full" v-model="payload.supplier"/>
				</td>
			</tr>
			<tr>
				<td>
					<p>Покупатель 
						<br>
						(заказчик):</p>
				</td>
				<td>
					<textarea placeholder="Покупатель" :disabled="isDisabled" class="w-full" v-model="payload.buyer"/>
				</td>
			</tr>
			<tr v-if="reason">
				<td>
					<p>Основание: </p>
				</td>
				<td>
					<textarea placeholder="Основание" :disabled="isDisabled" class="w-full" v-model="payload.reason"/>
				</td>
			</tr>
			</tbody>
		</table>

		<br>

		<table class="table-fixed p-5 mb-5 w-[99%] text-center" id="products">
			<thead>
				<tr>
					<td class="w-5 border"><span>№</span></td>
					<td class="w-50 border"><span>Название продукта</span></td>
					<td class="w-15 border"><span>Артикул</span></td>
					<td class="w-10 border"><span>Кол-во</span></td>
					<td class="w-13 border"><span>Ед. изм.</span></td>
					<td class="w-15 border"><span>Цена</span></td>
					<td class="w-20 border"><span>Сумма</span></td>
					<td class="w-1"><span></span></td>
				</tr>
			</thead>
			<tbody>
				<!-- <tr v-for="product in orderData.products">
					<td class="border">
						<span>{{ orderData.products.indexOf(product) + 1 }}</span>
					</td>
					<td class="border">
						<input :disabled="isDisabled" class="w-72" placeholder="Название" v-model.lazy="product.name" />
					</td>
					<td class="border">
						<input :disabled="isDisabled" class="w-21 text-center" placeholder="Артикул"
							v-model.lazy="product.article" />
					</td>
					<td class="border">
						<input :disabled="isDisabled" class="w-14 text-center" placeholder="Кол-во"
							v-model.lazy="product.quantity" />
					</td>
					<td class="border">
						<input :disabled="isDisabled" class="w-18 text-center" placeholder="Ед. изм."
							v-model.lazy="product.units" />
					</td>
					<td class="border">
						<input :disabled="isDisabled" class="w-21 text-center" placeholder="Цена" v-model.lazy="product.price" />
					</td>
					<td class="border">
						<span class="">{{ product.amount }}</span>
					</td>
					<td>
						<span :hidden="isDisabled" class="w-[10px] cursor-pointer" @click="removeProduct(product)">
							<svg class="w-7 h-5 fill-none stroke-neutral-400 hover:stroke-red-400" xmlns="http://www.w3.org/2000/svg"
								width="32" height="32" viewBox="0 0 24 24">
								<g class="fill-white stroke-neutral-400 hover:stroke-red-400" stroke-linecap="round"
									stroke-linejoin="round" stroke-width="3">
									<circle cx="12" cy="12" r="10" />
									<path d="m15 9l-6 6m0-6l6 6" />
								</g>
							</svg>
						</span>
					</td>
				</tr> -->

				<!-- <tr :hidden="isDisabled">
					<td @click="addProduct()" colspan="7"
						class="border text-left text-gray-400 hover:text-gray-700 cursor-pointer">
						Добавить товар
					</td>
				</tr> -->

				<tr class="text-right">
					<td colspan="4"></td>
					<td colspan="2" >Итого:</td>
					<td>
						<!-- товары * кол-во -->
					</td>
				</tr>
				<tr class="text-right">
					<td colspan="4"></td>
					<td colspan="2">В том числе НДС:</td>
					<td>
						<!-- итого * %НДС -->
					</td>
				</tr>
				<tr class="text-right">
					<td colspan="4"></td>
					<td colspan="2">Всего к оплате:</td>
					<td>
						<!-- итого + НДС -->
					</td>
				</tr>
				
			</tbody> 
		</table>

		<p>
			<span>
				Всего наименований: , на сумму:
				<span > 
					<!-- price -->
					{{  }} 
				</span>
				p.
			</span>
		</p>
		<div>
			<span class="underline underline-offset-4">
				<!-- {{ amountWord }} -->
			</span>
			<p v-if="dueDateCheck">
				<span>Срок оплаты: {{ dueDate }}</span>
			</p>
		</div>

		<br>

		<p>
		<textarea v-if="additionalInfo" class="w-full h-30 p-1">
Внимание!
Оплата данного счета означает согласие с условиями поставки товара.
Уведомление об оплате обязательно, в противном случае не гарантируется наличие товара на складе.
Товар отпускается по факту прихода денег на р/с Поставщика, самовывозом, при наличии доверенности и паспорта.
		</textarea>
		</p>

		<br>
		<hr class="border-2">
		<br>

		<table class="w-full">
			<tbody>
				<tr>
					<td>Руководитель</td>
					<td class="w-2/5 max-w-3/4 border-b-1">
						<textarea placeholder="Руководитель" :disabled="isDisabled" class="w-full" v-model="payload.leader"/>
					</td>
					<td>Бухгалтер</td>
					<td class="w-2/5 max-w-3/4 border-b-1">
						<textarea placeholder="Бухгалтер" :disabled="isDisabled" class="w-full" v-model="payload.accountant"/>
					</td>
				</tr>
			</tbody>
		</table>

	</div>
</template>

<script setup lang="ts">
import { useDocxGenerator } from '~/composables/useDocxGenerator';
import { Editor } from '~/constants/keys';
import { useRoute } from 'vue-router';
import { usePurchasesStore } from '~/stores/purchases';
import { useSalesStore } from '~/stores/sales';
import { normalizeDate } from '~/utils/normalize';
import { useDocumentForm } from '~/composables/useDocumentForm';
import { computed } from 'vue';

const route = useRoute();
const purchasesStore = usePurchasesStore();
const salesStore = useSalesStore();

const dealId = computed(() => {
	const q = route.query.dealId ?? route.query.deal_id;
	return q ? Number(q) : null;
});

const initialPayload: Record<string, string> = {
	ofpCompany: '',
	bik: '',
	bankName: '',
	accountNumber: '',
	inn: '',
	kpp: '',
	recipient: '',
	companyName: '',
	supplier: '',
	buyer: '',
	reason: '',
	leader: '',
	accountant: '',
};

const {
	payload,
	loading,
	saving,
	error,
	updatedAt,
	save,
} = useDocumentForm({
	slot: 'bill',
	dealId,
	initialPayload,
});

const billNumber = computed(() => {
  const q = route.query;
  if (!q?.dealId || !q?.role || !q?.productType) return '';
  const dealId = Number(q.dealId);
  if (q.role === 'buyer') {
    const deal = q.productType === 'goods'
      ? purchasesStore.findGoodsDeal(dealId)
      : purchasesStore.findGoodsDeal(dealId);
    return deal?.billNumber ?? '';
  }
  const deal = q.productType === 'goods'
    ? salesStore.findGoodsDeal(dealId)
    : salesStore.findGoodsDeal(dealId);
  return deal?.billNumber ?? '';
});

const billDateFormatted = computed(() => {
  const q = route.query;
  if (!q?.dealId || !q?.role || !q?.productType) return '—';
  const dealId = Number(q.dealId);
  let dateStr = '';
  if (q.role === 'buyer') {
    const deal = q.productType === 'goods'
      ? purchasesStore.findGoodsDeal(dealId)
      : purchasesStore.findGoodsDeal(dealId);
    dateStr = deal?.billDate ?? '';
  } else {
    const deal = q.productType === 'goods'
      ? salesStore.findGoodsDeal(dealId)
      : salesStore.findGoodsDeal(dealId);
    dateStr = deal?.billDate ?? '';
  }
  return dateStr ? normalizeDate(dateStr) : '—';
});

const { generateDocxBill, downloadBlob } = useDocxGenerator()
const reason = useTypedState(Editor.REASON)
const dueDateCheck = useTypedState(Editor.DUE_DATE_CHECK)
const dueDate = useTypedState(Editor.DUE_DATE)
const additionalInfo = useTypedState(Editor.ADDITIOANAL_INFO)
const vatRateCheck = useTypedState(Editor.VAT_RATE_CHECK)
const vatRate = useTypedState(Editor.VAT_RATE)
const isDisabled = useTypedState(Editor.IS_DISABLED)
const data = {}

const docxBill = await generateDocxBill(data)

</script>

<style lang="css" scoped>
* {
	line-height: 1.2em;
}


h1,
h2 {
	text-align: center;
	line-height: 3em;
}


p {
	text-indent: 0em;
	line-height: 1.5em;
}

/* table,
th,
td {
	border: solid gray 1px;
	padding: 5px;
} */

input,
textarea {
	/* margin: 3px 0 3px 3px; */
	line-height: 1.75;
	padding: 1px 5px;
	vertical-align: middle;
	field-sizing: content;
}
</style>