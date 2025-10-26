<script setup lang="ts">
import type { CompanyDataFormState } from '~/types/company'

const props = defineProps<{
  formState: CompanyDataFormState
}>()

const emit = defineEmits(['update:formState'])

const updateField = (field: keyof CompanyDataFormState, value: any) => {
  console.log("Typed neww value ", value)
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
            :model-value="formState.fullName"
            class="min-w-4/5"
            @update:model-value="value => updateField('fullName', value)"
        />
      </UFormField>

      <UFormField label="ИНН" required>
        <UInput
            :model-value="formState.inn"
            type="text"
            placeholder="10 цифр"
            maxlength="10"
            @input="event => event.target.value = event.target.value.slice(0, 10)"
            @update:model-value="value => updateField('inn', value?.toString().slice(0, 10))"
        />
      </UFormField>

      <UFormField label="ОГРН" required>
        <UInput
            :model-value="formState.ogrn"
            type="text"
            placeholder="13 цифр"
            @update:model-value="value => updateField('ogrn', value)"
        />
      </UFormField>
      <UFormField label="КПП" required>
        <UInput
            :model-value="formState.kpp"
            type="text"
            placeholder="9 цифр"
            @input="event => event.target.value = event.target.value.slice(0, 9)"
            @update:model-value="value => updateField('kpp', value?.toString().slice(0,9))"
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