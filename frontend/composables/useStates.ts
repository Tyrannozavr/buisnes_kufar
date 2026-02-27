import { Editor } from "~/constants/keys";
import { useTypedState } from "~/composables/useTypedState";

export const useInsertState = () => {
  const insertState = useState(Editor.INSERT_STATE, () =>
    ref({
      purchasesGood: false,
      salesGood: false,
    })
  );

  const statePurchasesGood = (newVal: boolean): void => {
    nextTick(() => (insertState.value.purchasesGood = newVal));
  };

  const stateSalesGood = (newVal: boolean): void => {
    nextTick(() => (insertState.value.salesGood = newVal));
  };

  return {
    statePurchasesGood,
    stateSalesGood,
  };
};

//манипуляции с состоянием кнопки вставки данных
export const useIsDisableState = () => {
  const disabldeState = useTypedState(Editor.IS_DISABLED, () => ref(true));

  const reversDisable = (): void => {
    disabldeState.value = !disabldeState.value;
  };

  const doubleReversDisable = (): void => {
    reversDisable();
    nextTick(() => reversDisable());
  };

  return {
    reversDisable,
    doubleReversDisable,
  };
};

export const useClearState = () => {
  const clearState = useTypedState(Editor.CLEAR_STATE, () => ref(false));

  const applyClearState = (): void => {
    clearState.value = true;
    nextTick(() => (clearState.value = false));
  };
  return {
    applyClearState,
  };
};


export const useSaveState = () => {
  const saveStateOrder = useTypedState(Editor.SAVE_STATE_ORDER, () => ref(false));

  const saveOrder = (): void => {
    saveStateOrder.value = true;
    nextTick(() => (saveStateOrder.value = false));
  };

  return {
    saveOrder,
  };
};

export const useRemoveDealState = () => {
  const removeDealState = useTypedState(Editor.REMOVE_DEAL, () => ref(false));

  const removeDeal = () => {
    removeDealState.value = !removeDealState.value;
    nextTick(() => (removeDealState.value = !removeDealState.value));
  };
  return {
    removeDeal,
  };
};
