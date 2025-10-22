import { useSalesStore } from "~/stores/sales";

export default defineNuxtPlugin(() => {
  const salesStore = useSalesStore();
  const { sales } = storeToRefs(salesStore);

  watch(
    () => sales,
    () => {
      salesStore.amountInGoodsList();
      salesStore.amountInServicesList();

      salesStore.amountPriceInGoods();
      salesStore.amountPriceInServices();

      salesStore.amountWordGoods();
      salesStore.amountWordServices();
    },
    { immediate: true, deep: true }
  );
});
