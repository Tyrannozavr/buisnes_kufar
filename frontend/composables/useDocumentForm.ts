/**
 * Композабл для загрузки/сохранения формы документа по сделке (API документов).
 * Используется в шаблонах редактора: при наличии deal_id в route — GET при монтировании, save() по кнопке «Сохранить».
 * Сергей: payload — произвольный объект формы; при открытии с deal_id подставляйте payload в форму.
 */
import type { Ref } from 'vue'
import { ref, watch } from 'vue'
import { SLOT_TO_DOCUMENT_TYPE, useDocumentsApi } from '~/api/documents'
import type { DocumentType } from '~/api/documents'

export interface UseDocumentFormOptions {
  /** Слот вкладки (order, bill, supplyContract, …) для маппинга в document_type. */
  slot: keyof typeof SLOT_TO_DOCUMENT_TYPE
  /** deal_id из route (query или param). Если нет — загрузка/сохранение не выполняются. */
  dealId: Ref<number | null | undefined>
  /** Начальное значение payload, пока не загружено с сервера. */
  initialPayload?: Record<string, unknown>
}

export function useDocumentForm(options: UseDocumentFormOptions) {
  const { slot, dealId, initialPayload = {} } = options
  const documentType = SLOT_TO_DOCUMENT_TYPE[slot] as DocumentType
  const { getDocument, saveDocument } = useDocumentsApi()

  const payload: Ref<Record<string, unknown>> = ref({ ...initialPayload })
  const loading = ref(false)
  const saving = ref(false)
  const error = ref<string | null>(null)
  /** Для диалога «Контрагент изменил данные»: если !== company_id текущего юзера и updated_at новее lastSeen — показать «Обновить?» */
  const updatedByCompanyId = ref<number | null>(null)
  const updatedAt = ref<string | null>(null)

  async function load() {
    const id = dealId.value
    if (id == null || id === undefined) return
    loading.value = true
    error.value = null
    try {
      const res = await getDocument(id, documentType)
      const fromServer = res.payload && Object.keys(res.payload).length ? res.payload : {}
      payload.value = { ...initialPayload, ...fromServer }
      updatedByCompanyId.value = res.updated_by_company_id ?? null
      updatedAt.value = res.updated_at ?? null
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e)
      error.value = msg
    } finally {
      loading.value = false
    }
  }

  async function save(version?: string) {
    const id = dealId.value
    if (id == null || id === undefined) return
    saving.value = true
    error.value = null
    try {
      const res = await saveDocument(id, documentType, payload.value, version)
      updatedByCompanyId.value = res.updated_by_company_id ?? null
      updatedAt.value = res.updated_at ?? null
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e)
      error.value = msg
    } finally {
      saving.value = false
    }
  }

  watch(dealId, (id) => {
    if (id != null) load()
  }, { immediate: true })

  return {
    payload,
    loading,
    saving,
    error,
    updatedByCompanyId,
    updatedAt,
    load,
    save,
    documentType,
  }
}
