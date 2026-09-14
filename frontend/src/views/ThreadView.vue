<template>
  <div class="space-y-6">
    <RouterLink to="/" class="inline-flex items-center gap-1 text-sm text-brand hover:underline">← back to all comments</RouterLink>
    <div v-if="loading" class="text-slate-400">Loading…</div>
    <CommentTree v-else-if="root" :nodes="[root]" :flat="nodes" @reply="setTarget" @quote="addQuote" />
    <CommentForm ref="form" :parent="target?.id || null" @created="reload" @cancel="target = null">
      <template #target>
        <p v-if="target" class="text-sm px-3 py-1 rounded-full bg-slate-100 text-slate-600">
          replying to <b class="text-brand">{{ target.author?.username }}</b>
          <button type="button" class="ml-2 icon-btn underline" @click="target = null">cancel</button>
        </p>
      </template>
    </CommentForm>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { getTree } from '../api'
import CommentTree from '../components/CommentTree.vue'
import CommentForm from '../components/CommentForm.vue'

const route = useRoute()
const nodes = ref([])
const loading = ref(true)
const target = ref(null)
const root = computed(() => nodes.value.find((n) => !n.parent))
const form = ref(null)

async function reload() {
  const { data } = await getTree(route.params.id)
  nodes.value = data
  loading.value = false
  target.value = null
}

function setTarget(comment) {
  target.value = comment
  form.value?.focus()
}

function addQuote(comment) {
  target.value = comment
  form.value?.quote(comment)
}

onMounted(reload)
</script>
