//Использовать совместно с composables/useTypedState.ts

export const enum RequestedType {
	PURCHASES_GOOD = 'purchasesGood',
	PURCHASES_SERVICE = 'purchasesService',
	SALES_GOOD = 'salesGood',
	SALES_SERVICE = 'salesService'
}

export const enum Editor {
	INSERT_STATE = 'insertState',
	SAVE_STATE_ORDER = 'saveStateOrder',
	IS_DISABLED = 'isDisabled',
	CLEAR_STATE = 'clearState',
	REMOVE_DEAL = 'removeDealState',
	ACTIVE_TAB = 'activeTab',
	REASON = 'reason',
	DUE_DATE_CHECK = 'dueDateCheck',
	DUE_DATE = 'dueDate',
	ADDITIOANAL_INFO = 'additionalInfo',
	VAT_RATE_CHECK = 'vatRateCheck',
	VAT_RATE = 'vatRate',
}

export const enum TemplateElement {
	ORDER = 'htmlOrder',
	BILL = 'htmlBill',
}