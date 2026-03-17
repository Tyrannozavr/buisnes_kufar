//From constant/keys
interface StateMap {
  //Editor
  saveState: boolean;
  isDisabled: boolean;
  clearState: boolean;
  removeDealState: boolean;
  activeTab: "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7";
  reasonCheck: boolean;
  dueDateCheck: boolean;
  dueDate: string;
  additionalInfo: boolean;
  vatRateCheck: boolean;
  //TemplateElement
  htmlOrder: HTMLElement | null;
  htmlBill: HTMLElement | null;
  htmlSupplyContract: HTMLElement | null;
  htmlDogovorUslug: HTMLElement | null;
}

export function useTypedState<T extends keyof StateMap>(
	key: T, 
	defaultValue?: () => Ref<StateMap[T]>
) {
	return useState<StateMap[T]>(key, defaultValue)
}