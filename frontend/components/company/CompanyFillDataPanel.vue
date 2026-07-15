<script setup lang="ts">
import CompanyAddressList from '~/components/company/CompanyAddressList.vue'
</script>

<template>
	<div class="space-y-6">
		<p class="text-sm text-gray-600">
			Адреса используются при заполнении документов. Если адрес один — он автоматически
			становится значением по умолчанию.
		</p>
		<CompanyAddressList
			kind="loading"
			title="Адрес места погрузки товара"
			hint="Адреса, откуда организация отправляет груз покупателю."
		/>
		<CompanyAddressList
			kind="receiving"
			title="Адрес места приема груза"
			hint="Адреса, где организация принимает груз от поставщика."
		/>
	</div>
</template>
