declare module 'vue-document-editor' {
  import type { DefineComponent } from 'vue'

  const VueDocumentEditor: DefineComponent<{
    content?: unknown[]
    display?: string
    editable?: boolean
    overlay?: (pageNum: number, totalPages: number) => string
    page_format_mm?: [number, number]
    page_margins?: string | ((pageIdx: number) => string)
    zoom?: number
    do_not_break?: (element: Element) => boolean
  }>

  export default VueDocumentEditor
}
