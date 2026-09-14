<template>
  <div :id="`c${comment.id}`" class="card overflow-hidden">
    <div class="flex items-center gap-3 bg-slate-50 border-b border-slate-100 px-4 py-2">
      <span
        class="w-9 h-9 rounded-full text-white text-xs font-bold flex items-center justify-center shrink-0"
        :style="{ backgroundColor: avatarColor }"
      >{{ initials }}</span>
      <span class="font-bold text-brand">{{ comment.author?.username || 'Anonym' }}</span>
      <span class="text-sm text-slate-400">{{ when }}</span>
      <div class="flex items-center gap-2 text-sm">
        <a :href="`#c${comment.id}`" class="icon-btn" title="link to this comment">#</a>
        <button class="icon-btn" title="quote" @click="$emit('quote', comment)">ђ</button>
        <a v-if="comment.parent" :href="`#c${comment.parent}`" class="icon-btn" title="go to parent">↑</a>
      </div>
      <button
        class="ml-auto text-xs font-medium text-brand hover:underline"
        @click="$emit('reply', comment)"
      >Reply</button>
    </div>

    <div class="px-4 py-3 space-y-3">
      <div class="text-slate-800 text-sm break-words leading-relaxed" v-html="comment.text" />
      <div v-if="comment.attachments?.length" class="flex gap-2 flex-wrap items-center">
        <img
          v-for="(a, i) in images"
          :key="a.id"
          :src="a.url"
          :alt="a.original_name"
          class="h-24 rounded-lg border border-slate-200 cursor-zoom-in hover:opacity-90 transition"
          @click="open(i)"
        />
        <a
          v-for="a in texts"
          :key="a.id"
          :href="a.url"
          target="_blank"
          class="px-2 py-1 rounded-md bg-slate-100 text-brand text-xs hover:bg-slate-200 transition"
        >{{ a.original_name || 'text file' }}</a>
      </div>
      <VueEasyLightbox :visible="viewer" :imgs="images.map((a) => a.url)" :index="index" @hide="viewer = false" />
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import VueEasyLightbox from 'vue-easy-lightbox'
import { formatDate } from '../composables/useDate'

const props = defineProps({ comment: { type: Object, required: true } })
defineEmits(['reply', 'quote'])

const viewer = ref(false)
const index = ref(0)
const images = computed(() => (props.comment.attachments || []).filter((a) => a.kind === 'image'))
const texts = computed(() => (props.comment.attachments || []).filter((a) => a.kind === 'text'))

function open(i) {
  index.value = i
  viewer.value = true
}

const name = computed(() => props.comment.author?.username || 'A')
const initials = computed(() => name.value.slice(0, 2).toUpperCase())
const when = computed(() => formatDate(props.comment.created_at))

// stable colour per author, so the same person keeps the same avatar across the thread
const avatarColor = computed(() => {
  let h = 0
  for (const ch of name.value) h = (h * 31 + ch.charCodeAt(0)) % 360
  return `hsl(${h}, 45%, 45%)`
})
</script>
