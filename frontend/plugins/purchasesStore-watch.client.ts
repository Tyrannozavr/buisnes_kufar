import { usePurchasesStore } from "~/stores/purchases";

export default defineNuxtPlugin(() => {
  const purchasesStore = usePurchasesStore();
  const { purchases } = storeToRefs(purchasesStore);

  watch(
    () => purchases,
    () => {
      purchasesStore.amountInGoodsList();
      purchasesStore.amountPriceInGoods();
      purchasesStore.amountWord();
			console.log('данные изменились: ',purchases.value.goodsDeals?.[0])
    },
    { immediate: true, deep: true }
  );
});
