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

        <InsertButtons :activeButtons="activeButtons" :isCancelChanges="isCancelChanges" />

        <div v-if="activeTab === '0'">
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
          <UButton label="DOC" @click="downloadCurrentDocxBlob(activeTab)" icon="i-lucide-dock"
            class="p-1 w-[81px] h-10 text-sm" :disabled="activeButtons" />
          <UButton label="PDF" @click="downloadCurrentPdf(activeTab, orderElement)" icon="i-lucide-dock"
            class="p-1 w-[77px] h-10 text-sm" :disabled="activeButtons" />
        </div>

        <div class="flex flex-col gap-2">
          <UButton :disabled="activeButtons" @click="editButton()" label="Редактировать" icon="i-lucide-file-pen"
            color="neutral" variant="subtle" class="active:bg-green-500" />

          <div class="flex gap-2">
            <UButton label="Oчистить форму" icon="lucide:remove-formatting" color="neutral" variant="subtle"
              class="w-1/2" @click="clearCurrentForm(activeTab)" />

            <UModal v-model:open="modalIsOpen" title="Вы уверены, что хотите удалить сделку?"
              description="Удаление сделки приведет к удалению всех данных у вас и у контрагента">
              <UButton label="Удалить сделку" icon="i-lucide-file-x" color="neutral" variant="subtle" class="w-1/2" />

              <template #footer>
                <UButton label="Удалить сделку" icon="i-lucide-file-x" color="neutral" variant="subtle" class="w-1/2"
                  @click="removeCurrentDeal(activeTab), modalIsOpen = false" />
                <UButton label="Отмена" icon="i-lucide-x" color="neutral" variant="subtle" class="w-1/2"
                  @click="modalIsOpen = false" />
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
          :disabled="!activeButtons || activeTab !== '0'" 
          @click="
            saveChanges(),
            sendMessageToCounterpart(Number(route.query.dealId), route.query.role as 'buyer' | 'seller', counterpartData as CounterpartData)"
          />
        </div>
      </div>
    </UCard>
  </div>
</template>

<script setup lang="ts">
import InsertButtons from './InsertButtons.vue';
import OrderMenu from './OrderMenu.vue';
import BillMenu from './BillMenu.vue';
import { useDocxGenerator } from '~/composables/useDocxGenerator';
import { usePdfGenerator } from '~/composables/usePdfGenerator';
import { useSearch } from '~/composables/useSearch';
import { usePurchasesStore } from '~/stores/purchases';
import { useSalesStore } from '~/stores/sales';
import { Editor, TemplateElement } from '~/constants/keys';
import { useIsDisableState, useClearState, useSaveState, useRemoveDealState } from '~/composables/useStates';
import { useRoute } from 'vue-router';
import { usePurchasesApi } from '~/api/purchases';
import { getCounterpartData, sendMessageToCounterpart } from '~/utils/counterpart';
import type { CounterpartData } from '~/utils/counterpart';

const modalIsOpen = ref(false)
const route = useRoute()
const router = useRouter()
const purchasesStore = usePurchasesStore()
const salesStore = useSalesStore()
const purchasesApi = usePurchasesApi()
const { purchases } = storeToRefs(purchasesStore)
const { sales } = storeToRefs(salesStore)
const activeTab = useTypedState(Editor.ACTIVE_TAB)
const orderElement = useTypedState(TemplateElement.ORDER)
const insertState = useTypedState(Editor.INSERT_STATE)

const inDevelopment = () => {
  const toast = useToast()
  toast.add({
    title: 'Кнопка находиться в разработке...',
    icon: 'i-lucide-git-compare',
  })
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

    } else if (sales.value.goodsDeals && insert.salesGood) {
      if (salesStore.lastGoodsDeal) {
        orderDocxBlob = await generateDocxOrder(salesStore.lastGoodsDeal)
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

const counterpartData: CounterpartData | null = getCounterpartData(Number(route.query.dealId), route.query.role as 'buyer' | 'seller')

const saveChanges = async (): Promise<void> => {
  if (activeTab.value !== '0') return

  try {
    // Сначала создаем новую версию, чтобы исходная версия осталась нетронутой для reject.
    if (route.query.role === 'seller') {
      await salesStore.createNewDealVersion(Number(route.query.dealId), purchasesApi)
    } else if (route.query.role === 'buyer') {
      await purchasesStore.createNewDealVersion(Number(route.query.dealId), purchasesApi)
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
const isCancelChanges: Ref<{
  salesGood: boolean
  purchasesGood: boolean
}> = ref({
  salesGood: false,
  purchasesGood: false,
})

const cancelChanges = (activeTab: string) => {
  const role = route.query.role

  if (role === 'seller') {
    isCancelChanges.value.salesGood = !isCancelChanges.value.salesGood  
  } else if (role === 'buyer') {
    isCancelChanges.value.purchasesGood = !isCancelChanges.value.purchasesGood
  }
}

//подтверждение изменений при изменении заказа одной из сторон
const confirmation = ref(false)

watch(() => route.fullPath,
  () => {
    confirmation.value = route.query.confirmation === 'true' ? true : false
  }, { immediate: true, deep: true })

const confirm = () => {
  router.replace({ query: { ...route.query, confirmation: 'false' } })
  sendMessageToCounterpart(Number(route.query.dealId), route.query.role as 'buyer' | 'seller', counterpartData as CounterpartData, true) //true если изменения приняты

  useToast().add({
    title: 'Изменения приняты',
    color: 'success',
  })
}

const reject = async () => {
  router.replace({ query: { ...route.query, confirmation: 'false' } })
  sendMessageToCounterpart(Number(route.query.dealId), route.query.role as 'buyer' | 'seller', counterpartData as CounterpartData, false) //false если изменения отклонены
  const dealId = Number(route.query.dealId)

  if (dealId) {
    await purchasesApi.deleteLastDealVersion(dealId)
    await purchasesStore.getDeals(purchasesApi)
    await salesStore.getDeals(purchasesApi)
  }


  useToast().add({
    title: 'Изменения отклонены',
    color: 'warning',
  })
}

</script>