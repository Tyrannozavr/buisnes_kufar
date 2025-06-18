<script setup lang="ts">
import type { CompanyDataFormState } from '~/types/company'
import type { LocationItem } from '~/types/location'
import { useLocationsApi } from '~/api/locations'
import UCombobox from '~/components/ui/UCombobox.vue'

const props = defineProps<{
  formState: CompanyDataFormState
}>()

const emit = defineEmits(['update:formState'])

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

// Добавляем состояние для поискового запроса города
const citySearchQuery = ref('')
const citySearchTimeout = ref<NodeJS.Timeout | null>(null)

// Watch для страны
watch(() => props.formState.country, async (newCountry) => {
  // Сбрасываем все зависимые поля
  emit('update:formState', {
    ...props.formState,
    federalDistrict: undefined,
    region: undefined,
    city: undefined
  })
  citySearchQuery.value = '' // Сбрасываем поисковый запрос

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
watch(() => props.formState.federalDistrict, async (newFederalDistrict) => {
  // Сбрасываем зависимые поля
  emit('update:formState', {
    ...props.formState,
    region: undefined,
    city: undefined
  })
  citySearchQuery.value = '' // Сбрасываем поисковый запрос

  if (!newFederalDistrict || !props.formState.country || props.formState.country.value !== 'Россия') {
    return
  }

  try {
    // Загружаем регионы только после выбора федерального округа для России
    await loadRegions(props.formState.country.value, newFederalDistrict.value)
  } catch (error) {
    console.error('Error handling federal district change:', error)
  }
})

// Watch для региона
watch(() => props.formState.region, async (newRegion) => {
  if (!newRegion || !props.formState.country) {
    emit('update:formState', {
      ...props.formState,
      city: undefined
    })
    citySearchQuery.value = '' // Сбрасываем поисковый запрос
    return
  }
  // Убираем автоматическую загрузку городов при выборе региона
})

// Watch для поискового запроса города
watch(citySearchQuery, async (newQuery: string) => {
  // Очищаем предыдущий таймаут
  if (citySearchTimeout.value) {
    clearTimeout(citySearchTimeout.value)
  }

  // Если запрос короче 2 символов, очищаем список городов
  if (newQuery.length < 2) {
    cityOptions.value = []
    return
  }

  // Устанавливаем таймаут для предотвращения частых запросов
  citySearchTimeout.value = setTimeout(async () => {
    try {
      if (props.formState.country?.value && props.formState.region?.value) {
        await loadCities(
          props.formState.country.value,
          props.formState.region.value,
          1,
          newQuery
        )
      }
    } catch (error) {
      console.error('Error searching cities:', error)
    }
  }, 300) // Задержка 300мс для предотвращения частых запросов
})

const updateField = (field: keyof CompanyDataFormState, value: any) => {
  emit('update:formState', {
    ...props.formState,
    [field]: value
  })
}
</script>

<template>
  <div>
    <h4 class="text-lg font-medium mb-4 text-gray-700 border-b pb-2">Информация о компании</h4>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <UFormField label="Торговая деятельность" required help="Выберите тип торговой деятельности вашей компании">
        <USelect
            :model-value="formState.tradeActivity"
            :items="tradeActivityOptions"
            class="min-w-1/2"
            @update:model-value="value => updateField('tradeActivity', value)"
        />
      </UFormField>

      <UFormField label="Род деятельности" required
                  help="Определяет в каком разделе будет отображаться ваша компания">
        <USelect
            :model-value="formState.businessType"
            :items="businessTypeOptions"
            class="min-w-1/2"
            @update:model-value="value => updateField('businessType', value)"
        />
      </UFormField>

      <UFormField label="Название организации" required help="Краткое название для отображения в карточке компании и списках">
        <UInput
            :model-value="formState.name"
            placeholder="Например: ЭкоПродукт"
            class="min-w-1/2"
            @update:model-value="value => updateField('name', value)"
        />
      </UFormField>

      <UFormField label="Полное юридическое название" required help="Полное название организации с указанием организационно-правовой формы">
        <UInput
            :model-value="formState.fullName"
            placeholder="Например: ООО 'ЭкоПродукт'"
            class="min-w-1/2"
            @update:model-value="value => updateField('fullName', value)"
        />
      </UFormField>

      <UFormField label="Вид деятельности" required
                  help="Основное направление деятельности компании. Например: «Производство обуви», «Строительство каркасных домов»">
        <UInput
            :model-value="formState.activityType"
            placeholder="Например: Производство обуви"
            class="min-w-full"
            @update:model-value="value => updateField('activityType', value)"
        />
      </UFormField>

      <UFormField label="Описание организации" required
                  help="Опишите деятельность компании и ее основные достоинства" class="md:col-span-2">
        <UTextarea
            :model-value="formState.description"
            placeholder="Опишите деятельность компании и ее основные достоинства"
            :rows="4"
            class="min-w-2/5"
            @update:model-value="value => updateField('description', value)"
        />
      </UFormField>

      <UFormField label="Страна" required>
        <UCombobox
            :model-value="formState.country"
            class="w-48"
            :items="countryOptions || []"
            :loading="countriesLoading"
            :disabled="countriesLoading || !!countriesError"
            placeholder="Выберите страну"
            :search-input="{
                placeholder: 'Поиск...',
                icon: 'i-lucide-search'
              }"
            searchable
            @update:model-value="value => updateField('country', value)"
        />
        <p v-if="countriesError" class="text-red-500 text-sm mt-1">
          Не удалось загрузить список стран. Пожалуйста, попробуйте позже.
        </p>
      </UFormField>

      <UFormField label="Федеральный округ" required>
        <UCombobox
            :model-value="formState.federalDistrict"
            :items="federalDistrictOptions || []"
            :loading="federalDistrictsLoading"
            class="w-48"
            :disabled="formState.country?.value !== 'Россия' || federalDistrictsLoading || !!federalDistrictsError"
            placeholder="Выберите федеральный округ"
            :search-input="{
                placeholder: 'Поиск...',
                icon: 'i-lucide-search'
              }"
            searchable
            @update:model-value="value => updateField('federalDistrict', value)"
        />
        <p v-if="federalDistrictsError" class="text-red-500 text-sm mt-1">
          Не удалось загрузить список федеральных округов. Пожалуйста, попробуйте позже.
        </p>
        <p v-if="formState.country && formState.country.value !== 'Россия'" class="text-gray-500 text-sm mt-1">
          Федеральный округ доступен только для России
        </p>
      </UFormField>

      <UFormField label="Регион" required>
        <UCombobox
            :model-value="formState.region"
            :items="regionOptions || []"
            :loading="regionsLoading"
            class="w-48"
            :disabled="!formState.country ||
                     (formState.country.value === 'Россия' && !formState.federalDistrict) ||
                     regionsLoading"
            placeholder="Выберите регион"
            :search-input="{
                placeholder: 'Поиск...',
                icon: 'i-lucide-search'
              }"
            searchable
            @update:model-value="value => updateField('region', value)"
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
        <UCombobox
            :model-value="formState.city"
            :items="cityOptions || []"
            :loading="citiesLoading"
            :disabled="!formState.region"
            :disabled-message="!formState.region ? 'Сначала выберите регион' : ''"
            class="w-48"
            placeholder="Введите название города (минимум 2 символа)"
            :search-input="{
                modelValue: citySearchQuery,
                'onUpdate:modelValue': (val: string) => { citySearchQuery = val },
                placeholder: 'Поиск города...',
                icon: 'i-lucide-search'
              }"
            @update:model-value="(value: LocationItem | undefined) => updateField('city', value)"
        />
        <p v-if="citiesError" class="text-red-500 text-sm mt-1">
          Не удалось загрузить список городов: {{ citiesError?.message || 'Неизвестная ошибка' }}
        </p>
        <p v-if="citySearchQuery.length > 0 && citySearchQuery.length < 2" class="text-gray-500 text-sm mt-1">
          Введите минимум 2 символа для поиска города
        </p>
      </UFormField>
    </div>
  </div>
</template> 