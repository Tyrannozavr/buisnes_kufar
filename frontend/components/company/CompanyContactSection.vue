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
    <h4 class="text-lg font-medium mb-4 text-gray-700 border-b pb-2">Контактные данные</h4>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <UFormField label="Юридический адрес" required>
        <UInput
            :model-value="formState.companyAddress"
            class="min-w-full"
            @update:model-value="value => updateField('companyAddress', value)"
        />
      </UFormField>

      <UFormField label="Адрес производства" required>
        <UInput
            :model-value="formState.productionAddress"
            class="min-w-full"
            @update:model-value="value => updateField('productionAddress', value)"
        />
      </UFormField>

      <UFormField label="Телефон" required>
        <UInput
            :model-value="formState.companyPhone"
            type="tel"
            @update:model-value="value => updateField('companyPhone', value)"
        />
      </UFormField>

      <UFormField label="Электронная почта" required>
        <UInput
            :model-value="formState.companyEmail"
            type="email"
            @update:model-value="value => updateField('companyEmail', value)"
        />
      </UFormField>

      <UFormField label="Официальный сайт компании">
        <UInput
            :model-value="formState.companyWebsite"
            type="url"
            placeholder="https://example.com"
            @update:model-value="value => updateField('companyWebsite', value)"
        />
      </UFormField>
    </div>
  </div>
</template> 