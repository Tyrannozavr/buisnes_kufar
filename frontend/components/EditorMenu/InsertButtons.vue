<script setup lang="ts">
import { useInsertState, useIsDisableState} from '~/composables/useStates';

const { activeButtons, isCancelChanges } = defineProps<{
  activeButtons: boolean
  isCancelChanges: {
    sales: boolean
    purchases: boolean
  }
}>()

const { statePurchasesGood, stateSalesGood } = useInsertState()
const { doubleReversDisable } = useIsDisableState()

const insertLastPurchasesGood = (): void => {
  statePurchasesGood(true)
  doubleReversDisable()
}

const insertLastSalesGood = (): void => {
  stateSalesGood(true)
  doubleReversDisable()
}

watch(() => isCancelChanges,
  () => {
    if (isCancelChanges.sales) {
      insertLastSalesGood()
    }
    if (isCancelChanges.purchases) {
      insertLastPurchasesGood()
    }
  }, { deep: true }
)
</script>

<template>
  <div class="w-full">
    <UCollapsible>
      <UButton label="Заполнить данными" icon="i-lucide-file-input" class="w-full justify-center"
        :disabled="activeButtons" />

      <template #content>
        <div class="flex gap-2 mt-4 justify-center">
          <div class="w-1/2">
            <UButton label="Последняя закупка" color="neutral" variant="subtle" class="w-full justify-center py-2"
              @click="insertLastPurchasesGood" />
          </div>
          <div class="w-1/2">
            <UButton label="Последняя продажа" color="neutral" variant="subtle" class="w-full justify-center py-2"
              @click="insertLastSalesGood" />
          </div>
        </div>
      </template>
    </UCollapsible>
  </div>
</template>