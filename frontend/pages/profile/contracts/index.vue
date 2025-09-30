<script setup lang="ts">
definePageMeta({
  layout: 'profile'
})
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <div class="bg-white shadow rounded-lg p-5">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Договоры</h2>
      <p class="text-gray-500">Раздел находится в разработке</p>
			<UButton 
				to="/profile/contracts/editor"
				label="Редактор документов"
				variant="subtle"
				color="neutral"
				class="m-5"
			/>
    </div>
  </div>
</template> 