import { useDealsStore } from "~/stores/deals"

export default defineNuxtPlugin(() => {
	const dealsStore = useDealsStore()
	const { deals } = storeToRefs(dealsStore)

	watch(
		() => deals,
		() => {
			dealsStore.amountPriceInProduct()
			dealsStore.amountPriceInProductItem()
			dealsStore.amountWordProduct()
		},
		{ immediate: true, deep: true }
	)
})
