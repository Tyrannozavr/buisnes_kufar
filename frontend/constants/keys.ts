//Использовать совместно с composables/useTypedState.ts

import type { InjectionKey, Ref } from 'vue'

/** Ключи для provide/inject в редакторе документов. */
export const injectionKeys = {
	editorSaveTriggerKey: Symbol('editorSaveTriggerKey') as InjectionKey<
		Ref<{ tab: number; ts: number }>
	>,
}


export const enum Editor {
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
	SUPPLY_CONTRACT = 'htmlSupplyContract',
	DOGOVOR_USLUG = 'htmlDogovorUslug',
}