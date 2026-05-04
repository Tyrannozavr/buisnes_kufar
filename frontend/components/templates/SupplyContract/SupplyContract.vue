<script setup lang="ts">
import { Editor, TemplateElement } from "~/constants/keys"
import { normalizePrice } from "~/utils/normalize"
import type { ProductsInOrder } from "~/types/order"
import type { SupplyContractData } from "~/types/supplyContract"

const supplyContractType = useTypedState(Editor.SUPPLY_CONTRACT_TYPE)
const supplyContractHTML = useTypedState(TemplateElement.SUPPLY_CONTRACT)
const specificationHTML = useTypedState(TemplateElement.SPECIFICATION)
const supplierDetailsCheck = useTypedState(Editor.SUPPLIER_DETAILS_CHECK)
const buyerDetailsCheck = useTypedState(Editor.BUYER_DETAILS_CHECK)
const isDisabled = useTypedState(Editor.IS_DISABLED)

//supply contract data
let seller: SupplyContractData['seller'] = {}
let buyer: SupplyContractData['buyer'] = {}
let products: SupplyContractData['products'] = []
let officials: SupplyContractData['officials'] = []

const supplyContractData = ref<SupplyContractData>({
	number: '',
	specificationNumber: '',
	specificationDate: '',
	date: '',
	seller,
	buyer,
	officials,
	products,
	amount: 0,
	amountExclVat: 0,
	amountVatRate: 0,
	amountWord: '',
	templateSupplyContract: '',
	templateSpecification: '',
})

const removeProduct = (product: ProductsInOrder) => {
	const index = supplyContractData.value.products.indexOf(product)
	if (index === -1) return
	supplyContractData.value.products.splice(index, 1)
}
</script>

<template>
	<!-- Преамбула -->
	<div v-if="supplyContractType === 'supplyContract'">
		<div>
			<h1 class="text-center font-bold">ДОГОВОР ПОСТАВКИ № ___________</h1>
		</div>
		<div class="flex justify-between">
			<span>г. __________</span>
			<span class="text-right">«____» _______________ 20____г.</span>
		</div>
		<br />

		<div>
			<!-- Поставщик -->
			<p v-if="supplyContractData.seller.companyType !== 'ИП'">
				{{supplyContractData.seller.companyName}} далее -
				<span class="font-bold">«Поставщик»</span>, от имени которого действует
				{{ supplyContractData.officials[0]?.position }} {{ supplyContractData.officials[0]?.name }}, действующего (ей) на основании {{ supplyContractData.officials[0]?.baseDocument }}
				{{ supplyContractData.officials[0]?.baseDocumentName }}, с одной стороны
			</p>
			<p v-else>
				{{ supplyContractData.seller.companyName }}, далее -
				<span class="font-bold">«Поставщик»</span>, зарегистрированный в реестре
				индивидуальных предпринимателей под № {{ supplyContractData.seller.ogrn }} с одной стороны
			</p>

			<!-- Покупатель -->
			<p v-if="supplyContractData.buyer.companyType !== 'ИП'">
				{{ supplyContractData.buyer.companyName }}, далее -
				<span class="font-bold">«Покупатель»</span>, от имени которого действует
				{{ supplyContractData.officials[0]?.position }} {{ supplyContractData.officials[0]?.name }}, действующего (ей) на основании {{ supplyContractData.officials[0]?.baseDocument }}
				{{ supplyContractData.officials[0]?.baseDocumentName }}, с другой стороны, далее совместно именуемые «Стороны»,
				заключили настоящий Договор поставки (далее именуемый «Договор») о
				нижеследующем:
			</p>
			<p v-else>
				{{ supplyContractData.buyer.companyName }}, далее -
				<span class="font-bold">«Покупатель»</span>, зарегистрированный в реестре
				индивидуальных предпринимателей под № {{ supplyContractData.buyer.ogrn }} с другой стороны, далее
				совместно именуемые «Стороны», заключили настоящий Договор поставки (далее
				именуемый «Договор») о нижеследующем:
			</p>
		</div>
	</div>
	<div v-else-if="supplyContractType === 'specification'">
		<div>
			<div class="text-right block">
				<p>Приложение</p>
				<p>к договору № {{ supplyContractData.number }}</p>
				<p>от {{ supplyContractData.date }}</p>
			</div>
		</div>
		<div>
			<h1 class="text-center ">Спецификация № {{ supplyContractData.specificationNumber }}</h1>
		</div>
	</div>
	<br />

	<div v-if="supplyContractType === 'specification'">
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
				<tr v-for="product in supplyContractData.products">
					<td class="border">
						<span>{{ supplyContractData.products.indexOf(product) + 1 }}</span>
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
						<span class="">{{ normalizePrice(product.amount) }}</span>
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
					<td @click="" colspan="7"
						class="border text-left text-gray-400 hover:text-gray-700 cursor-pointer">
						Добавить товар
					</td>
				</tr>

				<tr class="text-right">
					<td colspan="4"></td>
					<td colspan="2" >Итого:</td>
					<td >
						<span class="font-bold">{{ normalizePrice(supplyContractData.amountExclVat) }}</span>
					</td>
				</tr>
				<tr class="text-right">
					<td colspan="4"></td>
					<td colspan="2">В том числе НДС:</td>
					<td>
						<span class="font-bold">{{ normalizePrice(supplyContractData.amountVatRate) }}</span>
					</td>
				</tr>
				<tr class="text-right">
					<td colspan="4"></td>
					<td colspan="2">Всего к оплате:</td>
					<td>
						<span class="font-bold">{{ normalizePrice(supplyContractData.amount) }}</span>
					</td>
				</tr>
				
			</tbody> 
		</table>
	</div>

	<!-- Тело договора из редактора -->
	<div>
		<div v-if="supplyContractType === 'supplyContract'" v-html="supplyContractHTML"></div>
		<div v-else-if="supplyContractType === 'specification'" v-html="specificationHTML"></div>
	</div>
	<br />
	
	<!-- Реквизиты сторон -->
	<div>
		<table class="table_without_border">
			<tr class="font-bold">
				<td v-if="supplierDetailsCheck">ПОСТАВЩИК:</td>
				<td v-if="buyerDetailsCheck">ПОКУПАТЕЛЬ:</td>
			</tr>
			<tr class="font-bold">
				<td v-if="supplierDetailsCheck">{{ supplyContractData.seller.companyType }} {{ supplyContractData.seller.companyName }}</td>
				<!-- Поставщик -->
				<td v-if="buyerDetailsCheck">{{ supplyContractData.buyer.companyType }} {{ supplyContractData.buyer.companyName }}</td>
				<!-- Покупатель -->
			</tr>
			<tr>
				<td v-if="supplierDetailsCheck">{{ supplyContractData.seller.index }}, {{ supplyContractData.seller.legalAddress }}</td>
				<td v-if="buyerDetailsCheck">{{ supplyContractData.buyer.index }}, {{ supplyContractData.buyer.legalAddress }}</td>
			</tr>
			<tr>
				<td v-if="supplierDetailsCheck">ИНН {{ supplyContractData.seller.inn }}</td>
				<td v-if="buyerDetailsCheck">ИНН {{ supplyContractData.buyer.inn }}</td>
			</tr>
			<tr>
				<td v-if="supplierDetailsCheck">КПП {{ supplyContractData.seller.kpp }}</td>
				<td v-if="buyerDetailsCheck">КПП {{ supplyContractData.buyer.kpp }}</td>
			</tr>
			<tr>
				<td v-if="supplierDetailsCheck">Рас/счет № {{ supplyContractData.seller.accountNumber }} в {{ supplyContractData.seller.bankName }}</td>
				<td v-if="buyerDetailsCheck">Рас/счет № {{ supplyContractData.buyer.accountNumber }} в {{ supplyContractData.buyer.bankName }}</td>
			</tr>
			<tr>
				<td v-if="supplierDetailsCheck">{{ supplyContractData.seller.correspondentBankAccount }}</td>
				<td v-if="buyerDetailsCheck">{{ supplyContractData.buyer.correspondentBankAccount }}</td>
			</tr>
			<tr>
				<td v-if="supplierDetailsCheck">{{ supplyContractData.seller.bic }}</td>
				<td v-if="buyerDetailsCheck">{{ supplyContractData.buyer.bic }}</td>
			</tr>
			<tr>
				<td v-if="supplierDetailsCheck">{{ supplyContractData.seller.email }}</td>
				<td v-if="buyerDetailsCheck">{{ supplyContractData.buyer.email }}</td>
			</tr>
			<tr>
				<td v-if="supplierDetailsCheck">{{ supplyContractData.seller.phone }}</td>
				<td v-if="buyerDetailsCheck">{{ supplyContractData.buyer.phone }}</td>
			</tr>
			<!-- <tr class="h-5">
				<td></td>
				<td></td>
			</tr>
			<tr>
				<td>
					<div>
						<div class="h-5 flex justify-between">
							<span class="block mr-5">{ДОЛЖНОСТЬ}</span>
							<span class="block mr-5">{ФИО}</span>
						</div>
						<div class="text-center text-xs border-t mr-5">
							(должность, подпись, ФИО)
						</div>
					</div>
				</td>
				<td></td>
			</tr>
			<tr>
				<td></td>
				<td></td>
			</tr> -->
		</table>
	</div>
	<br />

	<!-- Подписи -->
	<div>
		<table class="table_without_border">
			<tr class="font-bold">
				<td>Поставщик:</td>
				<td>Покупатель:</td>
			</tr>
			<tr class="font-bold">
				<td>{{ supplyContractData.seller.companyType }} {{ supplyContractData.seller.companyName }}</td>
				<td>{{ supplyContractData.buyer.companyType }} {{ supplyContractData.buyer.companyName }}</td>
			</tr>
			<tr class="font-bold">
				<td>{{ supplyContractData.officials[0]?.position }} {{ supplyContractData.officials[0]?.name }}</td>
				<td>_____________(ДОЛЖНОСТЬ)</td>
			</tr>
			<!-- отступ -->
			<tr class="h-5">
				<td></td>
				<td></td>
			</tr>
			<tr>
				<td>______________________/{{ supplyContractData.officials[0]?.name }}/</td>
				<td>______________________/_______(ФИО)/</td>
			</tr>
			<tr class="font-bold">
				<td>«____» _______________ 20 г.</td>
				<td>«____» _______________ 20 г.</td>
			</tr>
			<tr>
				<td>М.П.</td>
				<td>М.П.</td>
			</tr>
		</table>
	</div>
</template>

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
	text-indent: 3em;
	line-height: 1.5em;
}

/* table,
th,
td {
	border: solid gray 1px;
	padding: 5px;
} */

.table_without_border {
	border: none;
}

.table_without_border td {
	border: none;
	padding: 1px;
}

input {
	line-height: 1.75;
	padding: 1px 5px;
	vertical-align: middle;
	field-sizing: content;
}
</style>
