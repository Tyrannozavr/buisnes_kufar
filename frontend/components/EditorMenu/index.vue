<template>
	<div>
		<UCard variant="subtle" class="top-26">

      <div v-if="confirmation" class="flex flex-col justify-between gap-5">
        <UButton label="Принять изменения" icon="i-lucide-check" color="success" variant="solid"
          class="w-full justify-center" @click="confirm()" />
        <UButton label="Отклонить изменения" icon="i-lucide-x" color="error" variant="soft"
          class="w-full justify-center" @click="reject(), clearCurrentForm(activeTab)" />
      </div>


			<div v-else class="flex flex-col justify-between gap-5">

				<div class="w-full">
					<UCollapsible>
						<UButton label="Заполнить данными" icon="i-lucide-file-input" class="w-full justify-center" :disabled="activeButtons" />

						<template #content>
							<div class="flex-col mt-4 justify-center">
								<div class="flex gap-2">
									<div>
										<p class="w-40 text-nowrap">Последняя закупка:</p>
									</div>
									<UButton label="Товар" color="neutral" variant="subtle" class="w-full justify-center mb-2"
										@click="insertLastPurchasesGood" />
									<UButton label="Услуга" color="neutral" variant="subtle" class="w-full justify-center mb-2"
										@click="insertLastPurchasesService" />
								</div>
								<div class="flex gap-2">
									<div>
										<p class="w-40 text-nowrap">Последняя продажа:</p>
									</div>
									<UButton label="Товар" color="neutral" variant="subtle" class="w-full justify-center"
										@click="insertLastSalesGood" />
									<UButton label="Услуга" color="neutral" variant="subtle" class="w-full justify-center"
										@click="insertLastSalesService" />
								</div>
							</div>
						</template>
					</UCollapsible>
				</div>

				<div v-if="activeTab === '0' ">
					<OrderMenu :activeButtons :inDevelopment />
				</div>

				<div v-if="activeTab === '1'">
					<BillMenu />
				</div>

				<div class="flex flex-row justify-between gap-1 w-full">
					<UCollapsible class="gap-3">
						<UButton @click="clearInput(), searchInCurrentDocument(activeTab, orderElement)" label="Поиск"
							icon="i-lucide-search" class="p-1 h-10 text-sm" />

						<template #content>
							<div class="mt-4 w-79 absolute">
								<input type="text" name="search" v-model="inputValue"
									@input="searchInCurrentDocument(activeTab, orderElement)"
									class=" border-emerald-500 border-2 rounded w-full leading-[1.75] px-2 text-lg " />
							</div>
							<div class="h-12"></div>
						</template>
					</UCollapsible>

					<UButton label="Печать" @click="printCurrentDocument(activeTab, orderElement)" icon="i-lucide-printer"
						class="p-1 w-[97px] h-10 text-sm" :disabled="activeButtons" />
					<UButton label="DOC" @click="downloadCurrentDocxBlob(activeTab)"
						icon="i-lucide-dock" class="p-1 w-[81px] h-10 text-sm" :disabled="activeButtons" />
					<UButton label="PDF" @click="downloadCurrentPdf(activeTab, orderElement)" icon="i-lucide-dock"
						class="p-1 w-[77px] h-10 text-sm" :disabled="activeButtons" />
				</div>

				<div class="flex flex-col gap-2">
					<UButton :disabled="activeButtons" @click="editButton()" label="Редактировать" icon="i-lucide-file-pen" color="neutral" variant="subtle"
						class="active:bg-green-500" />

					<div class="flex gap-2">
						<UButton label="Oчистить форму" icon="lucide:remove-formatting" color="neutral" variant="subtle"
							class="w-1/2" @click="clearCurrentForm(activeTab)" />

            <UModal
              v-model:open="modalIsOpen"
              title="Вы уверены, что хотите удалить сделку?"
              description="Удаление сделки приведет к удалению всех данных у вас и у контрагента"
            >
             <UButton label="Удалить сделку" icon="i-lucide-file-x" color="neutral" variant="subtle" class="w-1/2"/>
             
              <template #footer>
                <UButton label="Удалить сделку" icon="i-lucide-file-x" color="neutral" variant="subtle"
                  class="w-1/2" @click="removeCurrentDeal(activeTab), modalIsOpen = false" />
                <UButton label="Отмена" icon="i-lucide-x" color="neutral" variant="subtle" class="w-1/2" @click="modalIsOpen = false" />
              </template>
            </UModal>

					</div>
				</div>

				<div class="flex flex-col gap-2 text-center ">
					<p>Фото/Сканы документа</p>
					<UButton label="Выберите файл" icon="i-lucide-folder-search" color="neutral" variant="subtle" size="xl"
						class="justify-center" :disabled="activeButtons" @click="inDevelopment()" />
				</div>

        <div v-if="activeButtons" class="">
          <UButton label="Отменить изменения" size="lg" class="w-full justify-center" color="neutral" variant="subtle"
						:disabled="!activeButtons" @click="cancelChanges(activeTab), editButton()" />
        </div>

				<div class="flex flex-row justify-between">
					<UButton label="Отправить контрагенту и сохранить" size="xl" class="w-full justify-center"
						:disabled="!activeButtons || activeTab !== '0'" @click="saveChanges(), sendMessageToCounterpart()" />
				</div>
			</div>



      
    </UCard>
  </div>
</template>

<script setup lang="ts">
import { useDocxGenerator } from '~/composables/useDocxGenerator';
import { usePdfGenerator } from '~/composables/usePdfGenerator';
import { useSearch } from '~/composables/useSearch';
import { usePurchasesStore } from '~/stores/purchases';
import { useSalesStore } from '~/stores/sales';
import { Editor, TemplateElement } from '~/constants/keys';
import { useInsertState, useIsDisableState, useClearState, useSaveState, useRemoveDealState } from '~/composables/useStates';
import OrderMenu from './OrderMenu.vue';
import BillMenu from './BillMenu.vue';
import { useRoute } from 'vue-router';
import { useChatsApi } from '~/api/chats';
import { usePurchasesApi } from '~/api/purchases';


const modalIsOpen = ref(false)
const route = useRoute()
const router = useRouter()
const purchasesStore = usePurchasesStore()
const salesStore = useSalesStore()
const { deleteLastDealVersion } = usePurchasesApi()
const { purchases } = storeToRefs(purchasesStore)
const { sales } = storeToRefs(salesStore)
const activeTab = useTypedState(Editor.ACTIVE_TAB)
const orderElement = useTypedState(TemplateElement.ORDER)


const inDevelopment = () => {
	const toast = useToast()
	toast.add({
		title: 'Кнопка находиться в разработке...',
		icon: 'i-lucide-git-compare',
	})
}

//Insert Button
const { statePurchasesGood, statePurchasesService, stateSalesGood, stateSalesService } = useInsertState()
const insertState = useTypedState(Editor.INSERT_STATE)

const insertLastPurchasesGood = (): void => {
	statePurchasesGood(true)
	doubleReversDisable()
}

const insertLastPurchasesService = (): void => {
	statePurchasesService(true)
	doubleReversDisable()
}

const insertLastSalesGood = (): void => {
	stateSalesGood(true)
	doubleReversDisable()
}

const insertLastSalesService = (): void => {
	stateSalesService(true)
	doubleReversDisable()
}

//DOCX
const { downloadBlob, generateDocxOrder, generateDocxBill } = useDocxGenerator()

let orderDocxBlob: Blob | null = null
let billDocxBlob: Blob | null = null

//присвоение корректного Blob в зависимости от выбранной сделки
watch(
	insertState,
	async (insert) => {
		if (purchases.value.goodsDeals && insert.purchasesGood) {
			if (purchasesStore.lastGoodsDeal) {
				orderDocxBlob = await generateDocxOrder(purchasesStore.lastGoodsDeal)
			}

		} else if (purchases.value.servicesDeals && insert.purchasesService) {
			if (purchasesStore.lastServicesDeal) {
				orderDocxBlob = await generateDocxOrder(purchasesStore.lastServicesDeal)
			}

		} else if (sales.value.goodsDeals && insert.salesGood) {
			if (salesStore.lastGoodsDeal) {
				orderDocxBlob = await generateDocxOrder(salesStore.lastGoodsDeal)
			}

		} else if (sales.value.servicesDeals && insert.salesGood) {
			if (salesStore.lastServicesDeal) {
				orderDocxBlob = await generateDocxOrder(salesStore.lastServicesDeal)
			}
		}
	},
	{ immediate: false, deep: true }
)

const downloadCurrentDocxBlob = async (activeTab: string): Promise<void> => {
	if (activeTab === '0' && orderDocxBlob) {
		downloadBlob(orderDocxBlob, 'Order.docx')
	} else if (activeTab === '1') {
		if (!billDocxBlob) {
			// Генерируем billDocxBlob динамически при необходимости
			// TODO: передать нужные данные для генерации Bill
			return
		}
		downloadBlob(billDocxBlob, 'Bill.docx')
	}
}

//PDF
const { downloadPdf } = usePdfGenerator()

const downloadCurrentPdf = (activeTab: string, orderElement: HTMLElement | null): void => {
	if (activeTab === '0') {
		const fileName = 'Order'
		downloadPdf(orderElement, fileName)
	}
}

//Print 
const { printDocument } = usePdfGenerator()

const printCurrentDocument = (activeTab: string, orderElement: HTMLElement | null) => {
	if (activeTab === '0') {
		printDocument(orderElement)
	}
}

//Search
const { searchInDocument } = useSearch()
const inputValue: Ref<string> = ref('')

const clearInput = () => {
	inputValue.value = ''
}

const searchInCurrentDocument = (activeTab: string, orderElement: HTMLElement | null) => {
	if (activeTab === '0') {
		searchInDocument(orderElement, inputValue.value)
	}
}

//Button edit
const { reversDisable, doubleReversDisable } = useIsDisableState()
const activeButtons: Ref<boolean> = ref(false)

const editButton = () => {
	reversDisable()
	activeButtons.value = !activeButtons.value
}

//Button clearForm
const { applyClearState } = useClearState()

const clearCurrentForm = (activeTab: string) => {
	applyClearState()
}

//Button removeCurrentDeal
const { removeDeal } = useRemoveDealState()

const removeCurrentDeal = (activeTab: string) => {
	if (activeTab === '0') {
		removeDeal()
	}
}

// save button 
const { saveOrder } = useSaveState()
const { createChat, sendMessage } = useChatsApi()

const getCounterpartCompanyIdAndDealNumber = (): { companyId: number, dealNumber: string } | null => {
	const query = route.query
	const dealId = Number(query?.dealId)
	const role = query?.role
  const productType = query?.productType
  
	if (!dealId || !role || !productType) return null

	if (role === 'buyer') {
		if (productType === 'goods') {
			const deal = purchasesStore.findGoodsDeal(dealId)
      return { companyId: deal?.seller?.companyId ?? 0, dealNumber: deal?.sellerOrderNumber ?? '' }
      
		} else if (productType === 'services') {
			const deal = purchasesStore.findServicesDeal(dealId)
			return { companyId: deal?.seller?.companyId ?? 0, dealNumber: deal?.sellerOrderNumber ?? '' }
		}
  }
  
	if (role === 'seller') {
		if (productType === 'goods') {
			const deal = salesStore.findGoodsDeal(dealId)
      return { companyId: deal?.buyer?.companyId ?? 0, dealNumber: deal?.buyerOrderNumber ?? '' }
      
		} else if (productType === 'services') {
			const deal = salesStore.findServicesDeal(dealId)
			return { companyId: deal?.buyer?.companyId ?? 0, dealNumber: deal?.buyerOrderNumber ?? '' }
		}
	}
	return null
}

const sendMessageToCounterpart = async (isConfirm?: boolean): Promise<void> => {
  const dealId = route.query.dealId
  const role = route.query.role === 'seller' ? 'buyer' : 'seller'//меняем роль на противоположную
  const productType = route.query.productType
  const counterpartData = getCounterpartCompanyIdAndDealNumber()
  if (!counterpartData) {
    useToast().add({ title: 'Нет данных о контрагенте', color: 'error' })
    return
  }
  const orderNumber = String(await Promise.resolve(counterpartData.dealNumber ?? ''))
  const chatData = await createChat({ participantId: counterpartData.companyId })
  if (chatData?.id) {
    const resolvedDealRoute = router.resolve({
      path: route.path,
      query: {
        dealId: dealId,
        role: role,
        productType: productType,
        confirmation: isConfirm === undefined ? 'true' : 'false', //выставляем true если изменения приняты или отклонены, false если мы отправляем сообщение об изменениях 
      },
    })
    const reviewUrl = process.client
      ? new URL(resolvedDealRoute.href, window.location.origin).toString()
      : resolvedDealRoute.href

    const normalizedReviewUrl = String(await Promise.resolve(reviewUrl))

    let content = ''
    if (isConfirm === true) {
      content = `Изменения заказа ${orderNumber} ПРИНЯТЫ. [Просмотр заказа](${normalizedReviewUrl})`
    } else if (isConfirm === false) {
      content = `Изменения заказа ${orderNumber} ОТКЛОНЕНЫ. [Просмотр заказа](${normalizedReviewUrl})`
    } else {
      content = `Изменены условия заказа ${orderNumber}. Пожалуйста, ознакомьтесь с обновлённой версией. [Просмотр заказа](${normalizedReviewUrl})`
    }

    await sendMessage(chatData.id, {
      content: content,
    })
  }
}

const saveChanges = async (): Promise<void> => {
  if (activeTab.value !== '0') return
  
	try {
    // Сначала создаем новую версию, чтобы исходная версия осталась нетронутой для reject.
    if (route.query.role === 'seller') {
      await salesStore.createNewDealVersion(Number(route.query.dealId))
    } else if (route.query.role === 'buyer') {
      await purchasesStore.createNewDealVersion(Number(route.query.dealId))
    }
		await saveOrder()
    editButton()

		useToast().add({
			title: 'Изменения сохранены и отправлены контрагенту',
			color: 'success',
    })
    
	} catch (err) {
		console.error('Ошибка при отправке контрагенту:', err)
		useToast().add({
			title: 'Ошибка при отправке сообщения контрагенту',
			color: 'error',
		})
	}
}

// cancel button
const cancelChanges = (activeTab: string) => {
  const role = route.query.role
  const productType = route.query.productType

  if (role === 'seller') {
    if (productType === 'goods') {
      insertLastSalesGood()
    } else if (productType === 'services') {
      insertLastSalesService()
    }
  } else if (role === 'buyer') {
    if (productType === 'goods') {
      insertLastPurchasesGood()
    } else if (productType === 'services') {
      insertLastPurchasesService()
    }
  }
}

//подтверждение изменений при изменении заказа одной из сторон
const confirmation = ref(false)

watch(() => route.fullPath,
  () => {
  confirmation.value = route.query.confirmation === 'true' ? true : false
}, { immediate: true, deep: true})

const confirm = () => {
  router.replace({ query: { ...route.query, confirmation: 'false' } })
  sendMessageToCounterpart(true)
  useToast().add({
    title: 'Изменения приняты',
    color: 'success',
  })
}

const reject = async () => {
  router.replace({ query: { ...route.query, confirmation: 'false' } })
  sendMessageToCounterpart(false)
  const dealId = Number(route.query.dealId)

  if (dealId) {
    await deleteLastDealVersion(dealId)
    await purchasesStore.getDeals()
    await salesStore.getDeals()
  }
  

  useToast().add({
    title: 'Изменения отклонены',
    color: 'warning',
  })
}

</script>