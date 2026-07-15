<script setup lang="ts">
import { Editor } from '~/constants/keys'
import { useDeals } from '~/composables/useDeals'
import { useBillFillState } from '~/composables/useBillFillState'

const toast = useToast()
const route = useRoute()
const activeTab = useTypedState(Editor.ACTIVE_TAB)
const isDisabled = useTypedState(Editor.IS_DISABLED)
const loadDealTrigger = useTypedState(Editor.LOAD_DEAL_TRIGGER, () => ref(0))
const { findDeal } = useDeals()
const { clearBillAwaitingFill } = useBillFillState()

const confirmOpen = ref(false)

const canFill = computed(() => Boolean(route.query.dealId && route.query.role))
const isBuyer = computed(() => route.query.role === 'buyer')

/**
 * ТЗ_15 §7.4: не проверяем заполненность полей компании/бланка.
 * Достаточно сделки и роли продавца — даже при пустых реквизитах.
 */
const isFillDisabled = computed(() => {
	if (!canFill.value || isBuyer.value) return true
	return route.query.role !== 'seller'
})

const fillTooltip = computed(() => {
	if (!isFillDisabled.value) return ''
	if (isBuyer.value) {
		return 'Заполнить данными может только поставщик'
	}
	if (!canFill.value) return 'Сделка не выбрана'
	return 'Доступно только поставщику по выбранной сделке'
})

const openConfirm = () => {
	if (isBuyer.value) return

	if (!canFill.value) {
		toast.add({ title: 'Сделка не выбрана', color: 'warning' })
		return
	}

	// §7.4: не блокируем из‑за пустых реквизитов — подставляем что есть
	const deal = findDeal(Number(route.query.dealId))
	if (!deal) {
		toast.add({ title: 'Сделка не найдена', color: 'warning' })
		return
	}

	confirmOpen.value = true
}

const applyFill = () => {
	confirmOpen.value = false

	if (activeTab.value === '1') {
		clearBillAwaitingFill()
	}

	loadDealTrigger.value++
	// После подстановки данных — режим редактирования, чтобы можно было сохранить
	isDisabled.value = false

	toast.add({
		title: 'Данные подставлены',
		description:
			activeTab.value === '1'
				? 'Счёт заполнен данными текущей сделки'
				: activeTab.value === '2'
					? 'Договор поставки заполнен данными текущей сделки'
					: 'Заказ заполнен данными текущей сделки',
		color: 'success',
	})
}
</script>

<template>
	<div class="w-full">
		<UTooltip :text="fillTooltip" :disabled="!fillTooltip">
			<span
				class="block w-full"
				:class="{ 'cursor-not-allowed': Boolean(fillTooltip) }"
			>
				<UButton
					label="Заполнить данными"
					icon="i-lucide-file-input"
					class="w-full justify-center"
					:disabled="isFillDisabled"
					@click="openConfirm"
				/>
			</span>
		</UTooltip>

		<UModal v-model:open="confirmOpen" title="Данные будут изменены. Продолжить?">
			<template #body>
				<p class="text-sm text-gray-600 mb-4">
					Текущие данные формы будут заменены данными этой сделки (заказ, реквизиты, товары).
					Если счёт уже заполнен теми же данными — на экране ничего не изменится.
					Кнопка нужна после «Создать счёт» (только номер и дата) или чтобы сбросить ручные правки.
				</p>
				<div class="flex gap-2">
					<UButton
						label="Отмена"
						color="neutral"
						variant="subtle"
						class="flex-1 justify-center"
						@click="confirmOpen = false"
					/>
					<UButton
						label="Продолжить"
						color="primary"
						class="flex-1 justify-center"
						@click="applyFill"
					/>
				</div>
			</template>
		</UModal>
	</div>
</template>
