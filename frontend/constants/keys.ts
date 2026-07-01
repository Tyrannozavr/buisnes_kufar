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
	/** Инкремент при «Заполнить данными» — перезагрузка формы даже для той же сделки */
	LOAD_DEAL_TRIGGER = 'loadDealTrigger',
	/** Diff заказа для подсветки изменений при согласовании */
	ORDER_CHANGE_DIFF = 'orderChangeDiff',
	/** Счёт создан, полное заполнение — только по кнопке (§1.3) */
	BILL_AWAITING_FILL = 'billAwaitingFill',

	//bill
	BILL_TYPE = 'billType',
	REASON_CHECK = 'reasonCheck',
	VAT_RATE_CHECK = 'vatRateCheck',
	VAT_RATE = 'vatRate',

	//bill-payment(счет-оплата)
	PAYMENT_TERMS = 'paymentTerms',
	PAYMENT_TERMS_CHECK = 'paymentTermsCheck',
	ADDITIONAL_INFO_CHECK = 'additionalInfoCheck',

	//bill-contract
	PAYMENT_TERMS_CONTRACT = 'paymentTermsContract',
	DELIVERY_TERMS_CONTRACT = 'deliveryTermsContract',
	CONTRACT_TERMS_CONTRACT = 'contractTermsContract',
	CONTRACT_TERMS_TEXT_CONTRACT = 'contractTermsTextContract',
	PAYMENT_TERMS_CHECK_CONTRACT = 'paymentTermsCheckContract',
	DELIVERY_TERMS_CHECK_CONTRACT = 'deliveryTermsCheckContract',
	CONTRACT_TERMS_CHECK_CONTRACT = 'contractTermsCheckContract',
	
	//bill-offer
	PAYMENT_TERMS_OFFER = 'paymentTermsOffer',
	CONTRACT_TERMS_OFFER = 'contractTermsOffer',
	CONTRACT_TERMS_TEXT_OFFER = 'contractTermsTextOffer',
	CONTRACT_TERMS_CHECK_OFFER = 'contractTermsCheckOffer',
	PAYMENT_TERMS_CHECK_OFFER = 'paymentTermsCheckOffer',
	ADDITIONAL_INFO_CHECK_OFFER = 'additionalInfoCheckOffer',

	//supply contract
	COVER_LETTER_CHECK = 'coverLetterCheck',
	SUPPLIER_DETAILS_CHECK = 'supplierDetailsCheck',
	BUYER_DETAILS_CHECK = 'buyerDetailsCheck',
	SUPPLY_CONTRACT_TYPE = 'supplyContractType',
	SUPPLY_CONTRACT_OFFICIALS_SELLER = 'supplyContractOfficialsSeller',
	SUPPLY_CONTRACT_TABLE_DATA = 'supplyContractTableData',
	/** Инкремент при изменении данных слота SupplyContract (товары, суммы и т.д.) */
	SUPPLY_CONTRACT_SLOT_REVISION = 'supplyContractSlotRevision',
	SUPPLY_CONTRACT_PREVIEW_ELEMENT = 'supplyContractPreviewElement',
}

export const enum TemplateElement {
	ORDER = 'htmlOrder',
	BILL = 'htmlBill',
	SUPPLY_CONTRACT = 'htmlSupplyContract',
	SPECIFICATION = 'htmlSpecification',
	DOGOVOR_USLUG = 'htmlDogovorUslug',
}