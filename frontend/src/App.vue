<template>
  <div class="max-w-4xl mx-auto px-4 py-8">
    <header class="mb-6 flex items-center gap-3">
      <div class="bg-accent w-12 h-12 rounded-lg flex items-center justify-center font-bold text-brand text-lg shadow-sm">
        dZ
      </div>
      <div>
        <h1 class="text-2xl font-bold text-brand leading-tight">SPA Comments</h1>
        <p class="text-sm text-slate-500">Leave a comment, reply to any of them.</p>
      </div>
    </header>
    <RouterView />
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'
</script>
