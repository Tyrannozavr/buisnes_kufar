export const enum RequestedType {
	PURCHASES_GOOD = 'purchases-good',
	PURCHASES_SERVICE = 'purchases-service',
	SALES_GOOD = 'sales-good',
	SALES_SERVICE = 'sales-service'
}

export const enum Editor {
	INSERT_STATE = 'insertState',
	SAVE_STATE_ORDER = 'saveStateOrder',
	IS_DISABLED = 'isDisabled',
	CLEAR_STATE = 'clearState',
	REMOVE_DEAL = 'removeDealState',
	ACTIVE_TAB = 'activeTab',
}

export const enum TemplateElement {
	ORDER = 'htmlOrder',
	BILL = 'htmlBill',
}