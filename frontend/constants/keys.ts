import type { InjectionKey } from "vue";
import type { Insert } from "~/types/contracts";

export const enum RequestedType {
	PURCHASES_GOOD = 'purchases-good',
	PURCHASES_SERVICE = 'purchases-service',
	SALES_GOOD = 'sales-good',
	SALES_SERVICE = 'sales-service'
}

interface InjectionKeys {
	insertStateKey: InjectionKey<Ref<Insert>>
	changeStateOrderKey: InjectionKey<Ref<Boolean>>
	isDisabledKey: string
	clearStateKey: InjectionKey<Ref<Boolean>>
	removeDealStateKey: InjectionKey<Ref<Boolean>>
}

export const injectionKeys: InjectionKeys = {
	insertStateKey: Symbol('insertState'),
	changeStateOrderKey: Symbol('changeStateOrder'),
	isDisabledKey: 'isDisabled',
	clearStateKey: Symbol('clearState'),
	removeDealStateKey: Symbol('removeDealState'),
}