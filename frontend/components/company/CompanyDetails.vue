<script setup lang="ts">
import type { CompanyDetails } from '~/types/company'

defineProps<CompanyDetails>()
</script>

<template>
  <div class="mt-6">
    <UCard>
      <template #header>
        <h2 class="text-xl font-semibold">О компании</h2>
      </template>
      
      <p class="text-gray-600 mb-6">{{ description }}</p>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Реквизиты -->
        <div class="space-y-4">
          <h3 class="text-lg font-medium">Реквизиты компании</h3>
          
          <div class="space-y-2">
            <div class="flex justify-between">
              <span class="text-gray-500">ИНН</span>
              <span class="font-medium">{{ inn }}</span>
            </div>
            
            <div class="flex justify-between">
              <span class="text-gray-500">ОГРН</span>
              <span class="font-medium">{{ ogrn }}</span>
            </div>
            
            <div class="flex justify-between">
              <span class="text-gray-500">Дата регистрации ОГРН</span>
              <span class="font-medium">{{ ogrnDate }}</span>
            </div>
            
            <div class="flex justify-between">
              <span class="text-gray-500">КПП</span>
              <span class="font-medium">{{ kpp }}</span>
            </div>
          </div>
        </div>
        
        <!-- Контакты -->
        <div class="space-y-4">
          <h3 class="text-lg font-medium">Контактные данные</h3>
          
          <div class="space-y-2">
            <div class="flex justify-between">
              <span class="text-gray-500">Юридический адрес</span>
              <span class="font-medium">{{ legalAddress }}</span>
            </div>
            
            <div class="flex justify-between">
              <span class="text-gray-500">Адрес производства</span>
              <span class="font-medium">{{ productionAddress }}</span>
            </div>
            
            <div class="flex justify-between">
              <span class="text-gray-500">Телефон</span>
              <span class="font-medium">{{ phone }}</span>
            </div>
            
            <div class="flex justify-between">
              <span class="text-gray-500">Email</span>
              <span class="font-medium">{{ email }}</span>
            </div>
            
            <div class="flex justify-between">
              <span class="text-gray-500">Сайт</span>
              <a 
                :href="website" 
                target="_blank" 
                class="font-medium text-primary hover:underline"
              >
                {{ website }}
              </a>
            </div>
          </div>
        </div>
      </div>
    </UCard>
  </div>
</template> 