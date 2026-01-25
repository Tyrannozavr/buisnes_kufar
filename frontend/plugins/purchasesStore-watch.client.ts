import { usePurchasesStore } from "~/stores/purchases";

export default defineNuxtPlugin(() => {
  const purchasesStore = usePurchasesStore();
  const { purchases } = storeToRefs(purchasesStore);

  watch(
    () => purchases,
    () => {
      purchasesStore.amountInGoodsList();
      purchasesStore.amountInServicesList();

      purchasesStore.amountPriceInGoods();
      purchasesStore.amountPriceInServices();

      purchasesStore.amountWordGoods();
      purchasesStore.amountWordServices();
    },
    { immediate: true, deep: true }
  );
});
