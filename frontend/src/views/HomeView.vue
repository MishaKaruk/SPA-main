<template>
  <div class="space-y-6">
    <CommentForm @created="store.fetchRoots" />

    <div class="flex items-baseline justify-between">
      <h2 class="text-lg font-bold text-brand">Comments</h2>
      <span class="text-sm text-slate-500">{{ store.count }} total</span>
    </div>

    <CommentTable :roots="store.roots" :ordering="store.ordering" @sort="store.setOrdering" />

    <nav v-if="pages > 1" class="flex gap-1 justify-center">
      <button class="page" :disabled="store.page === 1" @click="store.setPage(store.page - 1)">←</button>
      <button
        v-for="p in pages"
        :key="p"
        class="page"
        :class="p === store.page ? 'bg-brand text-white border-brand' : 'text-brand'"
        @click="store.setPage(p)"
      >{{ p }}</button>
      <button class="page" :disabled="store.page === pages" @click="store.setPage(store.page + 1)">→</button>
    </nav>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useCommentsStore } from '../stores/comments'
import { useCommentsSocket } from '../composables/useWebSocket'
import CommentForm from '../components/CommentForm.vue'
import CommentTable from '../components/CommentTable.vue'

const store = useCommentsStore()
const pages = computed(() => Math.max(1, Math.ceil(store.count / 25)))

onMounted(store.fetchRoots)
useCommentsSocket((e) => e.event === 'comment.created' && store.prependComment(e.payload))
</script>

<style scoped>
.page {
  @apply px-3 py-1 rounded-md bg-white border border-slate-200 text-sm transition
         hover:border-brand disabled:opacity-40 disabled:hover:border-slate-200;
}
</style>
