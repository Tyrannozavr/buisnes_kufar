<script setup lang="ts">
import type { SelectMenuItem } from '@nuxt/ui';
import { getMyCompanyQuery } from '~/queries/companyOwner';
import type { OfficialsResponse } from '~/types/dealResponse';
import type { Official } from '~/types/dealState';

const OWNER_POSITION = 'owner'
const OWNER_POSITION_LABEL = 'Владелец'

const { isDisabled, isBase } = defineProps<{
	isDisabled: boolean
	isBase?: boolean //если это пропс есть, то предлагаются только люди, у которых isBase = true
}>() 

const route = useRoute()

const emit = defineEmits<{
	(e: 'addPerson', value: Official): void
}>()

const { data: myCompany } = useQuery(getMyCompanyQuery())

const isOwnerOfficial = (person: OfficialsResponse) => person.position === OWNER_POSITION

const formatOfficialPosition = (position: string) =>
	position === OWNER_POSITION ? OWNER_POSITION_LABEL : position

const mapOfficialToOption = (person: OfficialsResponse): SelectMenuItem => {
	const position = formatOfficialPosition(person.position)

	return {
		label: `${position} - ${person.full_name}`,
		value: {
			id: person.id,
			companyId: person.company_id,
			name: person.full_name,
			position,
			isBase: person.is_base,
			baseDocument: person.base_document ?? '',
			baseDocumentName: person.base_document_name ?? '',
		} satisfies Official,
	}
}

const personsOptions = computed<SelectMenuItem[]>(() => {
	const officials = myCompany.value?.officials ?? []
	const filteredOfficials = isBase
		? officials.filter((person) => person.is_base || isOwnerOfficial(person))
		: officials

	return filteredOfficials.map(mapOfficialToOption)
})
</script>

<template>
	<USelect 
	v-if="route.query.role === 'seller'"
	:disabled="isDisabled" 
	:items="personsOptions" 
	class="w-full" 
	default-value="Выберите сотрудника для подписи" 
	variant="soft" 
	icon="i-heroicons-user-plus"
	@update:modelValue="emit('addPerson', $event)"
/>
</template>