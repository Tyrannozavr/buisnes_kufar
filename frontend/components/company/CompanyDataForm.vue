<script setup lang="ts">
import type {Company} from '~/types/company'

const props = defineProps<{
  company: Company
  loading: boolean
}>()

const emit = defineEmits<{
  (e: 'save', data: Partial<Company>): void
}>()

const formState = ref<Company>({...props.company})

const tradeActivityOptions = [
  {label: 'Покупатель', value: 'Покупатель'},
  {label: 'Продавец', value: 'Продавец'},
  {label: 'Покупатель и продавец', value: 'Покупатель и продавец'}
]

const businessTypeOptions = [
  {label: 'Производство товаров', value: 'Производство товаров'},
  {label: 'Оказание услуг', value: 'Оказание услуг'},
  {label: 'Производство товаров и оказание услуг', value: 'Производство товаров и оказание услуг'}
]

const countryOptions = [
  'Азербайджан',
  'Армения',
  'Беларусь',
  'Казахстан',
  'Кыргызстан',
  'Молдова',
  'Россия',
  'Таджикистан',
  'Узбекистан'
].map(country => ({label: country, value: country}))

const federalDistrictOptions = [
  'Центральный',
  'Северо-Западный',
  'Южный',
  'Северо-Кавказский',
  'Приволжский',
  'Уральский',
  'Сибирский',
  'Дальневосточный'
].map(district => ({label: district, value: district}))

const regionOptions = [
  // TODO: Add actual regions based on selected federal district
].map(region => ({label: region, value: region}))

const handleSave = () => {
  emit('save', formState.value)
}

const handleLogoUpload = () => {
  // TODO: Implement logo upload
}
</script>

<template>
  <UCard>
    <template #header>
      <div class="flex items-center justify-between">
        <h3 class="text-xl font-semibold">Данные компании</h3>
        <UButton
            color="primary"
            :loading="loading"
            @click="handleSave"
        >
          Сохранить
        </UButton>
      </div>
    </template>

    <UForm
        :state="formState"
        @submit="handleSave"
    >
      <div class="space-y-6">
        <!-- Logo Upload -->
        <div class="flex items-center gap-4">
          <UAvatar
              :src="formState.logo"
              size="xl"
              :alt="formState.name"
          />
          <UButton
              color="secondary"
              variant="soft"
              icon="i-heroicons-photo"
              @click="handleLogoUpload"
          >
            Загрузить логотип
          </UButton>
          <UTooltip
              text="Выберите изображение для Вашей компании. Логотип компании будет отображаться на основных страницах сайта, улучшать наглядность и повышать узнаваемость компании">
            <UIcon name="i-heroicons-question-mark-circle" class="text-gray-400"/>
          </UTooltip>
        </div>

        <!-- Company Information -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <UFormGroup label="Торговая деятельность" required>
            <USelect
                v-model="formState.tradeActivity"
                :options="tradeActivityOptions"
            />
          </UFormGroup>

          <UFormGroup label="Род деятельности" required>
            <USelect
                v-model="formState.businessType"
                :options="businessTypeOptions"
            />
          </UFormGroup>

          <UFormGroup label="Название организации" required>
            <UInput
                v-model="formState.name"
                placeholder="Краткое название организации"
            />
          </UFormGroup>

          <UFormGroup label="Вид деятельности" required>
            <UInput
                v-model="formState.activityType"
                placeholder="Например: Производство обуви"
            />
          </UFormGroup>

          <UFormGroup label="Описание организации" required>
            <UTextarea
                v-model="formState.description"
                placeholder="Опишите деятельность компании и ее основные достоинства"
            />
          </UFormGroup>
        </div>

        <!-- Location -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <UFormGroup label="Страна" required>
            <USelect
                v-model="formState.country"
                :options="countryOptions"
            />
          </UFormGroup>

          <UFormGroup label="Федеральный округ" required>
            <USelect
                v-model="formState.federalDistrict"
                :options="federalDistrictOptions"
                :disabled="formState.country !== 'Россия'"
            />
          </UFormGroup>

          <UFormGroup label="Регион" required>
            <USelect
                v-model="formState.region"
                :options="regionOptions"
            />
          </UFormGroup>

          <UFormGroup label="Город" required>
            <UInput
                v-model="formState.city"
            />
          </UFormGroup>
        </div>

        <!-- Company Details -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <UFormGroup label="Полное название организации" required>
            <UInput
                v-model="formState.fullName"
            />
          </UFormGroup>

          <UFormGroup label="ИНН" required>
            <UInput
                v-model="formState.inn"
                type="number"
            />
          </UFormGroup>

          <UFormGroup label="ОГРН" required>
            <UInput
                v-model="formState.ogrn"
                type="number"
            />
          </UFormGroup>

          <UFormGroup label="КПП" required>
            <UInput
                v-model="formState.kpp"
                type="number"
            />
          </UFormGroup>

          <UFormGroup label="Дата регистрации ОГРН" required>
            <UInput
                v-model="formState.registrationDate"
                type="date"
            />
          </UFormGroup>
        </div>

        <!-- Contact Information -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <UFormGroup label="Юридический адрес" required>
            <UInput
                v-model="formState.legalAddress"
            />
          </UFormGroup>

          <UFormGroup label="Адрес производства" required>
            <UInput
                v-model="formState.productionAddress"
            />
          </UFormGroup>

          <UFormGroup label="Телефон" required>
            <UInput
                v-model="formState.phone"
                type="tel"
            />
          </UFormGroup>

          <UFormGroup label="Электронная почта" required>
            <UInput
                v-model="formState.email"
                type="email"
            />
          </UFormGroup>

          <UFormGroup label="Официальный сайт компании">
            <UInput
                v-model="formState.website"
                type="url"
            />
          </UFormGroup>
        </div>
      </div>
    </UForm>
  </UCard>
</template>
