<script setup lang="ts">
import type { OfficialBill } from '~/types/bill';
import type { SelectMenuItem } from '@nuxt/ui';
import { getMyCompanyQuery } from '~/queries/companyOwner';
import type { OfficialsResponse } from '~/types/dealResponse';

defineProps<{
	isDisabled: boolean
}>() 

const route = useRoute()

const emit = defineEmits<{
	(e: 'addPerson', value: OfficialBill): void
}>()

const { data: myCompany } = useQuery(getMyCompanyQuery())

const personsOptions = computed<SelectMenuItem[]>(() => {
return myCompany.value?.officials?.map((person: OfficialsResponse) => ({
	label: `${person.position} - ${person.full_name}`,
	value: {
		id: person.id,
		name: person.full_name,
		position: person.position,
	} satisfies OfficialBill,
})) ?? []
})
</script>

<template>
	<USelect 
	v-if="route.query.role === 'seller'"
	:disabled="isDisabled" 
	:items="personsOptions" 
	class="w-full mt-2" 
	default-value="Выберите сотрудника для подписи" 
	variant="soft" 
	icon="i-heroicons-user-plus"
	@update:modelValue="emit('addPerson', $event)"/>
</template>