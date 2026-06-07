/**
 * Оркестратор entity-договора поставки для редактора сделки.
 *
 * Новое API: supply_contract / supply_contract_specification (не legacy POST /deals/{id}/supply-contract).
 * Используется в SupplyContractMenu: check → create → bind → guard перед spec.
 * Feauture: будет использоваться перед оформлением заказа для проверки наличия договора поставки между компаниями
 */
import { useQueryCache } from '@pinia/colada'
import { useDeals } from '~/composables/useDeals'
import { QueryKeys } from '~/constants/queryKeys'
import {
	useCreateSupplyContractEntityQuery,
	useCreateSupplySpecificationQuery,
} from '~/queries/purchases'
import type { Deal } from '~/types/dealState'
import type {
	SupplyContractEntityResponse,
	SupplyContractEntityStatus,
	SupplyContractExistsResponse,
	SpecificationEntityResponse,
} from '~/types/supplyContractEntity'
import {
	resolveSupplyContractEntityStatus,
	SUPPLY_CONTRACT_STATUS_LABELS,
} from '~/types/supplyContractEntity'
import { usePurchasesApi } from '~/api/purchases'
import { normalizeSpecificationNumber } from '~/utils/normalize'

/** Копирует данные entity API в локальный deal (store), без PUT сделки на сервер. */
const syncContractEntityToDeal = (
	deal: Deal,
	contract: SupplyContractEntityResponse,
	spec?: SpecificationEntityResponse | null,
) => {
	deal.supplyContract.entityId = contract.id
	deal.supplyContract.number = contract.number
	deal.supplyContract.entityDate = contract.date
	deal.supplyContract.supplyContractText = contract.terms_text ?? ''
	deal.supplyContract.supplierDetailsCheck = contract.supplier_details_check
	deal.supplyContract.buyerDetailsCheck = contract.buyer_details_check
	deal.supplyContract.coverLetterCheck = contract.cover_letter_check

	if (spec) {
		deal.supplyContract.specificationEntityId = spec.id
		deal.supplyContract.specificationNumber = normalizeSpecificationNumber(spec.spec_number)
		deal.supplyContract.specificationDate = spec.spec_date
	} else if (contract.specifications?.length) {
		const latestSpec = contract.specifications[contract.specifications.length - 1]
		deal.supplyContract.specificationEntityId = latestSpec?.id ?? 0
		deal.supplyContract.specificationNumber = normalizeSpecificationNumber(latestSpec?.spec_number)
		deal.supplyContract.specificationDate = latestSpec?.spec_date ?? ''
	}
}

export const useSupplyContractEntity = (dealId: Ref<number | null | undefined>) => {
	const route = useRoute()
	const queryCache = useQueryCache()
	const toast = useToast()
	const { findDeal } = useDeals()
	const { createSupplyContractEntity } = useCreateSupplyContractEntityQuery()
	const { createSupplySpecification } = useCreateSupplySpecificationQuery()

	// --- reactive state (UI + entity cache) ---

	const status = ref<SupplyContractEntityStatus>('loading')
	const contractEntity = ref<SupplyContractEntityResponse | null>(null)
	const isBusy = ref(false)

	// --- context: какая сделка и пара компаний ---

	/** dealId из аргумента или ?dealId= в URL редактора. */
	const resolvedDealId = computed(() => {
		const fromArg = dealId.value
		if (fromArg && fromArg > 0) return fromArg
		const fromRoute = Number(route.query.dealId)
		return Number.isFinite(fromRoute) && fromRoute > 0 ? fromRoute : null
	})

	/** buyer/seller из deal store — нужны для GET /supply-contracts/exists. */
	const companyPair = computed(() => {
		const deal = resolvedDealId.value ? findDeal(resolvedDealId.value) : undefined
		if (!deal?.buyer?.companyId || !deal?.seller?.companyId) {
			return null
		}
		return {
			buyerCompanyId: deal.buyer.companyId,
			sellerCompanyId: deal.seller.companyId,
		}
	})

	// --- UI helpers для UAlert в SupplyContractMenu ---

	const statusLabel = computed(() => SUPPLY_CONTRACT_STATUS_LABELS[status.value])

	const statusColor = computed(() => {
		switch (status.value) {
			case 'found':
				return 'success'
			case 'not_found':
				return 'warning'
			case 'expired':
				return 'error'
			default:
				return 'neutral'
		}
	})

	// --- check: есть ли договор на пару компаний ---

	/** Разбор ответа exists + синхронизация deal, если договор найден. */
	const applyExistsResponse = (response: SupplyContractExistsResponse | undefined) => {
		contractEntity.value = response?.supply_contract ?? null
		status.value = resolveSupplyContractEntityStatus(
			Boolean(response?.is_exist),
			response?.supply_contract,
		)

		const deal = resolvedDealId.value ? findDeal(resolvedDealId.value) : undefined
		if (deal && contractEntity.value) {
			syncContractEntityToDeal(deal, contractEntity.value)
		}
	}

	/** GET /supply-contracts/exists — обновляет status и contractEntity. */
	const refreshStatus = async (): Promise<boolean> => {
		if (!companyPair.value) {
			status.value = 'not_found'
			contractEntity.value = null
			return true
		}

		status.value = 'loading'
		try {
			const response = await usePurchasesApi().checkSupplyContractExists(
				companyPair.value.buyerCompanyId,
				companyPair.value.sellerCompanyId,
			)
			applyExistsResponse(response)
			queryCache.setQueryData(
				[
					QueryKeys.SUPPLY_CONTRACT_EXISTS,
					companyPair.value.buyerCompanyId,
					companyPair.value.sellerCompanyId,
				],
				response,
			)
			return true
		} catch {
			status.value = 'not_found'
			contractEntity.value = null
			toast.add({
				title: 'Ошибка',
				description: 'Не удалось проверить договор поставки',
				color: 'error',
			})
			return false
		}
	}

	// --- create contract: POST entity + bind к order ---

	/**
	 * Гарантирует наличие entity-договора.
	 * Если нет — создаёт (POST /supply-contracts) и bind (POST .../supply-contract-entity/bind).
	 */
	const ensureContractEntity = async (): Promise<boolean> => {
		if (status.value === 'found' && contractEntity.value) {
			return true
		}

		await refreshStatus()

		if (status.value === 'found') {
			return true
		}

		if (status.value === 'expired') {
			toast.add({
				title: 'Договор недействителен',
				description: 'У договора нет номера или даты. Создайте новый договор.',
				color: 'error',
			})
			return false
		}

		if (!companyPair.value) {
			toast.add({
				title: 'Нет данных сделки',
				description: 'Не удалось определить компании покупателя и продавца',
				color: 'error',
			})
			return false
		}

		isBusy.value = true
		try {
			const created = await createSupplyContractEntity({
				buyer_company_id: companyPair.value.buyerCompanyId,
				seller_company_id: companyPair.value.sellerCompanyId,
			})
			if (!created) {
				return false
			}
			contractEntity.value = created
			status.value = 'found'

			const deal = resolvedDealId.value ? findDeal(resolvedDealId.value) : undefined
			if (deal) {
				syncContractEntityToDeal(deal, created)
			}
			if (resolvedDealId.value) {
				await usePurchasesApi().bindSupplyContractToDeal(resolvedDealId.value, created.id)
			}

			toast.add({
				title: 'Договор создан',
				description: `№ ${created.number} от ${normalizeDate(created.date)}`,
				color: 'success',
			})
			return true
		} catch (error: unknown) {
			const message =
				typeof error === 'object' &&
				error !== null &&
				'data' in error &&
				typeof (error as { data?: { detail?: string } }).data?.detail === 'string'
					? (error as { data: { detail: string } }).data.detail
					: 'Не удалось создать договор поставки'
			toast.add({ title: 'Ошибка', description: message, color: 'error' })
			return false
		} finally {
			isBusy.value = false
		}
	}

	// --- create spec: guard + POST + bind ---

	/** Guard перед вкладкой «Спецификация» — договор должен быть found. */
	const ensureContractForSpecification = async (): Promise<boolean> => {
		await refreshStatus()

		if (status.value === 'not_found') {
			toast.add({
				title: 'Договор не найден',
				description: 'Сначала создайте договор поставки для этой пары компаний',
				color: 'warning',
			})
			return false
		}

		if (status.value === 'expired') {
			toast.add({
				title: 'Договор недействителен',
				description: 'Нельзя создать спецификацию без действующего договора',
				color: 'error',
			})
			return false
		}

		return Boolean(contractEntity.value)
	}

	/**
	 * POST /supply-contracts/{id}/specifications + bind (POST .../supply-specification/bind).
	 * Вызывается из кнопки «Создать спецификацию» в меню.
	 */
	const createSpecificationEntity = async (): Promise<SpecificationEntityResponse | null> => {
		const canProceed = await ensureContractForSpecification()
		if (!canProceed || !contractEntity.value) {
			return null
		}

		isBusy.value = true
		try {
			const spec = await createSupplySpecification(contractEntity.value.id)
			if (!spec) {
				return null
			}

			const deal = resolvedDealId.value ? findDeal(resolvedDealId.value) : undefined
			if (deal) {
				syncContractEntityToDeal(deal, contractEntity.value, spec)
			}
			if (resolvedDealId.value) {
				await usePurchasesApi().bindSupplySpecificationToDeal(resolvedDealId.value, spec.id)
			}

			toast.add({
				title: 'Спецификация создана',
				description: `№ ${spec.spec_number}`,
				color: 'success',
			})
			return spec
		} catch {
			toast.add({
				title: 'Ошибка',
				description: 'Не удалось создать спецификацию',
				color: 'error',
			})
			return null
		} finally {
			isBusy.value = false
		}
	}

	// --- auto-check при смене сделки ---

	watch(
		[resolvedDealId, companyPair],
		() => {
			if (!companyPair.value) {
				status.value = 'not_found'
				contractEntity.value = null
				return
			}
			refreshStatus()
		},
		{ immediate: true },
	)

	return {
		status,
		statusLabel,
		statusColor,
		contractEntity,
		isBusy,
		refreshStatus,
		ensureContractEntity,
		ensureContractForSpecification,
		createSpecificationEntity,
	}
}
