<template>
  <div class="card overflow-x-auto">
    <table class="w-full min-w-[36rem] text-sm">
      <thead>
        <tr class="bg-slate-50 text-slate-500 text-xs uppercase tracking-wide">
          <th v-for="col in columns" :key="col.field" class="p-3 text-left">
            <button class="flex items-center gap-1 hover:text-brand transition" @click="$emit('sort', col.field)">
              {{ col.label }}
              <span :class="active(col.field) ? 'text-brand' : 'text-slate-300'">{{ arrow(col.field) }}</span>
            </button>
          </th>
          <th class="p-3 text-left">Text</th>
          <th class="p-3"></th>
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-100">
        <tr v-for="c in roots" :key="c.id" class="hover:bg-slate-50 transition">
          <td class="p-3">
            <div class="flex items-center gap-2">
              <span class="w-7 h-7 rounded-full bg-slate-200 text-slate-600 text-xs font-bold flex items-center justify-center shrink-0">
                {{ (c.author?.username || 'A').slice(0, 2).toUpperCase() }}
              </span>
              <span class="font-medium text-brand">{{ c.author?.username || '—' }}</span>
            </div>
          </td>
          <td class="p-3 text-slate-500">{{ c.author?.email || '—' }}</td>
          <td class="p-3 text-slate-500 whitespace-nowrap">{{ when(c.created_at) }}</td>
          <td class="p-3 text-slate-700 truncate max-w-xs" v-html="c.text" />
          <td class="p-3 text-right">
            <RouterLink
              :to="{ name: 'thread', params: { id: c.id } }"
              class="px-3 py-1 rounded-md bg-slate-100 text-brand text-xs font-medium hover:bg-brand hover:text-white transition whitespace-nowrap"
            >{{ replies(c) }}</RouterLink>
          </td>
        </tr>
        <tr v-if="!roots.length">
          <td colspan="5" class="p-8 text-center text-slate-400">No comments yet.</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import { formatDate } from '../composables/useDate'

const props = defineProps({
  roots: { type: Array, required: true },
  ordering: { type: String, default: '-created_at' },
})
defineEmits(['sort'])

const columns = [
  { field: 'author_name', label: 'User Name' },
  { field: 'author_email', label: 'E-mail' },
  { field: 'created_at', label: 'Date' },
]

const replies = (c) => (c.children_count ? `${c.children_count} ${c.children_count === 1 ? 'reply' : 'replies'}` : 'open')
const active = (field) => props.ordering.replace('-', '') === field
const arrow = (field) => (active(field) ? (props.ordering.startsWith('-') ? '↓' : '↑') : '↕')
const when = formatDate
</script>
