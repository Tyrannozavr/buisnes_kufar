<template>
	<div>
    <h4 class="text-lg font-medium mb-4 text-gray-700 border-b pb-2">Платежные реквизиты</h4>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
			<!-- left -->
			<UFormField label="Номер расчетного счёта">
				<UInput
            :model-value="currentAccountNumber"
            class="min-w-4/5"
            @update:model-value="value => updateField('currentAccountNumber', value)"
        />
			</UFormField>
			<!-- right -->
			<UFormField label="БИК Банка">
				<UInput
            :model-value="bic"
            class="min-w-4/5"
            @update:model-value="value => updateField('bic', value)"
        />
			</UFormField>
			<!-- left -->
			<UFormField label="Ставка НДС">
				<USelectMunu placeholder="Ставка НДС" :items="vatRateOptions" v-model="vatRate" />
			</UFormField>
			<!-- right -->
			<UFormField label="Корр. счет банка">
				<UInput
            :model-value="correspondentBankAccount"
            class="min-w-4/5"
            @update:model-value="value => updateField('correspondentBankAccount', value)"
        />
			</UFormField>
			<!-- left -->
			<UFormField hide label="">
				
			</UFormField>
			<!-- right -->
			<UFormField label="Наименование банка">
				<UInput
            :model-value="bankName"
            class="min-w-4/5"
            @update:model-value="value => updateField('bankName', value)"
        />
			</UFormField>
		</div>
	</div>
</template>

<script setup lang="ts">
import type { CompanyDataFormState } from '~/types/company'
import type { SelectMenuItem } from '@nuxt/ui';
import { Editor } from '~/constants/keys';

const props = defineProps<{
  formState: CompanyDataFormState
}>()

const emit = defineEmits(['update:formState'])

const updateField = (field: keyof CompanyDataFormState, value: any) => {
  console.log("Typed new value ", value)
  emit('update:formState', {
    ...props.formState,
    [field]: value
  })
}

const vatRateOptions = ref<SelectMenuItem[]>([
	{label: 'Без НДС', id: '0'},
	{label: '5%', id: '5'},
	{label: '7%', id: '7'}, 
	{label: '10%', id: '10'},
	{label: '18%', id: '18'},
	{label: '25%', id: '25'},
])
const vatRate = useState(Editor.VAT_RATE, () => ref())
</script>

<style scoped>

</style>