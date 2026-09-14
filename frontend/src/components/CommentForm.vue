<template>
  <form class="card p-5 space-y-4" @submit.prevent="submit">
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-bold text-brand">{{ parent ? 'Reply' : 'New comment' }}</h2>
      <slot name="target" />
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
      <label class="block">
        <span class="label">User Name</span>
        <input
          v-model="form.username" placeholder="latin letters and digits" pattern="[A-Za-z0-9]+"
          class="field" required
        />
      </label>
      <label class="block">
        <span class="label">E-mail</span>
        <input v-model="form.email" type="email" placeholder="you@example.com" class="field" required />
      </label>
      <label class="block md:col-span-2">
        <span class="label">Home page <span class="text-slate-400 font-normal">— optional</span></span>
        <input v-model="form.homepage" type="url" placeholder="https://" class="field" />
      </label>
    </div>

    <div>
      <div class="flex items-center justify-between mb-1">
        <span class="label mb-0">Text</span>
        <div class="flex gap-1">
          <button type="button" class="chip" @click="wrap('i')">[i]</button>
          <button type="button" class="chip" @click="wrap('strong')">[strong]</button>
          <button type="button" class="chip" @click="wrap('code')">[code]</button>
          <button type="button" class="chip" @click="insertLink">[a]</button>
        </div>
      </div>
      <textarea
        ref="area"
        v-model="form.text"
        rows="5"
        class="field font-mono text-sm resize-y"
        placeholder="Allowed tags: <a>, <code>, <i>, <strong>"
        required
      />
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
      <label class="block">
        <span class="label">CAPTCHA</span>
        <div class="flex items-center gap-2">
          <img v-if="captcha.image_url" :src="captcha.image_url" alt="captcha" class="h-10 rounded border border-slate-200" />
          <button type="button" class="icon-btn text-lg" title="another one" @click="loadCaptcha">⟳</button>
          <input v-model="form.captcha_value" placeholder="type the letters" class="field flex-1" required />
        </div>
      </label>
      <label class="block">
        <span class="label">Attachment <span class="text-slate-400 font-normal">— JPG, PNG, GIF or TXT</span></span>
        <input
          ref="fileInput"
          type="file"
          accept="image/jpeg,image/png,image/gif,.txt"
          class="w-full text-sm text-slate-500 file:mr-3 file:py-2 file:px-3 file:rounded-lg file:border-0
                 file:bg-slate-100 file:text-slate-700 file:font-medium hover:file:bg-slate-200"
          @change="onFile"
        />
        <span v-if="attached" class="text-xs text-slate-500">{{ attached.name }} · {{ Math.round(attached.size / 1024) }} KB</span>
      </label>
    </div>

    <div class="flex gap-2">
      <button type="submit" class="btn-primary">Send</button>
      <button type="button" class="btn-ghost" @click="preview">Preview</button>
    </div>

    <div v-if="previewHtml" class="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-4">
      <div class="label">Preview</div>
      <div class="text-sm text-slate-800 break-words" v-html="previewHtml" />
    </div>
    <p v-if="error" class="text-red-600 text-sm">{{ error }}</p>
  </form>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { createComment, previewComment, fetchCaptcha } from '../api'
import { resizeImage } from '../composables/useImageResize'
import { checkXhtml } from '../composables/useXhtml'
import { loadIdentity, saveIdentity } from '../composables/useIdentity'

const props = defineProps({ parent: { type: Number, default: null } })
const emit = defineEmits(['created'])

const known = ref(loadIdentity())
const form = reactive({
  username: known.value?.username || '',
  email: known.value?.email || '',
  homepage: known.value?.homepage || '',
  text: '',
  captcha_value: '',
})
const captcha = ref({ key: '', image_url: '' })
const previewHtml = ref('')
const error = ref('')
const area = ref(null)
const attached = ref(null)
const fileInput = ref(null)

onMounted(loadCaptcha)

async function loadCaptcha() {
  const { data } = await fetchCaptcha()
  captcha.value = data
}

function wrap(tag) {
  const el = area.value
  if (!el) return
  const [s, e] = [el.selectionStart, el.selectionEnd]
  const sel = form.text.slice(s, e)
  form.text = `${form.text.slice(0, s)}<${tag}>${sel}</${tag}>${form.text.slice(e)}`
}

function insertLink() {
  const url = prompt('URL:')
  if (!url) return
  const title = prompt('Title:') || ''
  form.text += `<a href="${url}" title="${title}">${url}</a>`
}

async function onFile(e) {
  error.value = ''
  attached.value = null
  const f = e.target.files[0]
  if (!f) return
  if (f.type === 'image/gif') {
    attached.value = f  // canvas would flatten it to a single JPEG frame; let the server scale it
  } else if (f.type.startsWith('image/')) {
    try {
      attached.value = await resizeImage(f)
    } catch {
      error.value = 'That file is not a readable image'
    }
  } else if (f.name.toLowerCase().endsWith('.txt') && f.size <= 100 * 1024) {
    attached.value = f
  } else {
    error.value = 'Only JPG, PNG, GIF and .txt up to 100 KB'
  }
}

function sameAsKnown() {
  const k = known.value
  return !!k && form.username === k.username && form.email === k.email
    && (form.homepage || '') === (k.homepage || '')
}

function clearFile() {
  attached.value = null
  if (fileInput.value) fileInput.value.value = ''
}

function focus() {
  area.value?.focus()
  area.value?.scrollIntoView({ behavior: 'smooth', block: 'center' })
}

function quote(comment) {
  const plain = new DOMParser().parseFromString(comment.text, 'text/html').body.textContent.trim()
  const short = plain.length > 120 ? `${plain.slice(0, 120)}…` : plain
  const escaped = short.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  form.text = `<i>${comment.author?.username}: ${escaped}</i>\n\n${form.text}`
  focus()
}

defineExpose({ focus, quote })

async function preview() {
  error.value = checkXhtml(form.text)
  if (error.value) return
  try {
    const { data } = await previewComment(form.text)
    previewHtml.value = data.html
  } catch (e) {
    error.value = e.response?.data?.detail || 'Preview failed'
  }
}

async function submit() {
  error.value = checkXhtml(form.text)
  if (error.value) return
  try {
    const payload = {
      parent: props.parent,
      text: form.text,
      captcha_key: captcha.value.key,
      captcha_value: form.captcha_value,
      file: attached.value,
    }
    // the signed identity replaces the fields while they stay as the server issued them
    if (sameAsKnown()) payload.identity = known.value.token
    else Object.assign(payload, {
      username: form.username,
      email: form.email,
      homepage: form.homepage || undefined,
    })
    const { data } = await createComment(payload)
    known.value = { token: data.identity, ...form }
    saveIdentity(data.identity, form)
    form.text = ''
    form.captcha_value = ''
    previewHtml.value = ''
    clearFile()
    await loadCaptcha()
    emit('created')
  } catch (e) {
    error.value = Object.values(e.response?.data || {}).flat().join(' ') || 'error'
    await loadCaptcha()
  }
}
</script>

<style scoped>
.label { @apply block text-xs font-semibold uppercase tracking-wide text-slate-500 mb-1; }
</style>
