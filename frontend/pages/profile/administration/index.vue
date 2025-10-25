<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useEmployeeApi } from '~/api/employee'
import type { EmployeeResponse } from '~/types/employee'

const employeeApi = useEmployeeApi()

// Состояние
const employees = ref<EmployeeResponse[]>([])
const loading = ref(false)
const error = ref<string | undefined>(undefined)
const showAddEmployeeModal = ref(false)
const selectedEmployee = ref<EmployeeResponse | null>(null)
const showDeleteModal = ref(false)
const showAdminDeletionModal = ref(false)

// Данные для форм
const positions = ref<Array<{value: string, label: string}>>([])
const roles = ref<Array<{value: string, label: string, description: string}>>([])

// Форма добавления сотрудника
const newEmployee = ref({
  email: '',
  first_name: '',
  last_name: '',
  patronymic: '',
  phone: '',
  position: '',
  role: 'user' as 'owner' | 'admin' | 'user',
  permissions: {} as Record<string, boolean>
})


// Фильтры
const roleFilter = ref<'all' | 'owner' | 'admin' | 'user'>('all')
const statusFilter = ref<'all' | 'pending' | 'active' | 'inactive' | 'deleted'>('all')

// Вычисляемые свойства
const filteredEmployees = computed(() => {
  let filtered = employees.value

  if (roleFilter.value !== 'all') {
    filtered = filtered.filter(emp => emp.role === roleFilter.value)
  }

  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(emp => emp.status === statusFilter.value)
  }

  return filtered
})

const adminsCount = computed(() => {
  return employees.value.filter(emp => emp.role === 'admin' && emp.status === 'active').length
})

// Методы для управления модальными окнами
const closeAllModals = () => {
  showAddEmployeeModal.value = false
  showDeleteModal.value = false
  showAdminDeletionModal.value = false
}

const openAddEmployeeModal = () => {
  closeAllModals()
  showAddEmployeeModal.value = true
}

const openDeleteModal = (employee: EmployeeResponse) => {
  closeAllModals()
  selectedEmployee.value = employee
  showDeleteModal.value = true
}

const openAdminDeletionModal = (employee: EmployeeResponse) => {
  closeAllModals()
  selectedEmployee.value = employee
  showAdminDeletionModal.value = true
}

// Методы
const loadEmployees = async () => {
  loading.value = true
  error.value = undefined
  try {
    const response = await employeeApi.getEmployees()
    employees.value = response.employees
  } catch (e: any) {
    error.value = e.message || 'Ошибка загрузки сотрудников'
    useToast().add({
      title: 'Ошибка',
      description: error.value,
      color: 'error'
    })
  } finally {
    loading.value = false
  }
}

const addEmployee = async () => {
  try {
    await employeeApi.createEmployee(newEmployee.value)
    useToast().add({
      title: 'Успешно',
      description: 'Сотрудник добавлен',
      color: 'success'
    })
    showAddEmployeeModal.value = false
    resetNewEmployeeForm()
    await loadEmployees()
  } catch (e: any) {
    useToast().add({
      title: 'Ошибка',
      description: e.message || 'Не удалось добавить сотрудника',
      color: 'error'
    })
  }
}

const deleteEmployee = async () => {
  if (!selectedEmployee.value) return

  try {
    await employeeApi.deleteEmployee(selectedEmployee.value.id)
    useToast().add({
      title: 'Успешно',
      description: 'Сотрудник удален',
      color: 'success'
    })
    showDeleteModal.value = false
    await loadEmployees()
  } catch (e: any) {
    useToast().add({
      title: 'Ошибка',
      description: e.message || 'Не удалось удалить сотрудника',
      color: 'error'
    })
  }
}

const requestAdminDeletion = async () => {
  if (!selectedEmployee.value) return

  try {
    await employeeApi.requestAdminDeletion(selectedEmployee.value.id, { reason: '' })
    useToast().add({
      title: 'Успешно',
      description: 'Запрос на удаление администратора отправлен. Удаление произойдет через 48 часов, если не будет отклонено.',
      color: 'success'
    })
    showAdminDeletionModal.value = false
    await loadEmployees()
  } catch (e: any) {
    useToast().add({
      title: 'Ошибка',
      description: e.message || 'Не удалось отправить запрос на удаление',
      color: 'error'
    })
  }
}

const rejectAdminDeletion = async (employee: EmployeeResponse) => {
  try {
    await employeeApi.rejectAdminDeletion(employee.id)
    useToast().add({
      title: 'Успешно',
      description: 'Удаление администратора отклонено',
      color: 'success'
    })
    await loadEmployees()
  } catch (e: any) {
    useToast().add({
      title: 'Ошибка',
      description: e.message || 'Не удалось отклонить удаление',
      color: 'error'
    })
  }
}

const resetNewEmployeeForm = () => {
  newEmployee.value = {
    email: '',
    first_name: '',
    last_name: '',
    patronymic: '',
    phone: '',
    position: '',
    role: 'user',
    permissions: {}
  }
}

const getRoleLabel = (role: string) => {
  const labels = {
    owner: 'Владелец',
    admin: 'Администратор',
    user: 'Пользователь'
  }
  return labels[role as keyof typeof labels] || role
}

const getStatusLabel = (status: string) => {
  const labels = {
    pending: 'Ожидает регистрации',
    active: 'Активный',
    inactive: 'Неактивный',
    deleted: 'Удален'
  }
  return labels[status as keyof typeof labels] || status
}

const getStatusColor = (status: string) => {
  const colors = {
    pending: 'warning',
    active: 'success',
    inactive: 'neutral',
    deleted: 'error'
  }
  return colors[status as keyof typeof colors] || 'neutral'
}

// Функции загрузки данных
const loadPositions = async () => {
  try {
    const response = await employeeApi.getPositions()
    positions.value = response.positions
  } catch (err) {
    console.error('Ошибка загрузки должностей:', err)
  }
}

const loadRoles = async () => {
  try {
    const response = await employeeApi.getRoles()
    roles.value = response.roles
  } catch (err) {
    console.error('Ошибка загрузки ролей:', err)
  }
}

// Жизненный цикл
onMounted(async () => {
  await Promise.all([
    loadEmployees(),
    loadPositions(),
    loadRoles()
  ])
})

definePageMeta({
  layout: 'profile'
})
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-2xl font-bold text-gray-900">Администрирование</h1>
      <UButton @click="openAddEmployeeModal" color="primary">
        <UIcon name="i-heroicons-plus" class="mr-2" />
        Добавить сотрудника
      </UButton>
    </div>

    <!-- Фильтры -->
    <div class="mb-6 flex gap-4">
      <USelect
        v-model="roleFilter"
        :options="[
          { label: 'Все роли', value: 'all' },
          { label: 'Владелец', value: 'owner' },
          { label: 'Администратор', value: 'admin' },
          { label: 'Пользователь', value: 'user' }
        ]"
        placeholder="Фильтр по роли"
        class="w-48"
      />
      <USelect
        v-model="statusFilter"
        :options="[
          { label: 'Все статусы', value: 'all' },
          { label: 'Ожидает регистрации', value: 'pending' },
          { label: 'Активный', value: 'active' },
          { label: 'Неактивный', value: 'inactive' },
          { label: 'Удален', value: 'deleted' }
        ]"
        placeholder="Фильтр по статусу"
        class="w-48"
      />
    </div>

    <!-- Список сотрудников -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500"></div>
    </div>

    <div v-else-if="error" class="mb-4 p-4 bg-red-50 text-red-700 rounded-md">
      {{ error }}
    </div>

    <div v-else class="bg-white shadow rounded-lg overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">
          Сотрудники компании ({{ filteredEmployees.length }})
        </h3>
        <p v-if="adminsCount > 0" class="text-sm text-gray-500 mt-1">
          Администраторов: {{ adminsCount }}
        </p>
      </div>

      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Сотрудник
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Email
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Роль
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
            <tr v-for="employee in filteredEmployees" :key="employee.id">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 h-10 w-10">
                    <div class="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                      <span class="text-sm font-medium text-gray-700">
                        {{ employee.first_name?.[0] || employee.email?.[0]?.toUpperCase() || '?' }}
                      </span>
                    </div>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">
                      {{ employee.first_name }} {{ employee.last_name }}
                    </div>
                    <div class="text-sm text-gray-500">
                      {{ employee.position }}
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ employee.email }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <UBadge :color="employee.role === 'owner' ? 'primary' : employee.role === 'admin' ? 'primary' : 'neutral'">
                  {{ getRoleLabel(employee.role) }}
                </UBadge>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <UBadge :color="getStatusColor(employee.status) as any">
                  {{ getStatusLabel(employee.status) }}
                </UBadge>
                <div v-if="employee.deletion_requested_at" class="text-xs text-red-600 mt-1">
                  Удаление запрошено
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                <!-- Кнопки для обычных пользователей -->
                <template v-if="employee.role === 'user'">
                  <UButton
                    size="sm"
                    variant="outline"
                    @click="$router.push(`/profile/administration/edit-permissions/${employee.id}`)"
                  >
                    Права
                  </UButton>
                  <UButton
                    size="sm"
                    color="error"
                    variant="outline"
                    @click="openDeleteModal(employee)"
                  >
                    Удалить
                  </UButton>
                </template>

                <!-- Кнопки для администраторов -->
                <template v-else-if="employee.role === 'admin'">
                  <UButton
                    v-if="employee.deletion_requested_at && !employee.deletion_rejected_at"
                    size="sm"
                    color="success"
                    variant="outline"
                    @click="rejectAdminDeletion(employee)"
                  >
                    Отклонить удаление
                  </UButton>
                  <UButton
                    v-else-if="!employee.deletion_requested_at"
                    size="sm"
                    color="error"
                    variant="outline"
                    @click="openAdminDeletionModal(employee)"
                  >
                    Удалить
                  </UButton>
                </template>

                <!-- Владелец не может быть удален -->
                <template v-else>
                  <span class="text-gray-400 text-sm">Недоступно</span>
                </template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Модальное окно добавления сотрудника -->
    <UModal v-if="showAddEmployeeModal" v-model="showAddEmployeeModal">
      <UCard @click.stop>
        <template #header>
          <h3 class="text-lg font-semibold" id="add-employee-title">Добавить сотрудника</h3>
        </template>

        <div class="space-y-4" aria-describedby="add-employee-description" @click.stop>
          <UFormField label="Email *">
            <UInput v-model="newEmployee.email" type="email" placeholder="email@example.com" />
          </UFormField>

          <div class="grid grid-cols-2 gap-4">
            <UFormField label="Имя">
              <UInput v-model="newEmployee.first_name" placeholder="Имя" />
            </UFormField>
            <UFormField label="Фамилия">
              <UInput v-model="newEmployee.last_name" placeholder="Фамилия" />
            </UFormField>
          </div>

          <UFormField label="Отчество">
            <UInput v-model="newEmployee.patronymic" placeholder="Отчество" />
          </UFormField>

          <UFormField label="Телефон">
            <UInput v-model="newEmployee.phone" placeholder="+7 (999) 123-45-67" />
          </UFormField>
          <UFormField label="Должность">
            <USelect
              v-model="newEmployee.position"
              :items="positions"
              placeholder="Выберите должность"
            />
          </UFormField>

          <UFormField label="Роль">
            <USelect
              v-model="newEmployee.role"
              :items="roles.filter(r => r.value !== 'owner')"
              placeholder="Выберите роль"
            />
          </UFormField>
        </div>

        <template #footer>
          <div class="flex justify-end space-x-2" @click.stop>
            <UButton variant="outline" @click="closeAllModals">
              Отмена
            </UButton>
            <UButton @click="addEmployee" :disabled="!newEmployee.email">
              Добавить
            </UButton>
          </div>
        </template>
      </UCard>
    </UModal>

    <!-- Модальное окно удаления сотрудника -->
    <UModal v-if="showDeleteModal" v-model="showDeleteModal">
      <UCard>
        <template #header>
          <h3 class="text-lg font-semibold text-red-600" id="delete-employee-title">Удалить сотрудника</h3>
        </template>

        <p class="text-gray-700" id="delete-employee-description">
          Вы уверены, что хотите удалить сотрудника 
          <strong>{{ selectedEmployee?.first_name }} {{ selectedEmployee?.last_name }}</strong>?
          Это действие нельзя отменить.
        </p>

        <template #footer>
          <div class="flex justify-end space-x-2" @click.stop>
            <UButton variant="outline" @click="closeAllModals">
              Отмена
            </UButton>
            <UButton color="error" @click="deleteEmployee">
              Удалить
            </UButton>
          </div>
        </template>
      </UCard>
    </UModal>

    <!-- Модальное окно удаления администратора -->
    <UModal v-if="showAdminDeletionModal" v-model="showAdminDeletionModal">
      <UCard>
        <template #header>
          <h3 class="text-lg font-semibold text-red-600" id="delete-admin-title">Удалить администратора</h3>
        </template>

        <div class="space-y-4" aria-describedby="delete-admin-description">
          <p class="text-gray-700" id="delete-admin-description">
            Вы уверены, что хотите удалить администратора 
            <strong>{{ selectedEmployee?.first_name }} {{ selectedEmployee?.last_name }}</strong>?
          </p>
          
          <div class="bg-yellow-50 border border-yellow-200 rounded-md p-4">
            <div class="flex">
              <UIcon name="i-heroicons-exclamation-triangle" class="h-5 w-5 text-yellow-400" />
              <div class="ml-3">
                <h3 class="text-sm font-medium text-yellow-800">Важно!</h3>
                <div class="mt-2 text-sm text-yellow-700">
                  <ul class="list-disc list-inside space-y-1">
                    <li>Удаление произойдет через 48 часов</li>
                    <li>Администратор может отклонить удаление</li>
                    <li>Если это единственный администратор, удаление невозможно</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>

        <template #footer>
          <div class="flex justify-end space-x-2" @click.stop>
            <UButton variant="outline" @click="closeAllModals">
              Отмена
            </UButton>
            <UButton color="error" @click="requestAdminDeletion">
              Запросить удаление
            </UButton>
          </div>
        </template>
      </UCard>
    </UModal>
  </div>
</template>
