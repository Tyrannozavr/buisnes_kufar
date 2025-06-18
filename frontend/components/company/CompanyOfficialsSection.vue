<script setup lang="ts">
import type { CompanyOfficial, CompanyOfficialBase } from '~/types/company'
import { useOfficialsApi } from '~/api/me/officials'

const props = defineProps<{
  officials: CompanyOfficial[]
}>()

const emit = defineEmits(['update:officials'])

const { getOfficials, createOfficial, updateOfficial, deleteOfficial } = useOfficialsApi()

const loading = ref(false)
const error = ref<string | undefined>(undefined)

// Добавляем debounce для обновления
const updateTimeout = ref<NodeJS.Timeout | null>(null)

// Добавляем состояние для временных должностных лиц (которые еще не созданы)
const tempOfficials = ref<Array<{ id: string, position: string, full_name: string, isTemp: boolean }>>([])

// Добавляем состояние для режима редактирования
const editingOfficials = ref<Set<number | string>>(new Set())

// Добавляем состояние для временных данных редактирования
const editData = ref<Map<number | string, { position: string, full_name: string }>>(new Map())

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

// Получаем все должностные лица (включая временные)
const allOfficials = computed(() => {
  return [...props.officials, ...tempOfficials.value]
})

// Загружаем должностных лиц при монтировании компонента
onMounted(async () => {
  // Если officials уже есть в props, не загружаем их заново
  if (props.officials.length === 0) {
    await loadOfficials()
  }
})

// Очищаем таймаут при размонтировании
onUnmounted(() => {
  if (updateTimeout.value) {
    clearTimeout(updateTimeout.value)
  }
})

// Загружаем должностных лиц
const loadOfficials = async () => {
  loading.value = true
  error.value = undefined
  try {
    const officials = await getOfficials()
    emit('update:officials', officials)
  } catch (e: any) {
    error.value = e.message || 'Ошибка загрузки должностных лиц'
    useToast().add({ title: 'Ошибка', description: error.value, color: 'error' })
  } finally {
    loading.value = false
  }
}

// Добавляем новую форму должностного лица (без отправки запроса)
const addOfficialForm = () => {
  const tempId = `temp_${Date.now()}_${Math.random()}`
  tempOfficials.value.push({
    id: tempId,
    position: '',
    full_name: '',
    isTemp: true
  })
  
  // Сразу включаем режим редактирования для новой записи
  startEditing(tempId)
}

// Создаем должностное лицо на сервере
const createOfficialOnServer = async (tempOfficial: { id: string, position: string, full_name: string, isTemp: boolean }) => {
  loading.value = true
  error.value = undefined
  try {
    const newOfficialData: CompanyOfficialBase = {
      position: tempOfficial.position,
      full_name: tempOfficial.full_name
    }
    const newOfficial = await createOfficial(newOfficialData)
    
    // Удаляем временного должностного лица из списка
    tempOfficials.value = tempOfficials.value.filter(o => o.id !== tempOfficial.id)
    
    // Добавляем созданного должностного лица в основной список
    emit('update:officials', [...props.officials, newOfficial])
    
    useToast().add({ title: 'Успешно', description: 'Должностное лицо добавлено', color: 'success' })
  } catch (e: any) {
    error.value = e.message || 'Ошибка добавления должностного лица'
    useToast().add({ title: 'Ошибка', description: error.value, color: 'error' })
  } finally {
    loading.value = false
  }
}

// Удаляем должностное лицо
const removeOfficial = async (officialId: number | string) => {
  // Если это временный должностное лицо, просто удаляем из списка
  if (typeof officialId === 'string') {
    tempOfficials.value = tempOfficials.value.filter(o => o.id !== officialId)
    editingOfficials.value.delete(officialId)
    editData.value.delete(officialId)
    return
  }
  
  loading.value = true
  error.value = undefined
  try {
    await deleteOfficial(officialId)
    const newOfficials = props.officials.filter(official => official.id !== officialId)
    emit('update:officials', newOfficials)
    editingOfficials.value.delete(officialId)
    editData.value.delete(officialId)
    useToast().add({ title: 'Успешно', description: 'Должностное лицо удалено', color: 'success' })
  } catch (e: any) {
    error.value = e.message || 'Ошибка удаления должностного лица'
    useToast().add({ title: 'Ошибка', description: error.value, color: 'error' })
  } finally {
    loading.value = false
  }
}

// Включаем режим редактирования
const startEditing = (officialId: number | string) => {
  const official = allOfficials.value.find(o => o.id === officialId)
  if (!official) return
  
  editingOfficials.value.add(officialId)
  editData.value.set(officialId, {
    position: official.position,
    full_name: official.full_name
  })
}

// Отменяем редактирование
const cancelEditing = (officialId: number | string) => {
  editingOfficials.value.delete(officialId)
  editData.value.delete(officialId)
}

// Сохраняем изменения
const saveChanges = async (officialId: number | string) => {
  const editInfo = editData.value.get(officialId)
  if (!editInfo) return
  
  // Проверяем, заполнены ли оба поля
  if (!editInfo.position || !editInfo.full_name) {
    useToast().add({ title: 'Ошибка', description: 'Заполните все поля', color: 'error' })
    return
  }
  
  // Если это временный должностное лицо
  if (typeof officialId === 'string') {
    await createOfficialOnServer({
      id: officialId,
      position: editInfo.position,
      full_name: editInfo.full_name,
      isTemp: true
    })
    editingOfficials.value.delete(officialId)
    editData.value.delete(officialId)
    return
  }
  
  // Если это существующий должностное лицо
  loading.value = true
  error.value = undefined
  try {
    const updateData: CompanyOfficialBase = {
      position: editInfo.position,
      full_name: editInfo.full_name
    }
    
    const updatedOfficial = await updateOfficial(officialId as number, updateData)
    const newOfficials = props.officials.map(o => 
      o.id === officialId ? updatedOfficial : o
    )
    emit('update:officials', newOfficials)
    editingOfficials.value.delete(officialId)
    editData.value.delete(officialId)
    useToast().add({ title: 'Успешно', description: 'Должностное лицо обновлено', color: 'success' })
  } catch (e: any) {
    error.value = e.message || 'Ошибка обновления должностного лица'
    useToast().add({ title: 'Ошибка', description: error.value, color: 'error' })
  } finally {
    loading.value = false
  }
}

// Обновляем должностное лицо (теперь только для временных записей)
const updateOfficialData = async (officialId: number | string, field: keyof CompanyOfficialBase, value: string) => {
  // Если в режиме редактирования, обновляем временные данные
  if (editingOfficials.value.has(officialId)) {
    const editInfo = editData.value.get(officialId)
    if (editInfo) {
      editInfo[field] = value
    }
    return
  }
  
  // Если это временный должностное лицо и не в режиме редактирования (старая логика)
  if (typeof officialId === 'string') {
    const tempOfficial = tempOfficials.value.find(o => o.id === officialId)
    if (!tempOfficial) return
    
    // Обновляем временного должностного лица
    tempOfficial[field] = value
    
    // Проверяем, заполнены ли оба поля
    if (tempOfficial.position && tempOfficial.full_name) {
      // Очищаем предыдущий таймаут
      if (updateTimeout.value) {
        clearTimeout(updateTimeout.value)
      }
      
      // Устанавливаем новый таймаут для создания на сервере
      updateTimeout.value = setTimeout(async () => {
        await createOfficialOnServer(tempOfficial)
      }, 500)
    }
    return
  }
  
  // Для существующих должностных лиц без режима редактирования - старая логика
  const official = props.officials.find(o => o.id === officialId)
  if (!official) return
  
  // Обновляем локальное состояние сразу
  const newOfficials = props.officials.map(o => 
    o.id === officialId ? { ...o, [field]: value } : o
  )
  emit('update:officials', newOfficials)
  
  // Проверяем, заполнены ли оба поля
  const updatedOfficial = newOfficials.find(o => o.id === officialId)
  if (!updatedOfficial || !updatedOfficial.position || !updatedOfficial.full_name) {
    return // Не отправляем запрос если не все поля заполнены
  }
  
  // Очищаем предыдущий таймаут
  if (updateTimeout.value) {
    clearTimeout(updateTimeout.value)
  }
  
  // Устанавливаем новый таймаут для API вызова
  updateTimeout.value = setTimeout(async () => {
    const updateData: Partial<CompanyOfficialBase> = {
      [field]: value
    }
    
    try {
      const serverUpdatedOfficial = await updateOfficial(officialId as number, updateData)
      const finalOfficials = props.officials.map(o => 
        o.id === officialId ? serverUpdatedOfficial : o
      )
      emit('update:officials', finalOfficials)
    } catch (e: any) {
      error.value = e.message || 'Ошибка обновления должностного лица'
      useToast().add({ title: 'Ошибка', description: error.value, color: 'error' })
    }
  }, 500)
}
</script>

<template>
  <div>
    <h4 class="text-lg font-medium mb-4 text-gray-700 border-b pb-2">Должностные лица</h4>
    
    <div v-if="error" class="mb-4 p-4 bg-red-50 text-red-700 rounded-md">
      {{ error }}
    </div>
    
    <div class="space-y-4">
      <div v-if="allOfficials.length === 0 && !loading" class="text-center py-8 text-gray-500">
        <p>Должностные лица не добавлены</p>
        <p class="text-sm mt-2">Нажмите кнопку ниже, чтобы добавить должностное лицо</p>
      </div>
      
      <div v-for="(official, index) in allOfficials" :key="official.id" class="flex items-end gap-4">
        <UFormField label="Должность" required class="flex-1">
          <USelect
              :model-value="editingOfficials.has(official.id) ? editData.get(official.id)?.position : official.position"
              :items="positionOptions"
              placeholder="Выберите должность"
              :disabled="loading"
              @update:model-value="value => updateOfficialData(official.id, 'position', value)"
          />
        </UFormField>
        <UFormField label="ФИО" required class="flex-1">
          <UInput
              :model-value="editingOfficials.has(official.id) ? editData.get(official.id)?.full_name : official.full_name"
              placeholder="Например: Иванова И.И."
              :disabled="loading"
              @update:model-value="value => updateOfficialData(official.id, 'full_name', value)"
          />
        </UFormField>
        
        <!-- Кнопки действий -->
        <div class="flex gap-2 mb-1">
          <!-- Кнопка редактирования/сохранения -->
          <UButton
              v-if="!editingOfficials.has(official.id)"
              color="primary"
              variant="soft"
              icon="i-heroicons-pencil"
              :loading="loading"
              :disabled="loading"
              @click="startEditing(official.id)"
          >
            Изменить
          </UButton>
          <UButton
              v-else
              color="success"
              variant="soft"
              icon="i-heroicons-check"
              :loading="loading"
              :disabled="loading"
              @click="saveChanges(official.id)"
          >
            Сохранить
          </UButton>
          
          <!-- Кнопка отмены редактирования -->
          <UButton
              v-if="editingOfficials.has(official.id)"
              color="neutral"
              variant="soft"
              icon="i-heroicons-x-mark"
              :loading="loading"
              :disabled="loading"
              @click="cancelEditing(official.id)"
          >
            Отмена
          </UButton>
          
          <!-- Кнопка удаления -->
          <UButton
              color="error"
              variant="soft"
              icon="i-heroicons-trash"
              :loading="loading"
              :disabled="loading"
              @click="removeOfficial(official.id)"
          />
        </div>
      </div>
      <UButton
          color="primary"
          variant="soft"
          icon="i-heroicons-plus"
          :loading="loading"
          :disabled="loading"
          @click="addOfficialForm"
      >
        Добавить должностное лицо
      </UButton>
    </div>
  </div>
</template> 