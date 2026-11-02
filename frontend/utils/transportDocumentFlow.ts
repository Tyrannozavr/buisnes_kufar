/**
 * Чистая машина состояний диалога «Создать документ» (§1.3).
 * Без Vue/API — удобно юнит-тестировать.
 */
import {
	TRANSPORT_CHILD_PARENT,
	TRANSPORT_DOCUMENT_TYPE_LABELS,
	TRANSPORT_FRAMEWORK_TYPES,
	type TransportContractSnapshot,
	type TransportDocumentType,
} from '~/types/transportDocument'

export type TransportDocFlowStep =
	| { step: 'type_select' }
	| { step: 'alert'; title: string; message: string; backTo: 'type_select' | 'close' }
	| {
			step: 'org_contracts_picker'
			docType: TransportDocumentType
			/** false у договор-заявки — справа список договоров не показываем */
			showContracts: boolean
	  }
	| {
			step: 'create_child'
			docType: TransportDocumentType
			parentId: number
			parentType: TransportDocumentType
	  }

const MSG_NO_CARRIERS =
	'Добавьте организацию в раздел Перевозчики для создания договора'

function parentOnDeal(
	snapshot: TransportContractSnapshot,
	parentType: TransportDocumentType,
): { id: number; type: TransportDocumentType } | null {
	const docs = snapshot?.documents ?? []
	for (const d of docs) {
		if (d?.type === parentType && d.id) {
			return { id: d.id, type: parentType }
		}
	}
	// legacy MVP: type transport_expedition ≈ expedition_contract без id
	if (
		parentType === 'expedition_contract' &&
		(snapshot?.type === 'expedition_contract' || snapshot?.type === 'transport_expedition') &&
		snapshot?.number
	) {
		return null
	}
	if (snapshot?.type === parentType && typeof (snapshot as { id?: number }).id === 'number') {
		return { id: (snapshot as { id: number }).id, type: parentType }
	}
	return null
}

/** После выбора радиокнопки — куда идти дальше. */
export function resolveTransportDocFlow(args: {
	docType: TransportDocumentType
	carriersCount: number
	dealTransport: TransportContractSnapshot
}): TransportDocFlowStep {
	const { docType, carriersCount, dealTransport } = args
	const parentType = TRANSPORT_CHILD_PARENT[docType]

	if (parentType) {
		const parent = parentOnDeal(dealTransport, parentType)
		if (!parent) {
			const msg =
				parentType === 'carriage_contract'
					? 'В заказе нет выбранных Договоров на перевозку грузов'
					: 'В заказе нет выбранных Договоров транспортной экспедиции'
			return {
				step: 'alert',
				title: TRANSPORT_DOCUMENT_TYPE_LABELS[docType],
				message: msg,
				backTo: 'type_select',
			}
		}
		return {
			step: 'create_child',
			docType,
			parentId: parent.id,
			parentType,
		}
	}

	if (carriersCount <= 0) {
		return {
			step: 'alert',
			title: TRANSPORT_DOCUMENT_TYPE_LABELS[docType],
			message: MSG_NO_CARRIERS,
			backTo: 'close',
		}
	}

	const showContracts = (TRANSPORT_FRAMEWORK_TYPES as readonly string[]).includes(docType)
	return {
		step: 'org_contracts_picker',
		docType,
		showContracts,
	}
}

export function isTransportFrameworkType(docType: string): boolean {
	return (TRANSPORT_FRAMEWORK_TYPES as readonly string[]).includes(docType)
}
