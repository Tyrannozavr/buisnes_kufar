<template>
	<div>
		<div v-if="additionalInfoCheckOffer" class="w-full mb-4">
			<p v-for="line in billData.additionalInfoOffer.split('\n')" :key="line">{{ replaceFields(line, billData) }}</p>
		</div>

		<div v-if="billData.contractTermsTextOffer" class="w-full">
			<p class="underline">Условия счета-оферты:</p>
			<div>
				<p v-for="line in billData.contractTermsTextOffer.split('\n')" :key="line">{{ replaceFields(line, billData) }}</p>
			</div>
		</div>

		<div class="w-2/5 mt-6">
			<div class="h-5"></div>
			<div class="text-center text-xs border-t">(должность, подпись, ФИО)</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import type { BillData } from '~/types/bill';

defineProps<{
	billData: BillData;
	additionalInfoCheckOffer: boolean;
}>();
</script>