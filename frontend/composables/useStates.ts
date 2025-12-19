import type { Insert } from "~/types/contracts";
import { Editor } from "~/constants/keys";

const insertState: Ref<Insert> = useState(Editor.INSERT_STATE, () =>
  ref({
    purchasesStateGood: false,
    purchasesStateService: false,
    salesStateGood: false,
    salesStateService: false,
  })
);

export const useInsertState = () => {
  const statePurchasesGood = (newVal: boolean): void => {
    nextTick(() => (insertState.value.purchasesStateGood = newVal));
  };

  const statePurchasesService = (newVal: boolean): void => {
    nextTick(() => (insertState.value.purchasesStateService = newVal));
  };

  const stateSalesGood = (newVal: boolean): void => {
    nextTick(() => (insertState.value.salesStateGood = newVal));
  };

  const stateSalesService = (newVal: boolean): void => {
    nextTick(() => (insertState.value.salesStateService = newVal));
  };

  return {
    statePurchasesGood,
    statePurchasesService,
    stateSalesGood,
    stateSalesService,
  };
};

const disabldeState: Ref<Boolean> = useState(Editor.IS_DISABLED, () =>
  ref(true)
);

export const useIsDisableState = () => {
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

const clearState: Ref<Boolean> = useState(Editor.CLEAR_STATE, () => ref(false));

export const useClearState = () => {
  const applyClearState = (): void => {
    clearState.value = true;
    nextTick(() => (clearState.value = false));
  };
  return {
    applyClearState,
  };
};

const saveStateOrder: Ref<Boolean> = useState(Editor.SAVE_STATE_ORDER, () =>
  ref(false)
);

export const useSaveState = () => {
  const saveOrder = (): void => {
    saveStateOrder.value = true;
    nextTick(() => (saveStateOrder.value = false));
  };
	
  return {
		saveOrder
	};
};

const removeDealState: Ref<Boolean> = useState(Editor.REMOVE_DEAL, () => ref(false))

export const useRemoveDealState = () => {
	const removeDeal = () => {
		removeDealState.value = !removeDealState.value
		nextTick(() => (removeDealState.value = !removeDealState.value))
	}
	return {
		removeDeal
	}
}
