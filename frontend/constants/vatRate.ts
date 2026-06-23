import type { SelectMenuItem } from '@nuxt/ui'

/** Ставки НДС по ТЗ §2: 5, 7, 10, 18, 20, 25, Без НДС */
export const VAT_RATE_OPTIONS: SelectMenuItem[] = [
	{ label: 'Без НДС', value: 0 },
	{ label: '5%', value: 5 },
	{ label: '7%', value: 7 },
	{ label: '10%', value: 10 },
	{ label: '18%', value: 18 },
	{ label: '20%', value: 20 },
	{ label: '25%', value: 25 },
]
