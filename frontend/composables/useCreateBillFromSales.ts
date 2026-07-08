import { useRouter } from "vue-router"
import { useDeals } from "~/composables/useDeals"
import { useBillFillState } from "~/composables/useBillFillState"
import { usePurchasesApi } from "~/api/purchases"
import { formatDocumentLinkLabel, normalizeDate } from "~/utils/normalize"
import type { CompanyContractItem } from "~/types/companyContract"

const WITHOUT_CONTRACT_VALUE = "__without_contract__"

/**
 * Диалог «Создать счет» из таблицы Продажи (§3.1).
 */
export function useCreateBillFromSales() {
	const router = useRouter()
	const toast = useToast()
	const purchasesApi = usePurchasesApi()
	const {
		createBill,
		findDealByDealNumber,
		editBillReason,
		editContractBinding,
		updateDeal,
	} = useDeals()
	const { markBillAwaitingFill } = useBillFillState()

	const isNoContractModalOpen = ref(false)
	const isContractSelectModalOpen = ref(false)
	const pendingDealNumber = ref("")
	const contractOptions = ref<CompanyContractItem[]>([])
	const selectedContractValue = ref<string | undefined>()
	const isBusy = ref(false)

	const contractSelectItems = computed(() => [
		...contractOptions.value.map((contract) => ({
			label: `№ ${contract.number} от ${normalizeDate(contract.date)}`,
			value: String(contract.id),
		})),
		{ label: "Без договора", value: WITHOUT_CONTRACT_VALUE },
	])

	const getDealIdForPending = () => {
		const deal = findDealByDealNumber(pendingDealNumber.value, "seller")
		return deal?.dealId
	}

	const navigateToNewBill = async (dealId: number) => {
		markBillAwaitingFill(dealId)
		await router.push({
			path: "/profile/editor",
			query: {
				dealId: dealId.toString(),
				role: "seller",
			},
			hash: "#bill",
		})
	}

	const finalizeBillCreation = async (
		dealId: number,
		basis?: { number: string; date: string },
	) => {
		isBusy.value = true
		try {
			await createBill(dealId, { fillFromDeal: false })

			if (basis) {
				const reason = formatDocumentLinkLabel(basis.number, basis.date)
				await editBillReason(dealId, reason)
				await editContractBinding(dealId, basis.number, basis.date)
				updateDeal(dealId)
			}

			await navigateToNewBill(dealId)
			toast.add({
				title: "Счёт создан",
				description: basis
					? "Основание заполнено из выбранного договора"
					: "Номер и дата присвоены",
				color: "success",
			})
		} catch {
			toast.add({
				title: "Не удалось создать счёт",
				color: "error",
			})
		} finally {
			isBusy.value = false
			isNoContractModalOpen.value = false
			isContractSelectModalOpen.value = false
			pendingDealNumber.value = ""
			selectedContractValue.value = undefined
			contractOptions.value = []
		}
	}

	const startCreateBill = async (dealNumber: string) => {
		const deal = findDealByDealNumber(dealNumber, "seller")
		if (!deal) return

		const buyerCompanyId = deal.buyer.companyId
		if (!buyerCompanyId) {
			toast.add({
				title: "Не удалось определить покупателя",
				color: "error",
			})
			return
		}

		pendingDealNumber.value = dealNumber
		isBusy.value = true

		try {
			const response = await purchasesApi.getCompanyContracts(buyerCompanyId)
			const contracts = response?.contracts ?? []

			if (!contracts.length) {
				isNoContractModalOpen.value = true
				return
			}

			contractOptions.value = contracts
			selectedContractValue.value = String(contracts[0]?.id ?? WITHOUT_CONTRACT_VALUE)
			isContractSelectModalOpen.value = true
		} catch {
			toast.add({
				title: "Не удалось загрузить договоры",
				color: "error",
			})
		} finally {
			isBusy.value = false
		}
	}

	const confirmCreateWithoutContract = async () => {
		const dealId = getDealIdForPending()
		if (!dealId) return
		await finalizeBillCreation(dealId)
	}

	const confirmCreateWithSelectedContract = async () => {
		const dealId = getDealIdForPending()
		if (!dealId) return

		const selected = selectedContractValue.value
		if (!selected) {
			toast.add({
				title: "Выберите договор",
				color: "warning",
			})
			return
		}

		if (selected === WITHOUT_CONTRACT_VALUE) {
			await finalizeBillCreation(dealId)
			return
		}

		const contract = contractOptions.value.find((item) => String(item.id) === selected)
		if (!contract) {
			toast.add({
				title: "Договор не найден",
				color: "error",
			})
			return
		}

		await finalizeBillCreation(dealId, {
			number: contract.number,
			date: contract.date,
		})
	}

	const cancelDialogs = () => {
		isNoContractModalOpen.value = false
		isContractSelectModalOpen.value = false
		pendingDealNumber.value = ""
		selectedContractValue.value = undefined
		contractOptions.value = []
	}

	return {
		isNoContractModalOpen,
		isContractSelectModalOpen,
		contractSelectItems,
		selectedContractValue,
		isBusy,
		startCreateBill,
		confirmCreateWithoutContract,
		confirmCreateWithSelectedContract,
		cancelDialogs,
	}
}
