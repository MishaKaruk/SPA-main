<template>
  <div class="space-y-3">
    <div v-for="node in nodes" :key="node.id">
      <CommentCard :comment="node" @reply="$emit('reply', $event)" @quote="$emit('quote', $event)" />
      <div v-if="childrenOf(node).length" class="ml-6 md:ml-10 mt-3 border-l-2 border-slate-200 pl-4">
        <CommentTree
          :nodes="childrenOf(node)"
          :flat="flat"
          @reply="$emit('reply', $event)"
          @quote="$emit('quote', $event)"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import CommentCard from './CommentCard.vue'

const props = defineProps({
  nodes: { type: Array, required: true },
  flat: { type: Array, default: null },
})
defineEmits(['reply', 'quote'])

function childrenOf(node) {
  if (!props.flat) return node.children || []
  return props.flat.filter((n) => n.parent === node.id)
}
</script>
