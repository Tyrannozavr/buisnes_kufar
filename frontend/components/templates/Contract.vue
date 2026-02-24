<template>
	<div class="font-serif text-base text-justify w-full max-w-[210mm]">
		<!-- ТЗ: Договор услуг/работ — закладка «Договор» (услуги), маска 00000, номер и дата в названии. -->
		<p v-if="loading" class="text-gray-500">Загрузка…</p>
		<template v-else>
			<p class="text-sm text-gray-500 mb-2">Договор оказания услуг/работ (ТЗ: для закладки «Услуги»). Сергей: доработать бланк по ТЗ.</p>
			<div class="border border-gray-300 p-4 min-h-[200px] rounded">
				<p class="font-bold mb-2">Договор № {{ (payload as any).number ?? '—' }} от {{ (payload as any).date ?? '—' }}</p>
				<pre class="whitespace-pre-wrap text-sm">{{ JSON.stringify(payload, null, 2) }}</pre>
			</div>
			<p v-if="error" class="text-red-500 mt-2">{{ error }}</p>
		</template>
	</div>
</template>

<script setup lang="ts">
import { injectionKeys } from '~/constants/keys'
import { useDocumentForm } from '~/composables/useDocumentForm'

defineOptions({ name: 'Contract' })

const route = useRoute()
const dealId = computed(() => {
	const q = route.query.dealId ?? route.query.deal_id
	return q ? Number(q) : null
})

const { payload, loading, error, save } = useDocumentForm({
	slot: 'contract',
	dealId,
	initialPayload: { number: '', date: '', conditions: '' },
})

const saveTrigger = inject(injectionKeys.editorSaveTriggerKey, ref({ tab: -1, ts: 0 }))
const tabIndex = 5

watch(saveTrigger, (v) => {
	if (v.tab === tabIndex) save()
}, { deep: true })
</script>
