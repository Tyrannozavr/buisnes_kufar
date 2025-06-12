<script setup lang="ts">
import type { CompanyOfficial } from '~/types/company'

const props = defineProps<{
  officials: CompanyOfficial[]
}>()

const emit = defineEmits(['update:officials'])

const positions = [
  {label: 'Генеральный директор', value: 'Генеральный директор'},
  {label: 'Финансовый директор', value: 'Финансовый директор'},
  {label: 'Главный бухгалтер', value: 'Главный бухгалтер'},
  {label: 'Коммерческий директор', value: 'Коммерческий директор'},
  {label: 'Технический директор', value: 'Технический директор'},
  {label: 'Руководитель отдела продаж', value: 'Руководитель отдела продаж'},
  {label: 'Руководитель отдела закупок', value: 'Руководитель отдела закупок'},
  {label: 'Руководитель производства', value: 'Руководитель производства'}
]

const positionOptions = positions.map(pos => ({
  label: pos.label,
  value: pos.value
}))

const addOfficial = () => {
  emit('update:officials', [...props.officials, {position: '', fullName: ''} as CompanyOfficial])
}

const removeOfficial = (index: number) => {
  if (props.officials.length > 1) {
    const newOfficials = [...props.officials]
    newOfficials.splice(index, 1)
    emit('update:officials', newOfficials)
  }
}

const updateOfficial = (index: number, field: keyof CompanyOfficial, value: string) => {
  const newOfficials = [...props.officials]
  newOfficials[index] = {
    ...newOfficials[index],
    [field]: value
  }
  emit('update:officials', newOfficials)
}
</script>

<template>
  <div>
    <h4 class="text-lg font-medium mb-4 text-gray-700 border-b pb-2">Должностные лица</h4>
    <div class="space-y-4">
      <div v-for="(official, index) in officials" :key="index" class="flex items-end gap-4">
        <UFormField label="Должность" required class="flex-1">
          <USelect
              :model-value="official.position"
              :items="positionOptions"
              placeholder="Выберите должность"
              @update:model-value="value => updateOfficial(index, 'position', value)"
          />
        </UFormField>
        <UFormField label="ФИО" required class="flex-1">
          <UInput
              :model-value="official.fullName"
              placeholder="Например: Иванова И.И."
              @update:model-value="value => updateOfficial(index, 'fullName', value)"
          />
        </UFormField>
        <UButton
            v-if="officials.length > 1"
            color="error"
            variant="soft"
            icon="i-heroicons-trash"
            class="mb-1"
            @click="removeOfficial(index)"
        />
      </div>
      <UButton
          color="primary"
          variant="soft"
          icon="i-heroicons-plus"
          @click="addOfficial"
      >
        Добавить должностное лицо
      </UButton>
    </div>
  </div>
</template> 