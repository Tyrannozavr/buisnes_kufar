import { Editor } from "~/constants/keys";

const insertState = useState(Editor.INSERT_STATE, () =>
  ref({
    purchasesGood: false,
    purchasesService: false,
    salesGood: false,
    salesService: false,
  })
);

export const useInsertState = () => {
  const statePurchasesGood = (newVal: boolean): void => {
    nextTick(() => (insertState.value.purchasesGood = newVal));
  };

  const statePurchasesService = (newVal: boolean): void => {
    nextTick(() => (insertState.value.purchasesService = newVal));
  };

  const stateSalesGood = (newVal: boolean): void => {
    nextTick(() => (insertState.value.salesGood = newVal));
  };

  const stateSalesService = (newVal: boolean): void => {
    nextTick(() => (insertState.value.salesService = newVal));
  };

  return {
    statePurchasesGood,
    statePurchasesService,
    stateSalesGood,
    stateSalesService,
  };
};

const disabldeState = useTypedState(Editor.IS_DISABLED, () =>
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

const clearState = useTypedState(Editor.CLEAR_STATE, () => ref(false));

export const useClearState = () => {
  const applyClearState = (): void => {
    clearState.value = true;
    nextTick(() => (clearState.value = false));
  };
  return {
    applyClearState,
  };
};

const saveStateOrder = useTypedState(Editor.SAVE_STATE_ORDER, () =>
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

const removeDealState = useTypedState(Editor.REMOVE_DEAL, () => ref(false))

export const useRemoveDealState = () => {
	const removeDeal = () => {
		removeDealState.value = !removeDealState.value
		nextTick(() => (removeDealState.value = !removeDealState.value))
	}
	return {
		removeDeal
	}
}
