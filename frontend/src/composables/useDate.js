const pad = (n) => String(n).padStart(2, '0')

export function formatDate(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return `${pad(d.getDate())}.${pad(d.getMonth() + 1)}.${String(d.getFullYear()).slice(-2)} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}
