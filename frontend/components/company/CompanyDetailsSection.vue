<script setup lang="ts">
import type { CompanyDataFormState } from '~/types/company'

const props = defineProps<{
  formState: CompanyDataFormState
}>()

const emit = defineEmits(['update:formState'])

const updateField = (field: keyof CompanyDataFormState, value: any) => {
  emit('update:formState', {
    ...props.formState,
    [field]: value
  })
}
</script>

<template>
  <div>
    <h4 class="text-lg font-medium mb-4 text-gray-700 border-b pb-2">Реквизиты компании</h4>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <UFormField label="Полное название организации" required>
        <UInput
            :model-value="formState.companyName"
            class="min-w-4/5"
            @update:model-value="value => updateField('companyName', value)"
        />
      </UFormField>

      <UFormField label="ИНН" required>
        <UInput
            :model-value="formState.inn"
            type="number"
            @update:model-value="value => updateField('inn', value)"
        />
      </UFormField>

      <UFormField label="ОГРН" required>
        <UInput
            :model-value="formState.ogrn"
            type="number"
            @update:model-value="value => updateField('ogrn', value)"
        />
      </UFormField>

      <UFormField label="КПП" required>
        <UInput
            :model-value="formState.kpp"
            type="number"
            @update:model-value="value => updateField('kpp', value)"
        />
      </UFormField>

      <UFormField label="Дата регистрации ОГРН" required>
        <UInput
            :model-value="formState.registrationDate"
            type="date"
            @update:model-value="value => updateField('registrationDate', value)"
        />
      </UFormField>
    </div>
  </div>
</template> 