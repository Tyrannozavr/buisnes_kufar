//From constant/keys
interface RequestedType {
	purchasesGood: boolean
	purchasesService: boolean
	salesGood: boolean
	salesService: boolean
}

interface StateMap {
	//Editor
	insertState: RequestedType
	saveStateOrder: boolean
	isDisabled: boolean
	clearState: boolean
	removeDealState: boolean
	activeTab: '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' 
	reason: string
	dueDateCheck: boolean
	dueDate: string
	additionalInfo: boolean
	vatRateCheck: boolean
  vatRate: '0' | '5' | '7' | '10' | '18' | '25'
	//TemplateElement
	htmlOrder: HTMLElement | null
	htmlBill: HTMLElement | null
	htmlSupplyContract: HTMLElement | null
	htmlDogovorUslug: HTMLElement | null
}

export function useTypedState<T extends keyof StateMap>(
	key: T, 
	defaultValue?: () => Ref<StateMap[T]>
) {
	return useState<StateMap[T]>(key, defaultValue)
}