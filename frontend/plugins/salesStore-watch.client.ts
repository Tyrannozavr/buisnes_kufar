import { useSalesStore } from "~/stores/sales";

export default defineNuxtPlugin(() => {
  const salesStore = useSalesStore();
  const { sales } = storeToRefs(salesStore);

  watch(
    () => sales,
    () => {
      salesStore.amountInGoodsList();
      salesStore.amountPriceInGoods();
      salesStore.amountWordGoods();
    },
    { immediate: true, deep: true }
  );
});
