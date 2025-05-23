<script setup lang="ts">
import type { Company } from '~/types/company'
import type { PropType } from 'vue'

const props = defineProps({
  company: {
    type: Object as PropType<Company>,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emits = defineEmits(['save'])

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

// Fetch countries from API
const { data: countryOptions, error: countriesError } = await useApi('/locations/countries')

// Fetch federal districts from API
const { data: federalDistrictOptions, error: federalDistrictsError } = await useApi('/locations/federal-districts')

// Reactive query for regions based on selected country and federal district
const regionsQuery = computed(() => ({
  country: formState.value.country,
  federalDistrict: formState.value.federalDistrict
}))

// Fetch regions based on selected country and federal district
const { data: regionOptions, error: regionsError, refresh: refreshRegions } = await useApi('/locations/regions', {
  query: regionsQuery
})

// Watch for changes in country or federal district to refresh regions
watch([() => formState.value.country, () => formState.value.federalDistrict], () => {
  refreshRegions()
})

interface PositionOption {
  label: string
  value: string
}

const positionOptions = [
  { label: 'Генеральный директор', value: 'Генеральный директор' },
  { label: 'Финансовый директор', value: 'Финансовый директор' },
  { label: 'Главный бухгалтер', value: 'Главный бухгалтер' },
  { label: 'Коммерческий директор', value: 'Коммерческий директор' },
  { label: 'Технический директор', value: 'Технический директор' },
  { label: 'Руководитель отдела продаж', value: 'Руководитель отдела продаж' },
  { label: 'Руководитель отдела закупок', value: 'Руководитель отдела закупок' },
  { label: 'Руководитель производства', value: 'Руководитель производства' }
]

const officials = ref(props.company.officials || [{ position: '', fullName: '' }])

const addOfficial = () => {
  officials.value.push({ position: '', fullName: '' })
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
                :src="formState.logo || undefined"
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

            <UFormField label="Род деятельности" required help="Определяет в каком разделе будет отображаться ваша компания">
              <USelect
                  v-model="formState.businessType"
                  :items="businessTypeOptions"
                  class="min-w-1/2"

              />
            </UFormField>

            <UFormField label="Название организации" required help="Краткое название организации для визитной карточки">
              <UInput
                  v-model="formState.name"
                  placeholder="Краткое название организации"
                  class="min-w-1/2"
              />
            </UFormField>

            <UFormField label="Вид деятельности" required help="Основное направление деятельности компании. Например: «Производство обуви», «Строительство каркасных домов»">
              <UInput
                  v-model="formState.activityType"
                  placeholder="Например: Производство обуви"
                  class="min-w-full"
              />
            </UFormField>

            <UFormField label="Описание организации" required help="Опишите деятельность компании и ее основные достоинства" class="md:col-span-2">
              <UTextarea
                  v-model="formState.description"
                  placeholder="Опишите деятельность компании и ее основные достоинства"
                  :rows="4"
                  class="min-w-2/5"
              />
            </UFormField>

            <UFormField label="Страна" required>
              <USelect
                  v-model="formState.country"
                  :items="countryOptions || []"
                  :loading="!countryOptions && !countriesError"
                  :disabled="!countryOptions || !!countriesError"
              />
              <p v-if="countriesError" class="text-red-500 text-sm mt-1">
                Ошибка загрузки списка стран
              </p>
            </UFormField>

            <UFormField label="Федеральный округ" required>
              <USelect
                  v-model="formState.federalDistrict"
                  :items="federalDistrictOptions || []"
                  :loading="!federalDistrictOptions && !federalDistrictsError"
                  :disabled="formState.country !== 'Россия' || !federalDistrictOptions || !!federalDistrictsError"
              />
              <p v-if="federalDistrictsError" class="text-red-500 text-sm mt-1">
                Ошибка загрузки списка федеральных округов
              </p>
            </UFormField>

            <UFormField label="Регион" required>
              <USelect
                  v-model="formState.region"
                  :items="regionOptions || []"
                  :loading="!regionOptions && !regionsError"
                  :disabled="!regionOptions || !!regionsError"
              />
              <p v-if="regionsError" class="text-red-500 text-sm mt-1">
                Ошибка загрузки списка регионов
              </p>
            </UFormField>

            <UFormField label="Город" required>
              <UInput
                  v-model="formState.city"
              />
            </UFormField>
          </div>
        </div>

        <!-- 3. Реквизиты компании -->
        <div>
          <h4 class="text-lg font-medium mb-4 text-gray-700 border-b pb-2">Реквизиты компании</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <UFormField label="Полное название организации" required>
              <UInput
                  v-model="formState.fullName"
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
                  v-model="formState.legalAddress"
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
                  v-model="formState.phone"
                  type="tel"
              />
            </UFormField>

            <UFormField label="Электронная почта" required>
              <UInput
                  v-model="formState.email"
                  type="email"
              />
            </UFormField>

            <UFormField label="Официальный сайт компании">
              <UInput
                  v-model="formState.website"
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