import type { PiniaColadaOptions } from '@pinia/colada'

export default {
	queryOptions: {
		staleTime: 1000 * 60 * 5,
		gcTime: 1000 * 60 * 30,
	},
} satisfies PiniaColadaOptions

