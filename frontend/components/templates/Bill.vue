<template>
	<div class="font-serif text-l text-justify text-pretty w-full">
		<p>Индивидуальный предприниматель {ФИОИП}</p>
		<p>{АдресДляДокументов}</p>
		<p>{КонтактныеДанные}</p>
		<br />

		<table class="p-3">
			<tr>
				<td colspan="4" rowspan="2">{НаименованиеБанкаИГородБанка}<br />Банк получателя</td>
				<td>БИК</td>
				<td rowspan="2">{НаименованиеБанкаИГородБанка}<br /> {БИК}
					{КоррСчет}
				</td>
			</tr>
			<tr>
				<td>Сч. №</td>
			</tr>
			<tr>
				<td>ИНН</td>
				<td>{ИНН}</td>
				<td>КПП</td>
				<td>{КПП}</td>
				<td rowspan="2">Сч. №</td>
				<td rowspan="2">{РасчетныйСчет}</td>
			</tr>
			<tr>
				<td colspan="4">Индивидуальный предприниматель {ФИОИП} <br />
					Получатель
				</td>
			</tr>
		</table>

		<h2 class="font-bold">Счёт № {НомерДокумента} от {ДатаДокумента}</h2>
		<p>Поставщик: {ФИОИП}</p>
		<p>Покупатель: {НазваниеКонтр}, {ИННКонтр}, {КППКонтр}</p>

		<p>{ФактурнаяЧасть}</p>
		<p>Всего к оплате: {СуммаДокументаПрописью}.</p>
		<strong>________________________________________</strong>

		<p>{Комментарий}</p>

		<pre class="font-serif">


Поставщик 	<span class="underline underline-offset-4">Индивидуальный предприниматель м.п.</span>	<span class="underline underline-offset-4">                                          </span>	<span class="underline underline-offset-4">{ФИОДляПодписи}</span>
														<span class="text-sm">должность 												подпись				расшифровка подписи</span>
</pre>

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

table,
th,
td {
	border: solid gray 1px;
	padding: 5px;
}
</style>