<script setup lang="ts">
import type {CompanyDataFormProps, CompanyDataFormState, CompanyOfficial} from '~/types/company'
import {useLocationsApi} from '~/api/locations'

const props = defineProps<CompanyDataFormProps>()

const emits = defineEmits(['save'])

// Определяем тип для значений формы
interface Official {
  position: string
  fullName: string
}

const formState = ref<CompanyDataFormState>({
  inn: '',
  kpp: '',
  ogrn: '',
  registrationDate: '',
  country: undefined,
  federalDistrict: undefined,
  region: undefined,
  city: undefined,
  productionAddress: '',
  officials: [],
  tradeActivity: '',
  businessType: '',
  activityType: '',
  position: '',
  companyName: '',
  companyDescription: '',
  companyWebsite: '',
  companyLogo: '',
  companyAddress: '',
  companyPhone: '',
  companyEmail: ''
})

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

const {
  countryOptions,
  federalDistrictOptions,
  regionOptions,
  cityOptions,
  countriesLoading,
  federalDistrictsLoading,
  regionsLoading,
  citiesLoading,
  countriesError,
  federalDistrictsError,
  regionsError,
  citiesError,
  loadFederalDistricts,
  loadRegions,
  loadCities
} = useLocationsApi()

// Watch для страны
watch(() => formState.value.country, async (newCountry) => {
  // Сбрасываем все зависимые поля
  formState.value.federalDistrict = undefined
  formState.value.region = undefined
  formState.value.city = undefined

  if (!newCountry) {
    return
  }

  try {
    // Загружаем федеральные округи только для России
    if (newCountry.value === 'Россия') {
      await loadFederalDistricts()
    } else {
      // Для других стран сразу загружаем регионы
      await loadRegions(newCountry.value)
    }
  } catch (error) {
    console.error('Error handling country change:', error)
  }
})

// Watch для федерального округа
watch(() => formState.value.federalDistrict, async (newFederalDistrict) => {
  // Сбрасываем зависимые поля
  formState.value.region = undefined
  formState.value.city = undefined

  if (!newFederalDistrict || !formState.value.country || formState.value.country.value !== 'Россия') {
    return
  }

  try {
    // Загружаем регионы только после выбора федерального округа для России
    await loadRegions(formState.value.country.value, newFederalDistrict.value)
  } catch (error) {
    console.error('Error handling federal district change:', error)
  }
})

// Watch для региона
watch(() => formState.value.region, async (newRegion) => {
  if (!newRegion || !formState.value.country) {
    formState.value.city = undefined
    return
  }
  try {
    await loadCities(formState.value.country.value, newRegion.value, 1) // Pass region value as string and specify level 1 for major cities
  } catch (error) {
    console.error('Error handling region change:', error)
  }
})

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

const officials = ref<CompanyOfficial[]>(props.company.officials || [{position: '', fullName: ''} as CompanyOfficial])

const addOfficial = () => {
  officials.value.push({position: '', fullName: ''})
}

const removeOfficial = (index: number) => {
  if (officials.value.length > 1) {
    officials.value.splice(index, 1)
  }
}

const handleSave = () => {
  formState.value.officials = officials.value
  emits('save', formState.value)
}

const handleLogoUpload = () => {
  // TODO: Implement logo upload
}

// Добавляем определение positionOptions
const positionOptions = positions.map(pos => ({
  label: pos.label,
  value: pos.value
}))
</script>

<template>
  <UCard>
    <template #header>
      <div class="flex items-center justify-between">
        <h3 class="text-xl font-semibold">Данные компании</h3>
        <UButton
            color="primary"
            :loading="loading"
            class="cursor-pointer"
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
      <div class="space-y-8">
        <!-- 1. Логотип компании -->
        <div>
          <h4 class="text-lg font-medium mb-4 text-gray-700 border-b pb-2">Логотип компании</h4>
          <div class="flex items-center gap-4">
            <UAvatar
                :src="formState.companyLogo || undefined"
                size="xl"
                :alt="formState.companyName"
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
        </div>

        <!-- 2. Информация о компании -->
        <CompanyInfoSection
            v-model:formState="formState"
        />

        <!-- 3. Реквизиты компании -->
        <CompanyDetailsSection
            v-model:formState="formState"
        />

        <!-- 4. Должностные лица -->
        <CompanyOfficialsSection
            v-model:officials="officials"
        />

        <!-- 5. Контактные данные -->
        <CompanyContactSection
            v-model:formState="formState"
        />
      </div>
      <div class="flex">
        <UButton
            color="primary"
            :loading="loading"
            class="w-full mt-3 cursor-pointer"
            @click="handleSave"
        >
          <span class="mx-auto">Сохранить</span>
        </UButton>
      </div>
    </UForm>
  </UCard>
</template>