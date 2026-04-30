<script setup lang="ts">
import { Editor, TemplateElement } from "~/constants/keys"

const supplyContractHTML = useTypedState(TemplateElement.SUPPLY_CONTRACT)
const supplierDetailsCheck = useTypedState(Editor.SUPPLIER_DETAILS_CHECK)
const buyerDetailsCheck = useTypedState(Editor.BUYER_DETAILS_CHECK)

watch(
	supplyContractHTML,
	(newVal) => {
		console.log(newVal)
	},
	{ deep: true, immediate: true }
)

// mocks
const sellerCompanyType = ref<"ООО" | "ИП">("ООО")
const buyerCompanyType = ref<"ООО" | "ИП">("ИП")
</script>

<template>
	<!-- Преамбула -->
	<div>
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
			<p v-if="sellerCompanyType !== 'ИП'">
				{ПОЛНОЕ НАЗВАНИЕ ОРГАНИЗАЦИИ}, далее -
				<span class="font-bold">«Поставщик»</span>, от имени которого действует
				{ДОЛЖНОСТЬ ФИО}, действующего (ей) на основании {ДОКУМЕНТ ОСНОВАНИЯ}
				{НАЗВАНИЕ ДОКУМЕНТА}, с одной стороны
			</p>
			<p v-else>
				{ПОЛНОЕ НАЗВАНИЕ ОРГАНИЗАЦИИ}, далее -
				<span class="font-bold">«Поставщик»</span>, зарегистрированный в реестре
				индивидуальных предпринимателей под № {ОГРН} с одной стороны
			</p>

			<!-- Покупатель -->
			<p v-if="buyerCompanyType !== 'ИП'">
				{ПОЛНОЕ НАЗВАНИЕ ОРГАНИЗАЦИИ}, далее -
				<span class="font-bold">«Покупатель»</span>, от имени которого действует
				{ДОЛЖНОСТЬ ФИО}, действующего (ей) на основании {ДОКУМЕНТ ОСНОВАНИЯ}
				{НАЗВАНИЕ ДОКУМЕНТА}, с другой стороны, далее совместно именуемые «Стороны»,
				заключили настоящий Договор поставки (далее именуемый «Договор») о
				нижеследующем:
			</p>
			<p v-else>
				{ПОЛНОЕ НАЗВАНИЕ ОРГАНИЗАЦИИ}, далее -
				<span class="font-bold">«Покупатель»</span>, зарегистрированный в реестре
				индивидуальных предпринимателей под № {ОГРН} с другой стороны, далее
				совместно именуемые «Стороны», заключили настоящий Договор поставки (далее
				именуемый «Договор») о нижеследующем:
			</p>
		</div>
	</div>
	<br />

	<!-- Тело договора из редактора -->
	<div>
		<div v-html="supplyContractHTML"></div>
	</div>

	<!-- Реквизиты сторон -->
	<div>
		<table class="table_without_border">
			<tr class="font-bold">
				<td v-if="supplierDetailsCheck">ПОСТАВЩИК:</td>
				<td v-if="buyerDetailsCheck">ПОКУПАТЕЛЬ:</td>
			</tr>
			<tr class="font-bold">
				<td v-if="supplierDetailsCheck">{ТИП ОРГАНИЗАЦИИ} {«НАЗВАНИЕ ОРГАНИЗАЦИИ»}</td>
				<!-- Поставщик -->
				<td v-if="buyerDetailsCheck">{ТИП ОРГАНИЗАЦИИ} {«НАЗВАНИЕ ОРГАНИЗАЦИИ»}</td>
				<!-- Покупатель -->
			</tr>
			<tr>
				<td v-if="supplierDetailsCheck">{ИНДЕКС}, {ЮРИДИЧЕСКИЙ АДРЕС}</td>
				<td v-if="buyerDetailsCheck">{ИНДЕКС}, {ЮРИДИЧЕСКИЙ АДРЕС}</td>
			</tr>
			<tr>
				<td v-if="supplierDetailsCheck">ИНН {ИНН}</td>
				<td v-if="buyerDetailsCheck">ИНН {ИНН}</td>
			</tr>
			<tr>
				<td v-if="supplierDetailsCheck">КПП {КПП}</td>
				<td v-if="buyerDetailsCheck">КПП {КПП}</td>
			</tr>
			<tr>
				<td v-if="supplierDetailsCheck">Рас/счет № {РАСЧЕТНЫЙ СЧЕТ} в {НАЗВАНИЕ БАНКА}</td>
				<td v-if="buyerDetailsCheck">Рас/счет № {РАСЧЕТНЫЙ СЧЕТ} в {НАЗВАНИЕ БАНКА}</td>
			</tr>
			<tr>
				<td v-if="supplierDetailsCheck">{КОРР.СЧЕТ БАНКА}</td>
				<td v-if="buyerDetailsCheck">{КОРР.СЧЕТ БАНКА}</td>
			</tr>
			<tr>
				<td v-if="supplierDetailsCheck">{БИК}</td>
				<td v-if="buyerDetailsCheck">{БИК}</td>
			</tr>
			<tr>
				<td v-if="supplierDetailsCheck">{email}</td>
				<td v-if="buyerDetailsCheck">{email}</td>
			</tr>
			<tr>
				<td v-if="supplierDetailsCheck">{phone}</td>
				<td v-if="buyerDetailsCheck">{phone}</td>
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
				<td>{ТИП ОРГАНИЗАЦИИ} {«НАЗВАНИЕ ОРГАНИЗАЦИИ»}</td>
				<td>{ТИП ОРГАНИЗАЦИИ} {«НАЗВАНИЕ ОРГАНИЗАЦИИ»}</td>
			</tr>
			<tr class="font-bold">
				<td>{ДОЛЖНОСТЬ}</td>
				<td>{ДОЛЖНОСТЬ}</td>
			</tr>
			<!-- отступ -->
			<tr class="h-5">
				<td></td>
				<td></td>
			</tr>
			<tr>
				<td>______________________/{ФИО}/</td>
				<td>______________________/{ФИО}/</td>
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

table,
th,
td {
	border: solid gray 1px;
	padding: 5px;
}

.table_without_border {
	border: none;
}

.table_without_border td {
	border: none;
	padding: 1px;
}
</style>
