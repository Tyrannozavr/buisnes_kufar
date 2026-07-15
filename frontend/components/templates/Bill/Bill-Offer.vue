<template>
	<div>
		<div v-if="additionalInfoCheckOffer" class="w-full mb-4">
			<template v-if="!isDisabled">
				<p class="text-xs text-neutral-500 mb-1">
					Доп. информация оферты
					<span class="text-neutral-400">(можно редактировать)</span>
				</p>
				<textarea
					class="w-full min-h-24 text-sm border border-dashed border-neutral-300 rounded px-2 py-1 bg-amber-50/40 focus:bg-white focus:border-solid focus:border-neutral-400 focus:outline-none"
					:value="billData.additionalInfoOffer"
					placeholder="Введите дополнительную информацию…"
					title="Редактируемое поле — текст попадёт в DOC/PDF"
					@input="onAdditionalInfoInput"
				/>
			</template>
			<template v-else>
				<p
					v-for="(line, idx) in additionalInfoOffer.split('\n')"
					:key="`ai-${idx}-${line.slice(0, 24)}`"
				>
					{{ replaceFields(line, billData, 'bill-offer') }}
				</p>
			</template>
		</div>

		<div v-if="visibleTermsLines.length" class="w-full">
			<p class="underline">Условия счета-оферты:</p>
			<div>
				<p
					v-for="(line, idx) in visibleTermsLines"
					:key="`ct-${idx}-${line.slice(0, 24)}`"
				>
					{{ replaceFields(line, billData, 'bill-offer') }}
				</p>
			</div>
		</div>

		<div class="w-2/5 mt-6">
			<div class="h-5"></div>
			<div class="text-center text-xs border-t">(должность, подпись, ФИО)</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import type { BillData } from '~/types/bill'
import { Editor } from '~/constants/keys'
import { filterTermsLinesByChecks, replaceFields } from '~/utils/replace'

const props = defineProps<{
	billData: BillData
	additionalInfoCheckOffer: boolean
	paymentTermsCheckOffer?: boolean
}>()

const isDisabled = useTypedState(Editor.IS_DISABLED)

const additionalInfoOffer = computed(() => props.billData.additionalInfoOffer || '')

const onAdditionalInfoInput = (e: Event) => {
	props.billData.additionalInfoOffer = (e.target as HTMLTextAreaElement).value
}

const visibleTermsLines = computed(() =>
	filterTermsLinesByChecks(props.billData.contractTermsTextOffer || '', {
		includePayment: props.paymentTermsCheckOffer !== false,
		includeDelivery: true,
	}),
)
</script>
