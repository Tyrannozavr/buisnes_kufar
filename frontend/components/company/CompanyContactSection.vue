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
            :model-value="formState.legalAddress"
            class="min-w-full"
            @update:model-value="value => updateField('legalAddress', value)"
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
            :model-value="formState.phone"
            type="tel"
            @update:model-value="value => updateField('phone', value)"
        />
      </UFormField>

      <UFormField label="Электронная почта" required>
        <UInput
            :model-value="formState.email"
            type="email"
            @update:model-value="value => updateField('email', value)"
        />
      </UFormField>

      <UFormField label="Официальный сайт компании">
        <UInput
            :model-value="formState.website"
            type="url"
            placeholder="https://example.com"
            @update:model-value="value => updateField('website', value)"
        />
      </UFormField>
    </div>
  </div>
</template> 