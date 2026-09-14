const ALLOWED = ['a', 'code', 'i', 'strong']
const ATTRS = { a: ['href', 'title'] }

// mirrors the server check so the user does not need a round trip to see a broken tag
export function checkXhtml(text) {
  const doc = new DOMParser().parseFromString(`<comment>${text}</comment>`, 'application/xml')
  if (doc.querySelector('parsererror')) return 'Not valid XHTML — check that every tag is closed'
  for (const el of doc.documentElement.querySelectorAll('*')) {
    const tag = el.tagName.toLowerCase()
    if (!ALLOWED.includes(tag)) return `<${tag}> is not an allowed tag`
    const extra = [...el.attributes].map((a) => a.name).filter((n) => !(ATTRS[tag] || []).includes(n))
    if (extra.length) return `<${tag}> must not carry ${extra.join(', ')}`
    const scheme = (el.getAttribute('href') || '').match(/^([a-z][a-z0-9+.-]*):/i)
    if (scheme && !['http', 'https'].includes(scheme[1].toLowerCase())) {
      return `${scheme[1]}: links are not allowed`
    }
  }
  return ''
}
