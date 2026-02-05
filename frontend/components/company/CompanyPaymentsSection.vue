<template>
	<div>
    <h4 class="text-lg font-medium mb-4 text-gray-700 border-b pb-2">Платежные реквизиты</h4>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
			<!-- left -->
			<UFormField label="Номер расчетного счёта">
				<UInput
            :model-value="formState.currentAccountNumber"
            class="min-w-4/5"
            @update:model-value="value => updateField('currentAccountNumber', value)"
        />
			</UFormField>
			<!-- right -->
			<UFormField label="БИК Банка">
				<UInput
            :model-value="formState.bic"
            class="min-w-4/5"
            @update:model-value="value => updateField('bic', value)"
        />
			</UFormField>
			<!-- left -->
			<UFormField label="Ставка НДС">
				<USelectMenu
					placeholder="Ставка НДС"
					:items="vatRateOptions"
					:model-value="formState.vatRate"
					class="min-w-4/5"
					@update:model-value="value => updateField('vatRate', normalizeVatRate(value))"
				/>
			</UFormField>
			<!-- right -->
			<UFormField label="Корр. счет банка">
				<UInput
            :model-value="formState.correspondentBankAccount"
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
            :model-value="formState.bankName"
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

const props = defineProps<{
  formState: CompanyDataFormState
}>()

const emit = defineEmits(['update:formState'])

const normalizeVatRate = (rawValue: unknown): number | undefined => {
  if (rawValue === null || rawValue === undefined) return undefined

  // Nuxt UI can emit either primitive value or the whole item object (often as a Proxy)
  if (typeof rawValue === 'number') return rawValue

  if (typeof rawValue === 'string') {
    const parsed = Number(rawValue)
    return Number.isFinite(parsed) ? parsed : undefined
  }

  if (typeof rawValue === 'object' && 'value' in (rawValue as Record<string, unknown>)) {
    const value = (rawValue as { value?: unknown }).value
    if (typeof value === 'number') return value
    const parsed = typeof value === 'string' ? Number(value) : Number(value)
    return Number.isFinite(parsed) ? parsed : undefined
  }

  return undefined
}

const updateField = (field: keyof CompanyDataFormState, value: any) => {
  console.log("Typed new value ", value)
  emit('update:formState', {
    ...props.formState,
    [field]: value
  })
}

const vatRateOptions = ref<SelectMenuItem[]>([
	{label: 'Без НДС', value: 0},
	{label: '5%', value: 5},
	{label: '7%', value: 7}, 
	{label: '10%', value: 10},
	{label: '18%', value: 18},
	{label: '25%', value: 25},
])
</script>

<style scoped>

</style>