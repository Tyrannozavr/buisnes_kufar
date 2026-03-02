import { usePurchasesStore } from "~/stores/purchases";

export default defineNuxtPlugin(() => {
  const purchasesStore = usePurchasesStore();
  const { purchases } = storeToRefs(purchasesStore);

  watch(
    () => purchases,
    () => {
      purchasesStore.amountInGoodsList();
      purchasesStore.amountPriceInGoods();
      purchasesStore.amountWordGoods();
    },
    { immediate: true, deep: true }
  );
});
