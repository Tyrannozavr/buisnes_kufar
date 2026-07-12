<script setup lang="ts">
import { Editor, TemplateElement } from '~/constants/keys'
import { normalizeDate, normalizePrice, normalizeName } from '~/utils/normalize'
import { renderSupplyContractFields } from '~/utils/supplyContractFields'
import type { ProductsInOrder } from '~/types/order'
import type { SupplyContractData } from '~/types/supplyContract'
import type { Official, ProductItem } from '~/types/dealState'
import { useRoute, useRouter } from 'vue-router'
import { useDeals } from '~/composables/useDeals'
import { useUserStore } from '~/stores/user'
import { formatCompanyRecipientLine } from '~/utils/companyPartyLine'
import { useCompanyBillRequisites } from '~/composables/useCompanyBillRequisites'
import { useSaveDeals } from '~/composables/useSaveDeals'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const {
	deals,
	findDeal,
	deleteDeal,
	editSupplyContractNumber,
	editSupplyContractSpecificationNumber,
	editSupplyContractSpecificationDate,
	editSupplyContractOfficialsSeller,
	editSupplyContractTemplate,
	editSupplyContractSpecificationTemplate,
	editSupplyContractText,
	editSupplyContractSpecificationText,
	editSupplyContractSupplierDetailsCheck,
	editSupplyContractBuyerDetailsCheck,
	editSupplyContractCoverLetterCheck,
} = useDeals()
const { completeSave, saveState } = useSaveDeals()
const { loadBillRequisites, mergeDealPartyRequisites } = useCompanyBillRequisites()

const supplyContractType = useTypedState(Editor.SUPPLY_CONTRACT_TYPE)
const supplyContractHTML = useTypedState(TemplateElement.SUPPLY_CONTRACT)
const specificationHTML = useTypedState(TemplateElement.SPECIFICATION)
const supplierDetailsCheck = useTypedState(Editor.SUPPLIER_DETAILS_CHECK)
const buyerDetailsCheck = useTypedState(Editor.BUYER_DETAILS_CHECK)
const coverLetterCheck = useTypedState(Editor.COVER_LETTER_CHECK)
const clearState = useTypedState(Editor.CLEAR_STATE)
const removeDealState = useTypedState(Editor.REMOVE_DEAL)
const supplyContractOfficialsSeller = useTypedState(Editor.SUPPLY_CONTRACT_OFFICIALS_SELLER, () => ref<Official[]>([]))
const supplyContractTableData = useTypedState(Editor.SUPPLY_CONTRACT_TABLE_DATA)
const supplyContractSlotRevision = useTypedState(Editor.SUPPLY_CONTRACT_SLOT_REVISION, () => ref(0))
const loadDealTrigger = useTypedState(Editor.LOAD_DEAL_TRIGGER, () => ref(0))
const currentDeal = computed(() => findDeal(Number(route.query.dealId)))


let seller: SupplyContractData['seller'] = {}
let buyer: SupplyContractData['buyer'] = {}
let products: SupplyContractData['products'] = []
let officialsSeller: Official[] = []

const supplyContractData = ref<SupplyContractData>({
	dealId: 0,
	number: '',
	specificationNumber: '',
	specificationDate: '',
	date: '',
	seller,
	buyer,
	officialsSeller,
	products,
	amount: 0,
	amountExclVat: 0,
	amountVatRate: 0,
	amountWord: '',
	templateSupplyContract: '',
	templateSpecification: '',
})

//заполнение query
const fillQuery = () => {
	const query: Record<string, string> = { ...route.query } as Record<string, string>

	if (supplyContractData.value.dealId) {
		query.dealId = String(supplyContractData.value.dealId)
	}

	if (userStore.companyId === supplyContractData.value.buyer.companyId) {
		query.role = 'buyer'
	} else if (userStore.companyId === supplyContractData.value.seller.companyId) {
		query.role = 'seller'
	}

	router.replace({
		query,
		hash: '#supplyContract',
	})
}

//заполнение данных из сделки
const fillSupplyContractData = async () => {
	const deal = findDeal(Number(route.query.dealId))
	if (!deal) return

	const productList = deal.product.productList ?? []
	products = productList.map(
		(product: ProductItem): ProductsInOrder => ({
			name: product.name,
			article: product.article,
			quantity: product.quantity ?? 0,
			units: product.units ?? '',
			price: product.price ?? 0,
			amount: product.amount ?? 0,
		}),
	)

	const sellerData = deal.seller ?? {}
	seller = {
		ownerName: sellerData.ownerName,
		companyName: sellerData.companyName,
		companyType: sellerData.companyType,
		city: sellerData.city,
		fullName: sellerData.fullName,
		companyId: sellerData.companyId,
		phone: sellerData.phone,
		email: sellerData.email,
		legalAddress: sellerData.legalAddress,
		productionAddress: sellerData.productionAddress,
		index: sellerData.index,
		inn: Number(sellerData.inn) || 0,
		kpp: sellerData.kpp,
		ogrn: sellerData.ogrn,
		accountNumber: sellerData.accountNumber,
		correspondentBankAccount: sellerData.correspondentBankAccount,
		bankName: sellerData.bankName,
		bic: sellerData.bic,
		vatRate: sellerData.vatRate,
	}

	const buyerData = deal.buyer ?? {}
	buyer = {
		ownerName: buyerData.ownerName,
		companyName: buyerData.companyName,
		companyType: buyerData.companyType,
		city: buyerData.city,
		fullName: buyerData.fullName,
		companyId: buyerData.companyId,
		phone: buyerData.phone,
		email: buyerData.email,
		legalAddress: buyerData.legalAddress,
		productionAddress: buyerData.productionAddress,
		index: buyerData.index,
		inn: Number(buyerData.inn) || 0,
		kpp: buyerData.kpp,
		ogrn: buyerData.ogrn,
		accountNumber: buyerData.accountNumber,
		correspondentBankAccount: buyerData.correspondentBankAccount,
		bankName: buyerData.bankName,
		bic: buyerData.bic,
		vatRate: buyerData.vatRate,
	}

	const officialsData = deal.supplyContract.officialsSeller ?? []
	officialsSeller = officialsData.map(
		(official: Official): Official => ({
			id: official.id,
			companyId: official.companyId,
			name: official.name,
			position: official.position,
			isBase: official.isBase,
			baseDocument: official.baseDocument,
			baseDocumentName: official.baseDocumentName,
		}),
	)

	if (route.query.role === 'seller' && seller.companyId) {
		const fresh = await loadBillRequisites(seller.companyId)
		if (fresh) {
			seller = mergeDealPartyRequisites(seller, fresh.party)
			if (!officialsSeller.length && fresh.officials.length) {
				officialsSeller = fresh.officials.map((official) => ({
					id: official.id,
					companyId: seller.companyId,
					name: official.name,
					position: official.position,
					isBase: official.isBase,
					baseDocument: official.baseDocument,
					baseDocumentName: official.baseDocumentName,
				}))
			}
		}
	}

	supplyContractOfficialsSeller.value = [...officialsSeller]
	supplyContractHTML.value = deal.supplyContract.supplyContractText ?? ''
	specificationHTML.value = deal.supplyContract.specificationText ?? ''
	supplierDetailsCheck.value = true
	buyerDetailsCheck.value = true
	coverLetterCheck.value = deal.supplyContract.coverLetterCheck ?? false

	const contractDate = deal.supplyContractDate || deal.supplyContract.entityDate || ''
	const specNumber = (deal.supplyContract.specificationNumber ?? '').trim() || '1'
	const specDate = (deal.supplyContract.specificationDate ?? '').trim() || contractDate

	supplyContractData.value = {
		dealId: deal.dealId,
		number: deal.supplyContract.number ?? '',
		date: contractDate,
		specificationNumber: specNumber,
		specificationDate: specDate,
		seller,
		buyer,
		officialsSeller: [...officialsSeller],
		products: [...products],
		amount: deal.product.amountPrice,
		amountExclVat: deal.totalAmountExclVat,
		amountVatRate: deal.product.amountVatRate,
		amountWord: deal.product.amountWord,
		templateSupplyContract: deal.supplyContract.templateSupplyContract ?? '',
		templateSpecification: deal.supplyContract.templateSpecification ?? '',
	}

	supplyContractTableData.value = {
		products: supplyContractData.value.products,
		amount: supplyContractData.value.amount,
		amountExclVat: supplyContractData.value.amountExclVat,
		amountVatRate: supplyContractData.value.amountVatRate,
	}

	fillQuery()
	// recalcSupplyContractAmounts()
}

//заполнение данных из query
const fillFromQuery = async () => {
	const query = route.query
	if (!query?.dealId || !query?.role) return
	await fillSupplyContractData()
}

//заполнение данных из query
watch(
	() => [
		route.query.dealId,
		route.query.role,
		deals?.value?.length ?? 0,
		findDeal(Number(route.query.dealId))?.supplyContract?.number ?? '',
		loadDealTrigger.value,
	],
	() => fillFromQuery(),
	{ immediate: true, deep: true },
)

//заполнение данных должностных лиц из state
watch(
	() => supplyContractOfficialsSeller.value,
	() => {
		supplyContractData.value.officialsSeller = [...supplyContractOfficialsSeller.value]
	},
	{ deep: true, immediate: true },
)

const getRenderedSupplyContractHtml = (html: string | null | undefined): string =>
	renderSupplyContractFields(html, {
		seller: currentDeal.value?.seller ?? supplyContractData.value.seller,
		buyer: currentDeal.value?.buyer ?? supplyContractData.value.buyer,
		sellerOfficial: supplyContractOfficialsSeller.value[0],
		paymentTerms: currentDeal.value?.bill.paymentTermsContract,
		deliveryTerms: currentDeal.value?.bill.deliveryTermsContract,
	})

const renderedSupplyContractHTML = computed(() => getRenderedSupplyContractHtml(supplyContractHTML.value))
const renderedSpecificationHTML = computed(() => getRenderedSupplyContractHtml(specificationHTML.value))

watch(
	[renderedSupplyContractHTML, renderedSpecificationHTML],
	() => {
		supplyContractSlotRevision.value += 1
	},
)

//сохранение заказа в store при нажатии на кнопку сохранения в меню
watch(() => saveState,
	async () => {
		if (!saveState.value) return
		try {
			const dealId = supplyContractData.value.dealId

			if (route.query.role === 'seller') {
				const deal = findDeal(dealId)
				await editSupplyContractNumber(dealId, supplyContractData.value.number)
				await editSupplyContractSpecificationNumber(dealId, supplyContractData.value.specificationNumber)
				await editSupplyContractSpecificationDate(dealId, supplyContractData.value.specificationDate)
				await editSupplyContractOfficialsSeller(dealId, supplyContractData.value.officialsSeller)
				if (deal) {
					await editSupplyContractTemplate(dealId, deal.supplyContract.templateSupplyContract)
					await editSupplyContractSpecificationTemplate(dealId, deal.supplyContract.templateSpecification)
				}
				await editSupplyContractText(dealId, supplyContractHTML.value ?? '')
				await editSupplyContractSpecificationText(dealId, specificationHTML.value ?? '')
				await editSupplyContractSupplierDetailsCheck(dealId, supplierDetailsCheck.value ?? false)
				await editSupplyContractBuyerDetailsCheck(dealId, buyerDetailsCheck.value ?? false)
				await editSupplyContractCoverLetterCheck(dealId, coverLetterCheck.value ?? false)
			}
		} finally {
			completeSave()
		}
	},
	{ deep: true },
)

//очистка формы
const clearForm = () => {
	products = []
	seller = {}
	buyer = {}
	officialsSeller = []
	supplyContractOfficialsSeller.value = []

	supplyContractData.value = {
		dealId: 0,
		number: '',
		specificationNumber: '',
		specificationDate: '',
		date: '',
		seller,
		buyer,
		officialsSeller,
		products,
		amount: 0,
		amountExclVat: 0,
		amountVatRate: 0,
		amountWord: '',
		templateSupplyContract: '',
		templateSpecification: '',
	}
}

//очистка формы при нажатии на кнопку очистки в меню
watch(
	() => clearState.value,
	() => {
		if (clearState.value) clearForm()
	},
	{ deep: true },
)

//удаление сделки
const removeDeal = () => {
	deleteDeal(supplyContractData.value.dealId)
	clearForm()
}

//удаление сделки при нажатии на кнопку удаления в меню
watch(
	() => removeDealState.value,
	() => {
		if (removeDealState.value) removeDeal()
	},
	{ deep: true },
)
</script>

<template>
	<div>
	<!-- Преамбула -->
	<div v-if="supplyContractType === 'supplyContract'">
		<div>
			<h1 class="text-center font-bold">
				ДОГОВОР ПОСТАВКИ № {{ supplyContractData.number || '___________' }}
			</h1>
		</div>
		<div class="flex justify-between">
			<span>г. {{ supplyContractData.seller.city ?? '_________' }}</span>
			<span class="text-right">{{ normalizeDate(supplyContractData.date) ? `${normalizeDate(supplyContractData.date)} г.` : '«____» _______________ 20____г.' }}</span>
		</div>
		<br />

		<div>
			<!-- Поставщик -->
			<p v-if="supplyContractData.seller.companyType !== 'ИП'">
				{{ formatCompanyRecipientLine(supplyContractData.seller) }} далее -
				<span class="font-bold">«Поставщик»</span>, от имени которого действует
				{{ supplyContractOfficialsSeller[0]?.position || (supplyContractOfficialsSeller[0]?.name || supplyContractData.seller.ownerName ? 'Генеральный директор' : '') }}
				{{ supplyContractOfficialsSeller[0]?.name || supplyContractData.seller.ownerName || ' _____________' }}, действующего (ей) на основании {{ supplyContractOfficialsSeller[0]?.baseDocument }}
				{{ supplyContractOfficialsSeller[0]?.baseDocumentName ?? ' _____________' }}, с одной стороны
			</p>
			<p v-else>
				{{ formatCompanyRecipientLine(supplyContractData.seller) }}, далее -
				<span class="font-bold">«Поставщик»</span>, зарегистрированный в реестре
				индивидуальных предпринимателей под № {{ supplyContractData.seller.ogrn }} с одной стороны
			</p>

			<!-- Покупатель -->
			<p v-if="supplyContractData.buyer.companyType !== 'ИП'">
				{{ formatCompanyRecipientLine(supplyContractData.buyer) }}, далее -
				<span class="font-bold">«Покупатель»</span>, от имени которого действует
				{{ supplyContractData.buyer.ownerName || ' _____________' }}, действующего (ей) на основании
				{{ ' _____________' }}, с другой стороны, далее совместно именуемые «Стороны»,
				заключили настоящий Договор поставки (далее именуемый «Договор») о
				нижеследующем:
			</p>
			<p v-else>
				{{ formatCompanyRecipientLine(supplyContractData.buyer) }}, далее -
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
				<p>к договору № {{ supplyContractData.number || '—' }}</p>
				<p>от {{ normalizeDate(supplyContractData.date, true) || '—' }} г.</p>
			</div>
		</div>
		<div>
			<h1 class="text-center ">
				Спецификация № {{ supplyContractData.specificationNumber || '1' }}
			</h1>
		</div>
	</div>
	<br />

	<div v-if="supplyContractType === 'specification'">
		<table class="table-fixed p-5 mb-5 w-[99%]" id="products">
			<thead>
				<tr class="font-bold text-center">
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
				<tr v-for="product in supplyContractData.products" :key="product.article + product.name">
					<td class="text-center border">
						<span>{{ supplyContractData.products.indexOf(product) + 1 }}</span>
					</td>
					<td class="border">
						<span>{{ product.name }}</span>
					</td>
					<td class="border">
						<span>{{ product.article }}</span>
					</td>
					<td class="border">
						<span>{{ product.quantity }}</span>
					</td>
					<td class="border">
						<span>{{ product.units }}</span>
					</td>
					<td class="text-right border">
						<span>{{ normalizePrice(product.price) }}</span>
					</td>
					<td class="text-right border">
						<span class="">{{ normalizePrice(product.amount) }}</span>
					</td>
					<td>
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

	<div v-if="supplyContractType === 'specification'">
		<span>
			Всего наименований: 
			<span class="font-bold">
				{{ supplyContractData.products.length }}
			</span>
			, на сумму:
			<span class="font-bold">
				{{ normalizePrice(supplyContractData.amount) }} p.
			</span> 
		</span>
	</div>
	<div v-if="supplyContractType === 'specification'">
		<span class="underline underline-offset-4">
			<span class="font-bold">{{ supplyContractData.amountWord }}</span>
		</span>
	</div>
	<br>

	<!-- Тело договора из редактора -->
	<div>
		<div v-if="supplyContractType === 'supplyContract'" v-html="renderedSupplyContractHTML"></div>
		<div v-else-if="supplyContractType === 'specification'" v-html="renderedSpecificationHTML"></div>
	</div>
	<br />

	<!-- Реквизиты сторон -->
	<div>
		<table class="table_without_border w-full">
			<tr class="font-bold">
				<td v-if="supplierDetailsCheck" class="w-1/2">ПОСТАВЩИК:</td>
				<td v-if="buyerDetailsCheck" class="w-1/2">ПОКУПАТЕЛЬ:</td>
			</tr>
			<tr class="font-bold">
				<td v-if="supplierDetailsCheck">{{ formatCompanyRecipientLine(supplyContractData.seller) }}</td>
				<td v-if="buyerDetailsCheck">{{ formatCompanyRecipientLine(supplyContractData.buyer) }}</td>
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
		</table>
	</div>
	<br />

	<!-- Подписи -->
	<div>
		<table class="table_without_border w-full">
			<tr class="font-bold">
				<td class="w-1/2">Поставщик:</td>
				<td class="w-1/2">Покупатель:</td>
			</tr>
			<tr class="font-bold">
				<td>{{ formatCompanyRecipientLine(supplyContractData.seller) }}</td>
				<td>{{ formatCompanyRecipientLine(supplyContractData.buyer) }}</td>
			</tr>
			<tr class="font-bold">
				<td>{{ supplyContractOfficialsSeller[0]?.position || (supplyContractOfficialsSeller[0]?.name || supplyContractData.seller.ownerName ? 'Генеральный директор' : '_________________(ДОЛЖНОСТЬ)') }}</td>
				<td>_________________(ДОЛЖНОСТЬ)</td>
			</tr>
			<tr class="h-5">
				<td></td>
				<td></td>
			</tr>
			<tr>
				<td>______________________/{{ normalizeName(supplyContractOfficialsSeller[0]?.name || supplyContractData.seller.ownerName || '_____________(ФИО)') }}/</td>
				<td>_______________/{{ normalizeName(supplyContractData.buyer.ownerName || '_____________(ФИО)') }}/</td>
			</tr>
			<tr class="font-bold">
				<td>«____» _______________ 20__г.</td>
				<td>«____» _______________ 20__г.</td>
			</tr>
			<tr>
				<td>М.П.</td>
				<td>М.П.</td>
			</tr>
		</table>
	</div>
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
