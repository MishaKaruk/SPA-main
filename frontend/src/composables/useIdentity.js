const KEY = 'identity'

// the server signs who you are after the first comment; keeping it saves retyping the form
export function loadIdentity() {
  try {
    return JSON.parse(localStorage.getItem(KEY)) || null
  } catch {
    return null
  }
}

export function saveIdentity(token, { username, email, homepage }) {
  localStorage.setItem(KEY, JSON.stringify({ token, username, email, homepage }))
}
