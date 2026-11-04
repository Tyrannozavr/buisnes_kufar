<script setup lang="ts">
import type { CargoTransportTableRow } from '~/utils/cargoTransportTable'

defineProps<{
	rows: CargoTransportTableRow[]
}>()
</script>

<template>
	<div
		class="my-4 rounded border border-neutral-300 bg-neutral-100 p-3 text-sm"
		aria-label="Таблица условий перевозки"
	>
		<p class="mb-2 text-center font-bold tracking-wide">ТАБЛИЦА УСЛОВИЙ ПЕРЕВОЗКИ</p>
		<p class="mb-2 text-xs text-neutral-500 text-center">
			Условия из перевозки по заказу. Чтобы изменить — кнопка «Редактировать данные перевозки» справа.
		</p>
		<table class="w-full border-collapse">
			<tbody>
				<tr
					v-for="row in rows"
					:key="row.label"
					class="border-b border-neutral-300/80 align-top"
				>
					<td class="py-1 pr-3 w-[42%] text-neutral-700">{{ row.label }}</td>
					<td class="py-1 font-medium text-neutral-900">
						{{ row.value || '—' }}
					</td>
				</tr>
			</tbody>
		</table>
	</div>
</template>
