<script setup lang="ts">
interface CompanyTypeOption {
  label: string
  value: string
  description?: string
}

const props = defineProps<{
  modelValue: string
  required?: boolean
  disabled?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const companyTypeOptions: CompanyTypeOption[] = [
  {
    label: 'ООО',
    value: 'ООО',
    description: 'Общество с ограниченной ответственностью'
  },
  {
    label: 'ОАО',
    value: 'ОАО',
    description: 'Открытое акционерное общество'
  },
  {
    label: 'ПАО',
    value: 'ПАО',
    description: 'Публичное акционерное общество'
  },
  {
    label: 'ЗАО',
    value: 'ЗАО',
    description: 'Закрытое акционерное общество'
  },
  {
    label: 'ИП',
    value: 'ИП',
    description: 'Индивидуальный предприниматель'
  },
  {
    label: 'АО',
    value: 'АО',
    description: 'Акционерное общество'
  },
  {
    label: 'НКО',
    value: 'НКО',
    description: 'Некоммерческая организация'
  },
  {
    label: 'ГУП',
    value: 'ГУП',
    description: 'Государственное унитарное предприятие'
  },
  {
    label: 'МУП',
    value: 'МУП',
    description: 'Муниципальное унитарное предприятие'
  },
  {
    label: 'Производственный кооператив',
    value: 'Производственный кооператив',
    description: 'Производственный кооператив'
  },
  {
    label: 'Потребительский кооператив',
    value: 'Потребительский кооператив',
    description: 'Потребительский кооператив'
  },
  {
    label: 'Товарищество',
    value: 'Товарищество',
    description: 'Товарищество'
  },
  {
    label: 'Фермерское хозяйство',
    value: 'Фермерское хозяйство',
    description: 'Крестьянское (фермерское) хозяйство'
  },
  {
    label: 'Другое',
    value: 'Другое',
    description: 'Другая организационно-правовая форма'
  }
]

const handleChange = (value: string) => {
  emit('update:modelValue', value)
}
</script>

<template>
  <UFormField 
    label="Тип организации" 
    :required="required"
    help="Выберите организационно-правовую форму вашей компании"
  >
    <USelect
      :model-value="modelValue"
      :items="companyTypeOptions"
      :disabled="disabled"
      placeholder="Выберите тип организации"
      class="min-w-1/2"
      @update:model-value="handleChange"
    >
      <template #option="{ item }">
        <div class="flex flex-col">
          <span class="font-medium">{{ item.label }}</span>
          <span v-if="item.description" class="text-sm text-gray-500">{{ item.description }}</span>
        </div>
      </template>
    </USelect>
  </UFormField>
</template> 