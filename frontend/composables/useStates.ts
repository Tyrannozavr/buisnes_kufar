import { Editor } from "~/constants/keys";
import { useTypedState } from "~/composables/useTypedState";

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
