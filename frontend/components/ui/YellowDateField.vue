<script setup lang="ts">
import { CalendarDate, parseDate } from '@internationalized/date'
import { YELLOW_INPUT_CLASS } from '~/utils/carriageParty'

/**
 * Жёлтое поле даты: ручной ввод ДД.ММ.ГГГГ + кнопка календаря (ru).
 * v-model: ISO `YYYY-MM-DD`.
 */
const model = defineModel<string>({ default: '' })

const props = withDefaults(
	defineProps<{
		disabled?: boolean
		ariaLabel?: string
		showYearSuffix?: boolean
	}>(),
	{
		disabled: false,
		ariaLabel: 'Дата',
		showYearSuffix: true,
	},
)

const open = ref(false)
const text = ref('')
const calendarValue = ref<CalendarDate | undefined>()
const syncingFromModel = ref(false)

const isoOrEmpty = computed(() => {
	const iso = String(model.value || '').slice(0, 10)
	return /^\d{4}-\d{2}-\d{2}$/.test(iso) ? iso : ''
})

const isoToRu = (iso: string): string => {
	if (!/^\d{4}-\d{2}-\d{2}$/.test(iso)) return ''
	const [y, m, d] = iso.split('-')
	return `${d}.${m}.${y}`
}

const parseRuToIso = (raw: string): string | null => {
	const s = String(raw || '').trim()
	if (!s) return ''
	const m = s.match(/^(\d{1,2})[./](\d{1,2})[./](\d{4})$/)
	if (!m) return null
	const d = Number(m[1])
	const mo = Number(m[2])
	const y = Number(m[3])
	if (mo < 1 || mo > 12 || d < 1 || d > 31) return null
	const iso = `${y}-${String(mo).padStart(2, '0')}-${String(d).padStart(2, '0')}`
	try {
		parseDate(iso)
		return iso
	} catch {
		return null
	}
}

const applyIso = (iso: string) => {
	syncingFromModel.value = true
	model.value = iso
	text.value = iso ? isoToRu(iso) : ''
	try {
		calendarValue.value = iso ? parseDate(iso) : undefined
	} catch {
		calendarValue.value = undefined
	}
	nextTick(() => {
		syncingFromModel.value = false
	})
}

watch(
	isoOrEmpty,
	(iso) => {
		if (syncingFromModel.value) return
		text.value = iso ? isoToRu(iso) : text.value && !parseRuToIso(text.value) ? text.value : isoToRu(iso)
		if (iso) {
			try {
				calendarValue.value = parseDate(iso)
			} catch {
				calendarValue.value = undefined
			}
		} else if (!text.value.trim()) {
			calendarValue.value = undefined
		}
	},
	{ immediate: true },
)

const commitText = () => {
	const raw = text.value.trim()
	if (!raw) {
		applyIso('')
		return
	}
	const iso = parseRuToIso(raw)
	if (iso === null) {
		// невалидно — вернуть отображение из model
		text.value = isoOrEmpty.value ? isoToRu(isoOrEmpty.value) : ''
		return
	}
	applyIso(iso)
}

const onCalendarSelect = (v: CalendarDate | null | undefined) => {
	if (!v || syncingFromModel.value) return
	const iso = `${v.year}-${String(v.month).padStart(2, '0')}-${String(v.day).padStart(2, '0')}`
	applyIso(iso)
	open.value = false
}

const onOpenChange = (next: boolean) => {
	if (props.disabled) {
		open.value = false
		return
	}
	open.value = next
}
</script>

<template>
	<span class="inline-flex items-center gap-1 align-middle">
		<input
			v-model="text"
			type="text"
			inputmode="numeric"
			placeholder="ДД.ММ.ГГГГ"
			:disabled="props.disabled"
			:class="YELLOW_INPUT_CLASS"
			class="w-[7.5rem]"
			:aria-label="props.ariaLabel"
			@keydown.enter.prevent="commitText"
			@blur="commitText"
		/>
		<span v-if="props.showYearSuffix" class="text-sm">г.</span>
		<ClientOnly>
			<UPopover :open="open" @update:open="onOpenChange">
				<UButton
					type="button"
					icon="i-lucide-calendar"
					size="xs"
					color="neutral"
					variant="soft"
					class="bg-yellow-100 hover:bg-yellow-200 ring-1 ring-yellow-300"
					:disabled="props.disabled"
					:aria-label="`${props.ariaLabel}: открыть календарь`"
				/>
				<template #content>
					<UCalendar
						:model-value="calendarValue"
						:week-starts-on="1"
						class="p-2"
						@update:model-value="onCalendarSelect"
					/>
				</template>
			</UPopover>
			<template #fallback>
				<UButton
					type="button"
					icon="i-lucide-calendar"
					size="xs"
					color="neutral"
					variant="soft"
					disabled
					class="bg-yellow-100 ring-1 ring-yellow-300"
				/>
			</template>
		</ClientOnly>
	</span>
</template>
