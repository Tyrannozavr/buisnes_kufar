//Использовать совместно с composables/useTypedState.ts

import type { InjectionKey, Ref } from 'vue'

/** Ключи для provide/inject в редакторе документов. */
export const injectionKeys = {
	editorSaveTriggerKey: Symbol('editorSaveTriggerKey') as InjectionKey<
		Ref<{ tab: number; ts: number }>
	>,
}

export const enum RequestedType {
	PURCHASES_GOOD = 'purchasesGood',
	PURCHASES_SERVICE = 'purchasesService',
	SALES_GOOD = 'salesGood',
	SALES_SERVICE = 'salesService'
}

export const enum Editor {
	INSERT_STATE = 'insertState',
	SAVE_STATE_ORDER = 'saveStateOrder',
	/** Опции при сохранении заказа: создать версию для контрагента и колбэк по завершении. */
	SAVE_ORDER_OPTIONS = 'saveOrderOptions',
	IS_DISABLED = 'isDisabled',
	CLEAR_STATE = 'clearState',
	REMOVE_DEAL = 'removeDealState',
	ACTIVE_TAB = 'activeTab',
	/** Выбранная версия заказа для просмотра (null = активная из store). */
	SELECTED_ORDER_VERSION = 'selectedOrderVersion',
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
	SUPPLY_CONTRACT = 'htmlSupplyContract',
	DOGOVOR_USLUG = 'htmlDogovorUslug',
}