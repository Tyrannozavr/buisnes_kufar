<script setup lang="ts">
import { useDocumentsApi } from '~/api/documents';
import type { DocumentDownloadResponse } from '~/types/documents';

const props = defineProps<{ 
  isModalOpen: boolean
  name?: string
  type?: string
  dealId: number
  documentId: number
}>()

defineEmits<{
  (e: 'close'): void
}>()

const isModalOpen = computed(() => props.isModalOpen)
const { downloadDocument } = useDocumentsApi()
const url = ref<string | undefined>(undefined)

watch(() => props,
  async () => {
  const response = await downloadDocument(props.dealId, props.documentId, false) as unknown as DocumentDownloadResponse
  url.value = response?.url
}, { deep: true })

</script>
  <template>
    <div v-if="url">
    <UModal fullscreen v-model:open="isModalOpen" size="4xl" class="">
      <template #header>
        <div class="flex items-center justify-between w-full">
          <h3 class="text-xl font-semibold">Просмотр документа: {{ name }}</h3>
          <UButton
            color="neutral"
            variant="ghost"
            icon="i-heroicons-x-mark"
            @click="$emit('close')"
          />
        </div>
      </template>

      <template #body>
        <div v-if="type === 'pdf'" class="h-[80vh] min-h-0 overflow-hidden flex flex-col">
          <iframe :src="url" class="w-full flex-1 min-h-0 border-0" />
        </div>

        <div v-else-if="type === 'jpeg' || type === 'jpg' || type === 'png'">
          <img :src="url" :alt="name">
        </div>
      </template>
    </UModal>
  </div>
</template>