<script setup lang="ts">
import type { CompanyDataFormState } from '~/types/company'
import type { LocationItem } from '~/types/location'
import { useLocationsDbApi } from '~/api/locations-db'
import UCombobox from '~/components/ui/UCombobox.vue'
import CompanyTypeSelect from '~/components/company/CompanyTypeSelect.vue'

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
  loadCities,
  createRegion,
  createCity
} = useLocationsDbApi()

// Добавляем состояние для поискового запроса города
const citySearchQuery = ref('')
const citySearchTimeout = ref<NodeJS.Timeout | null>(null)

// Watch для страны (опционально загружаем данные из БД)
watch(() => props.formState.country, async (newCountry) => {
  // Сбрасываем федеральный округ при смене страны (кроме России)
  if (newCountry?.value !== 'RU') {
    emit('update:formState', {
      ...props.formState,
      federalDistrict: undefined
    })
  }
  
  citySearchQuery.value = '' // Сбрасываем поисковый запрос

  if (!newCountry) {
    return
  }

  try {
    // Загружаем федеральные округи только для России
    if (newCountry.value === 'RU' || newCountry.value === 'Россия') {
      await loadFederalDistricts('RU')
    } else {
      // Для других стран сразу загружаем регионы
      await loadRegions(newCountry.value)
    }
  } catch (error) {
    console.error('Error handling country change:', error)
  }
})

// Watch для федерального округа (загружаем регионы для России)
watch(() => props.formState.federalDistrict, async (newFederalDistrict) => {
  // Не сбрасываем city - пользователь может вводить произвольные данные
  citySearchQuery.value = '' // Сбрасываем поисковый запрос

  if (!newFederalDistrict || !props.formState.country || props.formState.country.value !== 'RU') {
    return
  }

  try {
    // Загружаем регионы для выбранного федерального округа
    await loadRegions(props.formState.country.value, newFederalDistrict.value)
  } catch (error) {
    console.error('Error handling federal district change:', error)
  }
})

// Watch для региона (опционально загружаем города из БД)
watch(() => props.formState.region, async (newRegion) => {
  // Не сбрасываем city, чтобы пользователь мог вводить произвольные данные
  citySearchQuery.value = '' // Сбрасываем поисковый запрос
  
  if (!newRegion || !props.formState.country) {
    return
  }
  
  try {
    // Загружаем города для выбранного региона (необязательно)
    await loadCities(
      props.formState.country.value,
      newRegion.value,
      props.formState.federalDistrict?.value
    )
  } catch (error) {
    console.error('Error loading cities for region:', error)
  }
})

// Watch для поискового запроса города
watch(citySearchQuery, async (newQuery: string) => {
  // Очищаем предыдущий таймаут
  if (citySearchTimeout.value) {
    clearTimeout(citySearchTimeout.value)
  }

  // Если запрос короче 2 символов, не делаем поиск, но оставляем уже загруженные города
  if (newQuery.length < 2) {
    return
  }

  // Устанавливаем таймаут для предотвращения частых запросов
  citySearchTimeout.value = setTimeout(async () => {
    try {
      if (props.formState.country?.value && props.formState.region?.value) {
        await loadCities(
          props.formState.country.value,
          props.formState.region.value,
          props.formState.federalDistrict?.value,
          newQuery
        )
      }
    } catch (error) {
      console.error('Error searching cities:', error)
    }
  }, 300) // Задержка 300мс для предотвращения частых запросов
})

// Функция для форматирования названий (первая буква заглавная, остальные строчные)
const formatLocationName = (name: string): string => {
  if (!name || name.length === 0) return name
  
  // Разбиваем по пробелам и форматируем каждое слово
  return name
    .split(' ')
    .map(word => {
      if (word.length === 0) return word
      return word[0].toUpperCase() + word.slice(1).toLowerCase()
    })
    .join(' ')
}

// Обработчик blur для региона - создание нового региона при необходимости
const handleRegionBlur = async () => {
  const currentRegionValue = props.formState.region?.value || props.formState.region?.label
  
  console.log('🔍 handleRegionBlur вызван', {
    currentRegionValue,
    regionValue: props.formState.region?.value,
    regionLabel: props.formState.region?.label,
    countryValue: props.formState.country?.value
  })
  
  // Если регион не выбран и есть текст
  if (!currentRegionValue || currentRegionValue.trim().length === 0) {
    console.log('⚠️ Регион пустой, выходим')
    return
  }

  // Проверяем, существует ли регион в списке
  const regionExists = regionOptions.value.some(
    r => r.value.toLowerCase() === currentRegionValue.toLowerCase() || 
         r.label.toLowerCase() === currentRegionValue.toLowerCase()
  )
  
  console.log('🔍 Проверка существования региона', { regionExists, currentRegionValue })

  if (!regionExists && props.formState.country?.value) {
    try {
      const formattedName = formatLocationName(currentRegionValue)
      
      console.log('✨ Создание региона', {
        countryCode: props.formState.country.value,
        regionName: formattedName,
        federalDistrictCode: props.formState.federalDistrict?.value
      })
      
      // Пытаемся создать новый регион
      const result = await createRegion(
        props.formState.country.value,
        formattedName,
        props.formState.federalDistrict?.value
      )
      
      console.log('✅ Результат создания региона', result)
      if (result.success) {
        // Добавляем созданный регион в список опций
        regionOptions.value.push({
          label: formattedName,
          value: formattedName
        })
        
        // Устанавливаем созданный регион как выбранный
        updateField('region', {
          label: formattedName,
          value: formattedName
        })
        
        // Показываем уведомление
        useToast().add({
          title: 'Успешно',
          description: `Регион "${formattedName}" создан`,
          color: 'success'
        })
      }
    } catch (error: any) {
      console.error('❌ Error creating region:', error)
      // Не показываем ошибку, регион может уже существовать
    }
  } else {
    console.log('ℹ️ Регион уже существует или страна не выбрана')
  }
}

// Обработчик blur для города - создание нового города при необходимости
const handleCityBlur = async () => {
  const currentCityValue = props.formState.city?.value || props.formState.city?.label
  
  console.log('🔍 handleCityBlur вызван', {
    currentCityValue,
    cityValue: props.formState.city?.value,
    cityLabel: props.formState.city?.label,
    countryValue: props.formState.country?.value,
    regionValue: props.formState.region?.value
  })
  
  // Если город не выбран и есть текст
  if (!currentCityValue || currentCityValue.trim().length === 0) {
    console.log('⚠️ Город пустой, выходим')
    return
  }

  // Проверяем, существует ли город в списке
  const cityExists = cityOptions.value.some(
    c => c.value.toLowerCase() === currentCityValue.toLowerCase() || 
         c.label.toLowerCase() === currentCityValue.toLowerCase()
  )
  
  console.log('🔍 Проверка существования города', { cityExists, currentCityValue })

  if (!cityExists && props.formState.country?.value && props.formState.region?.value) {
    try {
      const formattedName = formatLocationName(currentCityValue)
      const regionName = props.formState.region.label || props.formState.region.value
      
      console.log('✨ Создание города', {
        countryCode: props.formState.country.value,
        regionName: regionName,
        cityName: formattedName,
        federalDistrictCode: props.formState.federalDistrict?.value
      })
      
      // Пытаемся создать новый город
      const result = await createCity(
        props.formState.country.value,
        regionName,
        formattedName,
        props.formState.federalDistrict?.value
      )
      
      console.log('✅ Результат создания города', result)
      if (result.success) {
        // Добавляем созданный город в список опций
        cityOptions.value.push({
          label: formattedName,
          value: formattedName
        })
        
        // Устанавливаем созданный город как выбранный
        updateField('city', {
          label: formattedName,
          value: formattedName
        })
        
        // Показываем уведомление
        useToast().add({
          title: 'Успешно',
          description: `Город "${formattedName}" создан`,
          color: 'success'
        })
      }
    } catch (error: any) {
      console.error('❌ Error creating city:', error)
    }
  } else {
    console.log('ℹ️ Город уже существует или регион не выбран')
  }
}

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

      <CompanyTypeSelect
          :model-value="formState.type"
          required
          @update:model-value="value => updateField('type', value)"
      />

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
            :disabled="countriesLoading"
            placeholder="Выберите страну или введите произвольное название"
            searchable
            @update:model-value="value => updateField('country', value)"
        />
        <p v-if="countriesError" class="text-gray-500 text-sm mt-1">
          Вы можете ввести любую страну вручную. Нажмите Enter для сохранения.
        </p>
        <p class="text-gray-500 text-sm mt-1">
          Нажмите Enter для сохранения произвольного названия
        </p>
      </UFormField>

      <UFormField label="Федеральный округ" required>
        <UCombobox
            :model-value="formState.federalDistrict"
            :items="federalDistrictOptions || []"
            :loading="federalDistrictsLoading"
            class="w-48"
            :disabled="formState.country?.value !== 'RU' || federalDistrictsLoading"
            :disabled-message="formState.country?.value !== 'RU' ? 'Федеральный округ доступен только для России' : ''"
            placeholder="Выберите федеральный округ или введите произвольное название"
            searchable
            @update:model-value="value => updateField('federalDistrict', value)"
        />
        <p v-if="federalDistrictsError" class="text-gray-500 text-sm mt-1">
          Вы можете ввести любой федеральный округ вручную. Нажмите Enter для сохранения.
        </p>
        <p v-if="formState.country && formState.country.value !== 'RU'" class="text-gray-500 text-sm mt-1">
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
                     (formState.country.value === 'RU' && !formState.federalDistrict) ||
                     regionsLoading"
            :disabled-message="!formState.country 
              ? 'Сначала выберите страну' 
              : (formState.country.value === 'RU' && !formState.federalDistrict 
                ? 'Сначала выберите федеральный округ' 
                : '')"
            placeholder="Выберите регион или введите произвольное название"
            searchable
            allow-custom-input
            :on-blur="handleRegionBlur"
            @update:model-value="value => updateField('region', value)"
        />
        <p v-if="regionsError" class="text-gray-500 text-sm mt-1">
          Вы можете ввести любой регион вручную. Нажмите Enter для сохранения.
        </p>
        <p v-if="formState.country?.value === 'RU' && !formState.federalDistrict" class="text-gray-500 text-sm mt-1">
          Выберите федеральный округ для загрузки списка регионов
        </p>
      </UFormField>

      <UFormField label="Город" required>
        <UCombobox
            :model-value="formState.city"
            :items="cityOptions || []"
            :loading="citiesLoading"
            class="w-48"
            placeholder="Выберите город или введите произвольное название"
            searchable
            allow-custom-input
            :on-blur="handleCityBlur"
            @update:model-value="(value: LocationItem | undefined) => updateField('city', value)"
        />
        <p class="text-gray-500 text-sm mt-1">
          Нажмите Enter для сохранения произвольного названия города
        </p>
      </UFormField>

			 <UFormField label="Индекс" required help="Почтовый индекс">
        <UInput
            maxlength="6"
            :model-value="formState.index"
            placeholder="Например: 620000"
            class="min-w-1/2"
            @update:model-value="value => updateField('index', value)"
        />
      </UFormField>
    </div>
  </div>
</template> 