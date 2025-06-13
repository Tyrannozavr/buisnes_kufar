<script setup lang="ts">
import {onMounted, ref, watch} from 'vue'
import type {
  BusinessType,
  CompanyDataFormProps,
  CompanyDataFormState,
  CompanyOfficial,
  CompanyResponse,
  CompanyUpdate,
  TradeActivity
} from '~/types/company'
import type {LocationItem} from '~/types/location'
import {useLocationsApi} from '~/api/locations'
import {useUserStore} from '~/stores/user'
import {uploadCompanyLogo} from '~/api/companyOwner'

const props = defineProps<CompanyDataFormProps>()

const emit = defineEmits<{
  (e: 'save', data: CompanyUpdate): void
  (e: 'logo-upload', file: File): void
  (e: 'logo-updated', data: CompanyResponse): void
}>()

const userStore = useUserStore()
const fileInputRef = ref<HTMLInputElement | null>(null)

const officials = ref<CompanyOfficial[]>(props.company?.officials || [])

const { 
  countryOptions,
  federalDistrictOptions,
  regionOptions,
  cityOptions,
  loadCountries,
  loadFederalDistricts,
  loadRegions,
  loadCities,
  searchCities
} = useLocationsApi()

// Загружаем списки локаций
const countries = ref<LocationItem[]>([])
const federalDistricts = ref<LocationItem[]>([])
const regions = ref<LocationItem[]>([])
const cities = ref<LocationItem[]>([])

// Добавляем состояние для поискового запроса города
const citySearchQuery = ref('')
const citySearchTimeout = ref<NodeJS.Timeout | null>(null)

// Добавляем состояние для отслеживания, был ли город выбран пользователем
const isCityManuallyChanged = ref(false)

// Функция для поиска городов с задержкой
const handleCitySearch = async (query: string) => {
  citySearchQuery.value = query // Обновляем значение поискового запроса
  isCityManuallyChanged.value = true // Отмечаем, что пользователь начал изменять город

  // Очищаем предыдущий таймаут
  if (citySearchTimeout.value) {
    clearTimeout(citySearchTimeout.value)
  }

  // Если запрос короче 2 символов, очищаем список городов
  if (query.length < 2) {
    cities.value = []
    return
  }

  // Устанавливаем новый таймаут для поиска
  citySearchTimeout.value = setTimeout(async () => {
    try {
      // Если есть выбранный регион, используем его для поиска
      if (formState.value.region?.value) {
        await loadCities(formState.value.country?.value || '', formState.value.region.value)
      } else {
        // Иначе используем поиск по имени
        await searchCities(query)
      }
      cities.value = cityOptions.value
    } catch (error) {
      console.error('Error searching cities:', error)
      cities.value = []
    }
  }, 300) // Задержка 300мс
}

// Загружаем страны при монтировании компонента
onMounted(async () => {
  await loadCountries()
  countries.value = countryOptions.value
  
  // Если есть данные о стране, загружаем федеральные округа
  if (props.company?.country) {
    await loadFederalDistricts()
    federalDistricts.value = federalDistrictOptions.value
  }
  
  // Если есть данные о регионе, загружаем регионы
  if (props.company?.region) {
    await loadRegions(props.company.country, props.company.federal_district)
    regions.value = regionOptions.value
  }
  
  // Если есть данные о городе, устанавливаем его без дополнительных запросов
  if (props.company?.city && props.company) {
    citySearchQuery.value = props.company.city
    // Создаем объект LocationItem для города
    formState.value.city = {
      label: props.company.city,
      value: props.company.city
    }
  }
})

// Функция для преобразования строки в LocationItem
const findLocationItem = (items: LocationItem[], value: string): LocationItem | undefined => {
  return items.find(item => item.value === value)
}

// Transform company data from snake_case to camelCase
const transformCompanyData = (companyData: CompanyResponse | undefined): CompanyDataFormState => {
  if (!companyData) {
    return {
      name: '',
      fullName: '',
      inn: '',
      kpp: '',
      ogrn: '',
      registrationDate: '',
      type: 'company',
      tradeActivity: 'Покупатель' as TradeActivity,
      businessType: 'Производство товаров' as BusinessType,
      activityType: null,
      description: null,
      website: null,
      legalAddress: null,
      phone: null,
      email: null,
      productionAddress: null,
      country: undefined,
      federalDistrict: undefined,
      region: undefined,
      city: undefined,
      officials: [],
      logo: null,
      logo_url: null
    }
  }

  const { 
    country: countryValue, 
    federal_district: federalDistrictValue, 
    region: regionValue, 
    city: cityValue,
    trade_activity: tradeActivityValue,
    business_type: businessTypeValue,
    activity_type: activityTypeValue,
    description: descriptionValue,
    website: websiteValue,
    legal_address: legalAddressValue,
    phone: phoneValue,
    email: emailValue,
    production_address: productionAddressValue,
    officials: officialsValue,
    logo: logoValue,
    logo_url: logoUrlValue,
    full_name: fullNameValue,
    inn: innValue,
    kpp: kppValue,
    ogrn: ogrnValue,
    registration_date: registrationDateValue,
    type: typeValue
  } = companyData

  const country = countryValue ? { label: countryValue, value: countryValue } : undefined
  const federalDistrict = federalDistrictValue ? { label: federalDistrictValue, value: federalDistrictValue } : undefined
  const region = regionValue ? { label: regionValue, value: regionValue } : undefined
  const city = cityValue ? { label: cityValue, value: cityValue } : undefined

  return {
    name: companyData.name,
    fullName: fullNameValue,
    inn: innValue,
    kpp: kppValue,
    ogrn: ogrnValue,
    registrationDate: registrationDateValue,
    type: typeValue,
    tradeActivity: tradeActivityValue,
    businessType: businessTypeValue,
    activityType: activityTypeValue,
    description: descriptionValue,
    website: websiteValue,
    legalAddress: legalAddressValue,
    phone: phoneValue,
    email: emailValue,
    productionAddress: productionAddressValue,
    country,
    federalDistrict,
    region,
    city,
    officials: officialsValue,
    logo: logoValue,
    logo_url: logoUrlValue
  }
}

// Transform form data back to snake_case for API
const transformFormData = (formData: CompanyDataFormState): CompanyUpdate => {
  const { 
    country: countryItem, 
    federalDistrict: federalDistrictItem, 
    region: regionItem, 
    city: cityItem,
    name: nameValue,
    fullName: fullNameValue,
    inn: innValue,
    kpp: kppValue,
    ogrn: ogrnValue,
    registrationDate: registrationDateValue,
    type: typeValue,
    tradeActivity: tradeActivityValue,
    businessType: businessTypeValue,
    activityType: activityTypeValue,
    description: descriptionValue,
    website: websiteValue,
    legalAddress: legalAddressValue,
    phone: phoneValue,
    email: emailValue,
    productionAddress: productionAddressValue,
    officials: officialsValue
  } = formData

  return {
    name: nameValue,
    full_name: fullNameValue,
    inn: innValue,
    kpp: kppValue,
    ogrn: ogrnValue,
    registration_date: registrationDateValue,
    type: typeValue,
    trade_activity: tradeActivityValue,
    business_type: businessTypeValue,
    activity_type: activityTypeValue,
    description: descriptionValue,
    website: websiteValue,
    legal_address: legalAddressValue,
    phone: phoneValue,
    email: emailValue,
    production_address: productionAddressValue,
    country: (countryItem as LocationItem)?.value,
    federal_district: (federalDistrictItem as LocationItem)?.value,
    region: (regionItem as LocationItem)?.value,
    city: (cityItem as LocationItem)?.value,
    officials: officialsValue
  }
}

// Инициализация состояния формы
const formState = ref<CompanyDataFormState>(transformCompanyData(props.company))

// Обновление формы при изменении props.company
watch(() => props.company, (newCompany) => {
  formState.value = transformCompanyData(newCompany)
}, { immediate: true })

// Следим за изменениями списков локаций и устанавливаем значения
watch(countryOptions, (newCountries) => {
  if (props.company?.country) {
    formState.value.country = findLocationItem(newCountries, props.company.country)
  }
})

watch(federalDistrictOptions, (newDistricts) => {
  if (props.company?.federal_district) {
    formState.value.federalDistrict = findLocationItem(newDistricts, props.company.federal_district)
  }
})

watch(regionOptions, (newRegions) => {
  if (props.company?.region) {
    formState.value.region = findLocationItem(newRegions, props.company.region)
  }
})

watch(cityOptions, (newCities) => {
  if (props.company?.city) {
    formState.value.city = findLocationItem(newCities, props.company.city)
  }
})

// Обработчик изменения страны
const handleCountryChange = async (country: LocationItem | undefined) => {
  formState.value.country = country
  formState.value.federalDistrict = undefined
  formState.value.region = undefined
  formState.value.city = undefined
  citySearchQuery.value = ''
  cities.value = []
  isCityManuallyChanged.value = false // Сбрасываем флаг изменения города
  
  if (country?.value === 'Россия') {
    await loadFederalDistricts()
    federalDistricts.value = federalDistrictOptions.value
  } else {
    federalDistricts.value = []
  }
  
  if (country?.value) {
    await loadRegions(country.value)
    regions.value = regionOptions.value
  } else {
    regions.value = []
  }
}

// Обработчик изменения федерального округа
const handleFederalDistrictChange = async (district: LocationItem | undefined) => {
  formState.value.federalDistrict = district
  formState.value.region = undefined
  formState.value.city = undefined
  citySearchQuery.value = ''
  cities.value = []
  isCityManuallyChanged.value = false // Сбрасываем флаг изменения города
  
  if (formState.value.country?.value && district?.value) {
    await loadRegions(formState.value.country.value, district.value)
    regions.value = regionOptions.value
  } else {
    regions.value = []
  }
}

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

const handleLogoUpload = async (event: Event) => {
  const input = event.target as HTMLInputElement
  if (!input.files?.length) return
  
  const file = input.files[0]
  if (file) {
    try {
      const response = await uploadCompanyLogo(file)
      if (response) {
        formState.value.logo = response.logo_url
        // Emit event with updated company data
        emit('logo-updated', response)
        useToast().add({
          title: 'Успешно',
          description: 'Логотип компании обновлен',
          color: 'success'
        })
      }
    } catch (error) {
      useToast().add({
        title: 'Ошибка',
        description: 'Не удалось загрузить логотип',
        color: 'error'
      })
    }
  }
}

const handleSubmit = async () => {

  const data: CompanyUpdate = transformFormData(formState.value)

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
  if (!formState.value.legalAddress) {
    errors.push('Введите юридический адрес')
  }
  if (!formState.value.productionAddress) {
    errors.push('Введите адрес производства')
  }
  if (!formState.value.phone) {
    errors.push('Введите телефон')
  }
  if (!formState.value.email) {
    errors.push('Введите email')
  }
  
  return errors
}

// Обновляем обработчик изменения города
const handleCityChange = (city: LocationItem | undefined) => {
  formState.value.city = city
  if (city) {
    citySearchQuery.value = city.label
    isCityManuallyChanged.value = true // Отмечаем, что пользователь выбрал город
  }
}

// Обновляем обработчик изменения региона
const handleRegionChange = async (region: LocationItem | undefined) => {
  formState.value.region = region
  formState.value.city = undefined
  citySearchQuery.value = ''
  cities.value = [] // Очищаем список городов при смене региона
  isCityManuallyChanged.value = false // Сбрасываем флаг изменения города
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
                :src="formState.logo_url || undefined"
                size="xl"
                :alt="formState.name"
            />
            <input
                ref="fileInputRef"
                type="file"
                accept="image/*"
                class="hidden"
                @change="handleLogoUpload"
            />
            <UButton
                color="secondary"
                variant="soft"
                icon="i-heroicons-photo"
                @click="fileInputRef?.click()"
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

        <!-- 6. Местоположение -->
        <div>
          <h4 class="text-lg font-medium mb-4 text-gray-700 border-b pb-2">Местоположение</h4>
          <div class="flex items-center gap-4">
            <UCombobox
                v-model="formState.country"
                :items="countries"
                label="Страна"
                placeholder="Выберите страну"
                @update:model-value="handleCountryChange"
            />
            <UCombobox
                v-if="formState.country?.value === 'Россия'"
                v-model="formState.federalDistrict"
                :items="federalDistricts"
                label="Федеральный округ"
                placeholder="Выберите федеральный округ"
                @update:model-value="handleFederalDistrictChange"
            />
            <UCombobox
                v-model="formState.region"
                :items="regions"
                label="Регион"
                placeholder="Выберите регион"
                @update:model-value="handleRegionChange"
            />
            <UCombobox
                v-model="formState.city"
                :items="cities"
                label="Город"
                :placeholder="isCityManuallyChanged ? 'Введите название города' : 'Город'"
                :search-input="{
                  modelValue: citySearchQuery,
                  'onUpdate:modelValue': handleCitySearch,
                  placeholder: 'Поиск города...',
                  icon: 'i-lucide-search'
                }"
                @update:model-value="handleCityChange"
            />
          </div>
        </div>
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