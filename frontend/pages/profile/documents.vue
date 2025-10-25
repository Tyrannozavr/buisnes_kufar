<script setup lang="ts">
import { ref, onMounted } from 'vue'

// Состояние
const documents = ref([
  {
    id: 1,
    name: 'Договор поставки №123',
    type: 'contract',
    size: '2.5 MB',
    uploadDate: '2024-01-15',
    status: 'active',
    category: 'Договоры'
  },
  {
    id: 2,
    name: 'Счет-фактура №456',
    type: 'invoice',
    size: '1.2 MB',
    uploadDate: '2024-01-14',
    status: 'active',
    category: 'Финансы'
  },
  {
    id: 3,
    name: 'Акт выполненных работ №789',
    type: 'act',
    size: '3.1 MB',
    uploadDate: '2024-01-13',
    status: 'archived',
    category: 'Документы'
  }
])

const loading = ref(false)
const showUploadModal = ref(false)
const selectedCategory = ref('all')
const searchQuery = ref('')

// Форма загрузки документа
const newDocument = ref({
  name: '',
  category: '',
  file: null as File | null
})

// Фильтры
const categories = [
  { label: 'Все категории', value: 'all' },
  { label: 'Договоры', value: 'contracts' },
  { label: 'Финансы', value: 'finance' },
  { label: 'Документы', value: 'documents' },
  { label: 'Отчеты', value: 'reports' }
]

// Вычисляемые свойства
const filteredDocuments = computed(() => {
  let filtered = documents.value

  if (selectedCategory.value !== 'all') {
    filtered = filtered.filter(doc => doc.category.toLowerCase() === selectedCategory.value)
  }

  if (searchQuery.value) {
    filtered = filtered.filter(doc => 
      doc.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  return filtered
})

// Методы
const uploadDocument = async () => {
  if (!newDocument.value.file || !newDocument.value.name) {
    useToast().add({
      title: 'Ошибка',
      description: 'Заполните все поля',
      color: 'error'
    })
    return
  }

  loading.value = true
  try {
    // Здесь будет API вызов для загрузки документа
    await new Promise(resolve => setTimeout(resolve, 1000)) // Имитация загрузки
    
    const newDoc = {
      id: Date.now(),
      name: newDocument.value.name,
      type: 'document',
      size: `${(newDocument.value.file.size / 1024 / 1024).toFixed(1)} MB`,
      uploadDate: new Date().toISOString().split('T')[0],
      status: 'active',
      category: newDocument.value.category
    }
    
    documents.value.unshift(newDoc)
    
    useToast().add({
      title: 'Успешно',
      description: 'Документ загружен',
      color: 'success'
    })
    
    showUploadModal.value = false
    resetUploadForm()
  } catch (error) {
    useToast().add({
      title: 'Ошибка',
      description: 'Не удалось загрузить документ',
      color: 'error'
    })
  } finally {
    loading.value = false
  }
}

const downloadDocument = (document: any) => {
  // Здесь будет логика скачивания документа
  useToast().add({
    title: 'Информация',
    description: `Скачивание документа: ${document.name}`,
    color: 'info'
  })
}

const deleteDocument = (documentId: number) => {
  const index = documents.value.findIndex(doc => doc.id === documentId)
  if (index !== -1) {
    documents.value.splice(index, 1)
    useToast().add({
      title: 'Успешно',
      description: 'Документ удален',
      color: 'success'
    })
  }
}

const archiveDocument = (documentId: number) => {
  const document = documents.value.find(doc => doc.id === documentId)
  if (document) {
    document.status = document.status === 'archived' ? 'active' : 'archived'
    useToast().add({
      title: 'Успешно',
      description: `Документ ${document.status === 'archived' ? 'архивирован' : 'восстановлен'}`,
      color: 'success'
    })
  }
}

const resetUploadForm = () => {
  newDocument.value = {
    name: '',
    category: '',
    file: null
  }
}

const getDocumentIcon = (type: string) => {
  const icons = {
    contract: 'i-heroicons-document-text',
    invoice: 'i-heroicons-receipt-percent',
    act: 'i-heroicons-clipboard-document-check',
    document: 'i-heroicons-document'
  }
  return icons[type as keyof typeof icons] || 'i-heroicons-document'
}

const getStatusColor = (status: string) => {
  const colors = {
    active: 'green',
    archived: 'gray'
  }
  return colors[status as keyof typeof colors] || 'gray'
}

const getStatusLabel = (status: string) => {
  const labels = {
    active: 'Активный',
    archived: 'Архивный'
  }
  return labels[status as keyof typeof labels] || status
}

// Жизненный цикл
onMounted(() => {
  // Загрузка документов
})

definePageMeta({
  layout: 'profile'
})
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-2xl font-bold text-gray-900">Документы</h1>
      <UButton @click="showUploadModal = true" color="primary">
        <UIcon name="i-heroicons-plus" class="mr-2" />
        Загрузить документ
      </UButton>
    </div>

    <!-- Фильтры и поиск -->
    <div class="mb-6 flex gap-4">
      <USelect
        v-model="selectedCategory"
        :options="categories"
        placeholder="Выберите категорию"
        class="w-48"
      />
      <UInput
        v-model="searchQuery"
        placeholder="Поиск по названию документа..."
        icon="i-heroicons-magnifying-glass"
        class="flex-1"
      />
    </div>

    <!-- Список документов -->
    <div class="bg-white shadow rounded-lg overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">
          Документы ({{ filteredDocuments.length }})
        </h3>
      </div>

      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500"></div>
      </div>

      <div v-else-if="filteredDocuments.length === 0" class="text-center py-12">
        <UIcon name="i-heroicons-document" class="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <p class="text-gray-500">Документы не найдены</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Документ
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Категория
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Размер
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Дата загрузки
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Статус
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Действия
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="document in filteredDocuments" :key="document.id">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 h-10 w-10">
                    <div class="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                      <UIcon :name="getDocumentIcon(document.type)" class="h-5 w-5 text-blue-600" />
                    </div>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">
                      {{ document.name }}
                    </div>
                    <div class="text-sm text-gray-500">
                      {{ document.type }}
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ document.category }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ document.size }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ document.uploadDate }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <UBadge :color="getStatusColor(document.status)">
                  {{ getStatusLabel(document.status) }}
                </UBadge>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                <UButton
                  size="sm"
                  variant="outline"
                  @click="downloadDocument(document)"
                >
                  <UIcon name="i-heroicons-arrow-down-tray" class="h-4 w-4" />
                </UButton>
                <UButton
                  size="sm"
                  variant="outline"
                  :color="document.status === 'archived' ? 'green' : 'gray'"
                  @click="archiveDocument(document.id)"
                >
                  <UIcon :name="document.status === 'archived' ? 'i-heroicons-arrow-uturn-up' : 'i-heroicons-archive-box'" class="h-4 w-4" />
                </UButton>
                <UButton
                  size="sm"
                  color="red"
                  variant="outline"
                  @click="deleteDocument(document.id)"
                >
                  <UIcon name="i-heroicons-trash" class="h-4 w-4" />
                </UButton>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Модальное окно загрузки документа -->
    <UModal v-model="showUploadModal">
      <UCard>
        <template #header>
          <h3 class="text-lg font-semibold">Загрузить документ</h3>
        </template>

        <div class="space-y-4">
          <UFormField label="Название документа *">
            <UInput v-model="newDocument.name" placeholder="Введите название документа" />
          </UFormField>

          <UFormField label="Категория *">
            <USelect
              v-model="newDocument.category"
              :options="[
                { label: 'Договоры', value: 'contracts' },
                { label: 'Финансы', value: 'finance' },
                { label: 'Документы', value: 'documents' },
                { label: 'Отчеты', value: 'reports' }
              ]"
              placeholder="Выберите категорию"
            />
          </UFormField>

          <UFormField label="Файл *">
            <input
              type="file"
              @change="newDocument.file = ($event.target as HTMLInputElement).files?.[0] || null"
              accept=".pdf,.doc,.docx,.xls,.xlsx,.txt"
              class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
            <p class="mt-1 text-xs text-gray-500">
              Поддерживаемые форматы: PDF, DOC, DOCX, XLS, XLSX, TXT
            </p>
          </UFormField>
        </div>

        <template #footer>
          <div class="flex justify-end space-x-2">
            <UButton variant="outline" @click="showUploadModal = false">
              Отмена
            </UButton>
            <UButton @click="uploadDocument" :disabled="!newDocument.name || !newDocument.category || !newDocument.file" :loading="loading">
              Загрузить
            </UButton>
          </div>
        </template>
      </UCard>
    </UModal>
  </div>
</template>
