//Использовать совместно с composables/useTypedState.ts

import type { InjectionKey, Ref } from 'vue'

/** Ключи для provide/inject в редакторе документов. */
export const injectionKeys = {
	editorSaveTriggerKey: Symbol('editorSaveTriggerKey') as InjectionKey<
		Ref<{ tab: number; ts: number }>
	>,
}


export const enum Editor {
	SAVE_STATE = 'saveState',
	IS_DISABLED = 'isDisabled',
	CLEAR_STATE = 'clearState',
	REMOVE_DEAL = 'removeDealState',
	ACTIVE_TAB = 'activeTab',
	REASON_CHECK = 'reasonCheck',
	PAYMENT_TERMS = 'paymentTerms',
	PAYMENT_TERMS_CHECK = 'paymentTermsCheck',
	ADDITIONAL_INFO_CHECK = 'additionalInfoCheck',
	VAT_RATE_CHECK = 'vatRateCheck',
	VAT_RATE = 'vatRate',
	BILL_TYPE = 'billType',
	CONTRACT_TERMS = 'contractTerms',
	CONTRACT_TERMS_CHECK = 'contractTermsCheck',
}

export const enum TemplateElement {
	ORDER = 'htmlOrder',
	BILL = 'htmlBill',
	SUPPLY_CONTRACT = 'htmlSupplyContract',
	DOGOVOR_USLUG = 'htmlDogovorUslug',
}