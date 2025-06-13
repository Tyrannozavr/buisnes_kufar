<script setup lang="ts">
import type {Company, CompanyUpdate, CompanyDataFormProps, CompanyDataFormState, CompanyOfficial} from '~/types/company'
import type {LocationItem} from '~/types/location'
import {useLocationsApi} from '~/api/locations'

const props = defineProps<{
  company?: Company
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'save', data: CompanyUpdate): void
  (e: 'logo-upload', file: File): void
}>()

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
  name: '',
  fullName: '',
  companyDescription: '',
  companyWebsite: '',
  companyLogo: '',
  companyAddress: '',
  companyPhone: '',
  companyEmail: ''
})

// Initialize form state with company data if available
watch(() => props.company, (newCompany) => {
  if (newCompany) {
    formState.value = {
      inn: newCompany.inn ?? '',
      kpp: newCompany.kpp ?? '',
      ogrn: newCompany.ogrn ?? '',
      registrationDate: newCompany.registrationDate ?? '',
      country: undefined,
      federalDistrict: undefined,
      region: undefined,
      city: undefined,
      productionAddress: newCompany.productionAddress ?? '',
      officials: newCompany.officials ?? [],
      tradeActivity: newCompany.tradeActivity ?? '',
      businessType: newCompany.businessType ?? '',
      activityType: newCompany.activityType ?? '',
      position: '',
      name: newCompany.name ?? '',
      fullName: newCompany.fullName ?? '',
      companyDescription: newCompany.description ?? '',
      companyWebsite: newCompany.website ?? '',
      companyLogo: newCompany.logo ?? '',
      companyAddress: newCompany.legalAddress ?? '',
      companyPhone: newCompany.phone ?? '',
      companyEmail: newCompany.email ?? ''
    }
  }
}, { immediate: true })

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
  emit('save', formState.value)
}

const handleLogoUpload = (event: Event) => {
  const input = event.target as HTMLInputElement
  if (!input.files?.length) return
  
  const file = input.files[0]
  if (file) {
    emit('logo-upload', file)
  }
}

const handleSubmit = () => {
  const data: CompanyUpdate = {
    name: formState.value.name,
    fullName: formState.value.fullName,
    inn: formState.value.inn,
    kpp: formState.value.kpp,
    ogrn: formState.value.ogrn,
    registrationDate: formState.value.registrationDate,
    country: (formState.value.country as LocationItem)?.value,
    federalDistrict: (formState.value.federalDistrict as LocationItem)?.value,
    region: (formState.value.region as LocationItem)?.value,
    city: (formState.value.city as LocationItem)?.value,
    productionAddress: formState.value.productionAddress,
    officials: formState.value.officials,
    tradeActivity: formState.value.tradeActivity as CompanyUpdate['tradeActivity'],
    businessType: formState.value.businessType as CompanyUpdate['businessType'],
    activityType: formState.value.activityType,
    description: formState.value.companyDescription,
    website: formState.value.companyWebsite || undefined,
    legalAddress: formState.value.companyAddress,
    phone: formState.value.companyPhone,
    email: formState.value.companyEmail
  }

  const errors = validateForm()
  if (errors.length > 0) {
    useToast().add({
      title: 'Ошибка валидации',
      description: errors.join('\n'),
      color: 'error'
    })
    return
  }

  emit('save', data)
}

// Добавляем определение positionOptions
const positionOptions = positions.map(pos => ({
  label: pos.label,
  value: pos.value
}))

const validateForm = () => {
  const errors: string[] = []
  
  if (!formState.value.name) {
    errors.push('Введите название организации')
  }
  if (!formState.value.fullName) {
    errors.push('Введите полное юридическое название организации')
  }
  if (!formState.value.inn) {
    errors.push('Введите ИНН')
  }
  if (!formState.value.ogrn) {
    errors.push('Введите ОГРН')
  }
  if (!formState.value.kpp) {
    errors.push('Введите КПП')
  }
  if (!formState.value.registrationDate) {
    errors.push('Введите дату регистрации')
  }
  if (!formState.value.tradeActivity) {
    errors.push('Выберите тип торговой деятельности')
  }
  if (!formState.value.businessType) {
    errors.push('Выберите род деятельности')
  }
  if (!formState.value.activityType) {
    errors.push('Введите вид деятельности')
  }
  if (!formState.value.companyAddress) {
    errors.push('Введите юридический адрес')
  }
  if (!formState.value.productionAddress) {
    errors.push('Введите адрес производства')
  }
  if (!formState.value.companyPhone) {
    errors.push('Введите телефон')
  }
  if (!formState.value.companyEmail) {
    errors.push('Введите email')
  }
  
  return errors
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
            class="cursor-pointer"
            @click="handleSubmit"
        >
          Сохранить
        </UButton>
      </div>
    </template>

    <UForm
        :state="formState"
        @submit="handleSubmit"
    >
      <div class="space-y-8">
        <!-- 1. Логотип компании -->
        <div>
          <h4 class="text-lg font-medium mb-4 text-gray-700 border-b pb-2">Логотип компании</h4>
          <div class="flex items-center gap-4">
            <UAvatar
                :src="formState.companyLogo || undefined"
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
            @click="handleSubmit"
        >
          <span class="mx-auto">Сохранить</span>
        </UButton>
      </div>
    </UForm>
  </UCard>
</template>