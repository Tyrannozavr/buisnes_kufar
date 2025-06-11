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
  if (!newCountry || newCountry.value !== 'Россия') {
    formState.value.federalDistrict = undefined
    formState.value.region = undefined
    formState.value.city = undefined
    return
  }
  try {
    await loadRegions(newCountry.value)
    await loadFederalDistricts()
  } catch (error) {
    console.error('Error handling country change:', error)
  }
})

// Watch для региона
watch(() => formState.value.region, async (newRegion) => {
  if (!newRegion || !formState.value.country) {
    formState.value.city = undefined
    return
  }
  try {
    await loadCities(newRegion.value, 1) // Pass region value as string and specify level 1 for major cities
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

const officials = ref<CompanyOfficial[]>(props.company.officials || [{position: '', fullName: ''}])

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
        <div>
          <h4 class="text-lg font-medium mb-4 text-gray-700 border-b pb-2">Информация о компании</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <UFormField label="Торговая деятельность" required help="Выберите тип торговой деятельности вашей компании">
              <USelect
                  v-model="formState.tradeActivity"
                  :items="tradeActivityOptions"
                  class="min-w-1/2"
              />
            </UFormField>

            <UFormField label="Род деятельности" required
                        help="Определяет в каком разделе будет отображаться ваша компания">
              <USelect
                  v-model="formState.businessType"
                  :items="businessTypeOptions"
                  class="min-w-1/2"

              />
            </UFormField>

            <UFormField label="Название организации" required help="Краткое название организации для визитной карточки">
              <UInput
                  v-model="formState.companyName"
                  placeholder="Краткое название организации"
                  class="min-w-1/2"
              />
            </UFormField>

            <UFormField label="Вид деятельности" required
                        help="Основное направление деятельности компании. Например: «Производство обуви», «Строительство каркасных домов»">
              <UInput
                  v-model="formState.activityType"
                  placeholder="Например: Производство обуви"
                  class="min-w-full"
              />
            </UFormField>

            <UFormField label="Описание организации" required
                        help="Опишите деятельность компании и ее основные достоинства" class="md:col-span-2">
              <UTextarea
                  v-model="formState.companyDescription"
                  placeholder="Опишите деятельность компании и ее основные достоинства"
                  :rows="4"
                  class="min-w-2/5"
              />
            </UFormField>
            <UFormField label="Страна" required>
              <USelectMenu
                  v-model="formState.country"
                  :items="countryOptions || []"
                  :loading="countriesLoading"
                  :disabled="countriesLoading || !!countriesError"
                  placeholder="Выберите страну"
                  :search-input="{
                      placeholder: 'Поиск...',
                      icon: 'i-lucide-search'
                    }"
                  searchable
              />
              <p v-if="countriesError" class="text-red-500 text-sm mt-1">
                Не удалось загрузить список стран. Пожалуйста, попробуйте позже.
              </p>
            </UFormField>

            <UFormField label="Федеральный округ" required>
              <USelectMenu
                  v-model="formState.federalDistrict"
                  :items="federalDistrictOptions || []"
                  :loading="federalDistrictsLoading"
                  :disabled="formState.country?.value !== 'Россия' || federalDistrictsLoading || !!federalDistrictsError"
                  placeholder="Выберите федеральный округ"
                  :search-input="{
                      placeholder: 'Поиск...',
                      icon: 'i-lucide-search'
                    }"
                  searchable
              />
              <p v-if="federalDistrictsError" class="text-red-500 text-sm mt-1">
                Не удалось загрузить список федеральных округов. Пожалуйста, попробуйте позже.
              </p>
              <p v-if="formState.country && formState.country.value !== 'Россия'" class="text-gray-500 text-sm mt-1">
                Федеральный округ доступен только для России
              </p>
            </UFormField>

            <UFormField label="Регион" required>
              <USelectMenu
                  v-model="formState.region"
                  :items="regionOptions || []"
                  :loading="regionsLoading"
                  :disabled="!formState.country || regionsLoading"
                  placeholder="Выберите регион"
                  :search-input="{
                      placeholder: 'Поиск...',
                      icon: 'i-lucide-search'
                    }"
                  searchable
              />
              <p v-if="regionsError" class="text-red-500 text-sm mt-1">
                Не удалось загрузить список регионов: {{ regionsError?.message || 'Неизвестная ошибка' }}
              </p>
              <p v-if="formState.country && !regionsLoading && !regionOptions?.length" class="text-gray-500 text-sm mt-1">
                {{ formState.country.value === 'Россия' 
                  ? 'Выберите федеральный округ для загрузки списка регионов' 
                  : 'Для выбранной страны регионы не требуются' }}
              </p>
            </UFormField>
            <UFormField label="Город" required>
              <USelectMenu
                  v-model="formState.city"
                  :items="cityOptions || []"
                  :loading="citiesLoading"
                  :disabled="!formState.region || citiesLoading"
                  placeholder="Выберите город"
                  :search-input="{
                      placeholder: 'Поиск...',
                      icon: 'i-lucide-search'
                    }"
                  searchable
              />
              <p v-if="citiesError" class="text-red-500 text-sm mt-1">
                Не удалось загрузить список городов: {{ citiesError?.message || 'Неизвестная ошибка' }}
              </p>
              <p v-if="formState.region && !citiesLoading && !cityOptions?.length" class="text-gray-500 text-sm mt-1">
                Для выбранного региона список городов недоступен. Введите название города вручную.
              </p>
            </UFormField>
          </div>
        </div>

        <!-- 3. Реквизиты компании -->
        <div>
          <h4 class="text-lg font-medium mb-4 text-gray-700 border-b pb-2">Реквизиты компании</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <UFormField label="Полное название организации" required>
              <UInput
                  v-model="formState.companyName"
                  class="min-w-4/5"
              />
            </UFormField>

            <UFormField label="ИНН" required>
              <UInput
                  v-model="formState.inn"
                  type="number"
              />
            </UFormField>

            <UFormField label="ОГРН" required>
              <UInput
                  v-model="formState.ogrn"
                  type="number"
              />
            </UFormField>

            <UFormField label="КПП" required>
              <UInput
                  v-model="formState.kpp"
                  type="number"
              />
            </UFormField>

            <UFormField label="Дата регистрации ОГРН" required>
              <UInput
                  v-model="formState.registrationDate"
                  type="date"
              />
            </UFormField>
          </div>
        </div>

        <!-- 4. Должностные лица -->
        <div>
          <h4 class="text-lg font-medium mb-4 text-gray-700 border-b pb-2">Должностные лица</h4>
          <div class="space-y-4">
            <div v-for="(official, index) in officials" :key="index" class="flex items-end gap-4">
              <UFormField label="Должность" required class="flex-1">
                <USelect
                    v-model="official.position"
                    :items="positionOptions || []"
                    placeholder="Выберите должность"
                />
              </UFormField>
              <UFormField label="ФИО" required class="flex-1">
                <UInput
                    v-model="official.fullName"
                    placeholder="Например: Иванова И.И."
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

        <!-- 5. Контактные данные -->
        <div>
          <h4 class="text-lg font-medium mb-4 text-gray-700 border-b pb-2">Контактные данные</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <UFormField label="Юридический адрес" required>
              <UInput
                  v-model="formState.companyAddress"
                  class="min-w-full"
              />
            </UFormField>

            <UFormField label="Адрес производства" required>
              <UInput
                  v-model="formState.productionAddress"
                  class="min-w-full"
              />
            </UFormField>

            <UFormField label="Телефон" required>
              <UInput
                  v-model="formState.companyPhone"
                  type="tel"
              />
            </UFormField>

            <UFormField label="Электронная почта" required>
              <UInput
                  v-model="formState.companyEmail"
                  type="email"
              />
            </UFormField>

            <UFormField label="Официальный сайт компании">
              <UInput
                  v-model="formState.companyWebsite"
                  type="url"
                  placeholder="https://example.com"
              />
            </UFormField>
          </div>
        </div>
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