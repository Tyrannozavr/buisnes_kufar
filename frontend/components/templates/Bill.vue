<template>
	<div class="font-sans text-l text-justify text-pretty w-full">
		
		<table class="p-3 w-full border-2 border-black">
			
			<tr>
				<td colspan="4" rowspan="1">OФП, Название компании, город
					<br />
					<br />
					<br />
					<br />
				</td>
				<td class="border">БИК</td>
				<td> номер БИК</td>
			</tr>

			<tr class="border-b-2 black">
				<td colspan="4" class="border">Банк получателя</td>
				<td class="border">Сч. №</td>
				<td>номер счета </td>
			</tr>

			<tr>
				<td class="border">ИНН</td>
				<td class="border">{ИНН}</td>
				<td class="border">КПП</td>
				<td class="border">{КПП}</td>
				<td rowspan="3" class="border">Сч. №</td>
				<td rowspan="3">{РасчетныйСчет}</td>
			</tr>

			<tr>
				<td colspan="4">
					ОФП, Название компании
					<br>
					<br>
					<br>
				</td>
			</tr>

			<tr>
				<td colspan="4" class="border">
					Получатель
				</td>
			</tr>

		</table>

		<h2 class="font-bold text-2xl">Счёт на оплату № ... от ... г.</h2>
		<hr>
		<br>
		<table>
			<tr>
				<td>
					<p>Поставщик 
						<br>
						(исполнитель):</p>
				</td>
				<td><input /></td>
			</tr>
			<tr>
				<td>
					<p>Покупатель 
						<br>
						(заказчик):</p>
				</td>
				<td><input /></td>
			</tr>
		</table>

		<br>

		<table class="table-fixed p-5 mb-5 w-[99%] text-center" id="products">
			<thead>
				<th class="w-5 border"><span>№</span></th>
				<th class="w-50 border"><span>Название продукта</span></th>
				<th class="w-15 border"><span>Артикул</span></th>
				<th class="w-10 border"><span>Кол-во</span></th>
				<th class="w-13 border"><span>Ед. изм.</span></th>
				<th class="w-15 border"><span>Цена</span></th>
				<th class="w-20 border"><span>Сумма</span></th>
				<th class="w-1"><span></span></th>
			</thead>
			<!-- <tbody>
				<tr v-for="product in orderData.products">
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

				</tr>
				<tr :hidden="isDisabled">
					<td @click="addProduct()" colspan="7"
						class="border text-left text-gray-400 hover:text-gray-700 cursor-pointer">
						Добавить товар
					</td>
				</tr>
			</tbody> -->
		</table>

		<p>
			<!-- <span>
				Всего наименований:{{ orderData.products.length }}, на сумму:
				<span v-if="orderData.amount"> 
					{{ orderData.amount }} 
				</span>
				p.
			</span> -->
		</p>
		<p>
			<span class="underline underline-offset-4">
				<!-- {{ orderData.amountWord }} -->
			</span>
		</p>

		<br>

		<p>
		<pre>

Внимание!
Оплата данного счета означает согласие с условиями поставки товара.
Уведомление об оплате обязательно, в противном случае не гарантируется наличие товара 
на складе.
Товар отпускается по факту прихода денег на р/с Поставщика, самовывозом, при наличии 
доверенности и паспорта.
			</pre>
		</p>

		<br>
		<hr>
		<br>

		<table class="w-full">
			<tr>
				<td>Руководитель</td>
				<td class="w-2/5 border-b-1"></td>
				<td>Бухгалтер</td>
				<td class="w-2/5 border-b-1"></td>
			</tr>
		</table>

	</div>
</template>

<script setup lang="ts">
import { useDocxGenerator } from '~/composables/useDocxGenerator';

const { generateDocxBill, downloadBlob } = useDocxGenerator()

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
</style>