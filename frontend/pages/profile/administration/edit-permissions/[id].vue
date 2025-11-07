<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useEmployeeApi } from '~/api/employee'
import type { EmployeeResponse } from '~/types/employee'

const route = useRoute()
const router = useRouter()
const employeeApi = useEmployeeApi()

// Состояние
const employee = ref<EmployeeResponse | null>(null)
const permissions = ref<Record<string, boolean>>({})
const availablePermissions = ref<Record<string, string>>({})
const loading = ref(false)
const saving = ref(false)

// Получаем ID сотрудника из URL
const employeeId = computed(() => parseInt(route.params.id as string))

// Загружаем данные сотрудника
const loadEmployee = async () => {
  loading.value = true
  try {
    const employees = await employeeApi.getEmployees()
    const foundEmployee = employees.employees.find(emp => emp.id === employeeId.value)
    
    if (!foundEmployee) {
      throw new Error('Сотрудник не найден')
    }
    
    employee.value = foundEmployee
    permissions.value = { ...foundEmployee.permissions }
  } catch (e: any) {
    useToast().add({
      title: 'Ошибка',
      description: e.message || 'Не удалось загрузить данные сотрудника',
      color: 'error'
    })
    router.push('/profile/administration')
  } finally {
    loading.value = false
  }
}

// Загружаем доступные права
const loadAvailablePermissions = async () => {
  try {
    const response = await employeeApi.getAvailablePermissions()
    availablePermissions.value = response.permissions
  } catch (e: any) {
    console.error('Failed to load permissions:', e)
  }
}

// Сохраняем права
const savePermissions = async () => {
  saving.value = true
  try {
    console.log('Saving permissions for employee:', employeeId.value)
    console.log('Permissions data:', permissions.value)
    
    await employeeApi.updateEmployeePermissions(employeeId.value, { permissions: permissions.value })
    useToast().add({
      title: 'Успешно',
      description: 'Права доступа обновлены',
      color: 'success'
    })
    router.push('/profile/administration')
  } catch (e: any) {
    console.error('Error saving permissions:', e)
    useToast().add({
      title: 'Ошибка',
      description: e.message || 'Не удалось сохранить права',
      color: 'error'
    })
  } finally {
    saving.value = false
  }
}

// Отмена
const cancel = () => {
  router.push('/profile/administration')
}

// Загружаем данные при монтировании
onMounted(async () => {
  await Promise.all([
    loadEmployee(),
    loadAvailablePermissions()
  ])
})

definePageMeta({
  layout: 'profile'
})
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Заголовок -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Редактирование прав доступа</h1>
          <p class="text-gray-600 mt-2">
            {{ employee?.first_name }} {{ employee?.last_name }} ({{ employee?.email }})
          </p>
        </div>
        <div class="flex space-x-2">
          <UButton variant="outline" @click="cancel">
            Отмена
          </UButton>
          <UButton @click="savePermissions" :disabled="saving" :loading="saving">
            Сохранить
          </UButton>
        </div>
      </div>
    </div>

    <!-- Загрузка -->
    <div v-if="loading" class="text-center py-8">
      <div class="text-gray-500">Загрузка данных...</div>
    </div>

    <!-- Форма прав доступа -->
    <div v-else-if="employee" class="bg-white shadow rounded-lg">
      <div class="px-6 py-4 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">Права доступа</h3>
        <p class="text-sm text-gray-600 mt-1">
          Выберите права доступа для сотрудника
        </p>
      </div>
      
      <div class="p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div v-for="(label, key) in availablePermissions" :key="key" class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
            <div>
              <label class="text-sm font-medium text-gray-900">{{ label }}</label>
              <p class="text-xs text-gray-500 mt-1">{{ key }}</p>
            </div>
            <input 
              type="checkbox" 
              v-model="permissions[key]" 
              class="h-5 w-5 text-emerald-600 focus:ring-emerald-500 border-gray-300 rounded"
            />
          </div>
        </div>
        
        <!-- Информация о выбранных правах -->
        <div class="mt-6 p-4 bg-gray-50 rounded-lg">
          <h4 class="text-sm font-medium text-gray-900 mb-2">Выбранные права:</h4>
          <div class="text-sm text-gray-600">
            <span v-if="Object.values(permissions).every(p => !p)" class="text-gray-400">
              Права не выбраны
            </span>
            <span v-else>
              {{ Object.entries(permissions)
                .filter(([_, value]) => value)
                .map(([key, _]) => availablePermissions[key])
                .join(', ') }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Ошибка -->
    <div v-else class="text-center py-8">
      <div class="text-red-600">Сотрудник не найден</div>
    </div>
  </div>
</template>
