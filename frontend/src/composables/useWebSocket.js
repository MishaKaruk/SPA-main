import { onMounted, onBeforeUnmount } from 'vue'

export function useCommentsSocket(onEvent, threadId = null) {
  const base = import.meta.env.VITE_WS_URL || `ws://${location.host}/ws`
  const url = threadId ? `${base}/comments/${threadId}/` : `${base}/comments/`
  let socket = null

  onMounted(() => {
    socket = new WebSocket(url)
    socket.onmessage = (m) => {
      try { onEvent(JSON.parse(m.data)) } catch {}
    }
  })

  onBeforeUnmount(() => socket?.close())
}
