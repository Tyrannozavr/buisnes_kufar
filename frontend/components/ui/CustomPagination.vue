<template>
  <nav class="flex items-center justify-center gap-1" aria-label="Pagination">
    <!-- First Page -->
    <button
      @click="$emit('update:page', 1)"
      :disabled="currentPage === 1"
      class="rounded-md font-medium inline-flex items-center disabled:cursor-not-allowed aria-disabled:cursor-not-allowed disabled:opacity-75 aria-disabled:opacity-75 transition-colors text-sm gap-1.5 ring ring-inset ring-accented text-default bg-default hover:bg-elevated active:bg-elevated disabled:bg-default aria-disabled:bg-default focus:outline-none focus-visible:ring-2 focus-visible:ring-inverted p-1.5"
    >
      <span class="sr-only">Первая страница</span>
      <Icon name="i-lucide:chevrons-left" class="shrink-0 size-5" />
    </button>

    <!-- Previous Page -->
    <button
      @click="$emit('update:page', currentPage - 1)"
      :disabled="currentPage === 1"
      class="rounded-md font-medium inline-flex items-center disabled:cursor-not-allowed aria-disabled:cursor-not-allowed disabled:opacity-75 aria-disabled:opacity-75 transition-colors text-sm gap-1.5 ring ring-inset ring-accented text-default bg-default hover:bg-elevated active:bg-elevated disabled:bg-default aria-disabled:bg-default focus:outline-none focus-visible:ring-2 focus-visible:ring-inverted p-1.5"
    >
      <span class="sr-only">Предыдущая страница</span>
      <Icon name="i-lucide:chevron-left" class="shrink-0 size-5" />
    </button>

    <!-- Page Numbers -->
    <template v-for="page in visiblePages" :key="page">
      <button
        v-if="page !== '...'"
        @click="$emit('update:page', page)"
        class="rounded-md font-medium inline-flex items-center disabled:cursor-not-allowed aria-disabled:cursor-not-allowed disabled:opacity-75 aria-disabled:opacity-75 transition-colors text-sm gap-1.5 p-1.5"
        :class="page === currentPage 
          ? 'text-inverted bg-primary hover:bg-primary/75 active:bg-primary/75 disabled:bg-primary aria-disabled:bg-primary focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary' 
          : 'ring ring-inset ring-accented text-default bg-default hover:bg-elevated active:bg-elevated disabled:bg-default aria-disabled:bg-default focus:outline-none focus-visible:ring-2 focus-visible:ring-inverted'"
      >
        <span class="truncate min-w-5 text-center">{{ page }}</span>
      </button>
      <span
        v-else
        class="rounded-md font-medium inline-flex items-center text-sm gap-1.5 ring ring-inset ring-accented text-default bg-default p-1.5"
      >
        <span class="truncate min-w-5 text-center">...</span>
      </span>
    </template>

    <!-- Next Page -->
    <button
      @click="$emit('update:page', currentPage + 1)"
      :disabled="currentPage === totalPages"
      class="rounded-md font-medium inline-flex items-center disabled:cursor-not-allowed aria-disabled:cursor-not-allowed disabled:opacity-75 aria-disabled:opacity-75 transition-colors text-sm gap-1.5 ring ring-inset ring-accented text-default bg-default hover:bg-elevated active:bg-elevated disabled:bg-default aria-disabled:bg-default focus:outline-none focus-visible:ring-2 focus-visible:ring-inverted p-1.5"
    >
      <span class="sr-only">Следующая страница</span>
      <Icon name="i-lucide:chevron-right" class="shrink-0 size-5" />
    </button>

    <!-- Last Page -->
    <button
      @click="$emit('update:page', totalPages)"
      :disabled="currentPage === totalPages"
      class="rounded-md font-medium inline-flex items-center disabled:cursor-not-allowed aria-disabled:cursor-not-allowed disabled:opacity-75 aria-disabled:opacity-75 transition-colors text-sm gap-1.5 ring ring-inset ring-accented text-default bg-default hover:bg-elevated active:bg-elevated disabled:bg-default aria-disabled:bg-default focus:outline-none focus-visible:ring-2 focus-visible:ring-inverted p-1.5"
    >
      <span class="sr-only">Последняя страница</span>
      <Icon name="i-lucide:chevrons-right" class="shrink-0 size-5" />
    </button>
  </nav>
</template>

<script setup lang="ts">
interface Props {
  currentPage: number
  total: number
  perPage: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:page': [page: number]
}>()

const totalPages = computed(() => Math.ceil(props.total / props.perPage))

const visiblePages = computed(() => {
  const pages: (number | string)[] = []
  const current = props.currentPage
  const total = totalPages.value
  
  if (total <= 7) {
    // Если страниц мало, показываем все
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    // Показываем первую страницу
    pages.push(1)
    
    if (current <= 4) {
      // Если текущая страница в начале
      for (let i = 2; i <= Math.min(5, total - 1); i++) {
        pages.push(i)
      }
      if (total > 5) {
        pages.push('...')
        pages.push(total)
      }
    } else if (current >= total - 3) {
      // Если текущая страница в конце
      pages.push('...')
      for (let i = Math.max(total - 4, 2); i <= total; i++) {
        pages.push(i)
      }
    } else {
      // Если текущая страница в середине
      pages.push('...')
      for (let i = current - 1; i <= current + 1; i++) {
        pages.push(i)
      }
      pages.push('...')
      pages.push(total)
    }
  }
  
  return pages
})
</script>
