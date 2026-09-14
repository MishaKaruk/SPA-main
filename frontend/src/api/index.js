import axios from 'axios'

const baseURL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({ baseURL })

export const listRoots = (params) => api.get('/comments/', { params })
export const getTree = (id) => api.get(`/comments/${id}/tree/`)
export const createComment = ({ file, ...payload }) => {
  if (!file) return api.post('/comments/', payload)
  const fd = new FormData()
  Object.entries({ ...payload, file }).forEach(([k, v]) => v != null && fd.append(k, v))
  return api.post('/comments/', fd)
}
export const previewComment = (text) => api.post('/comments-preview/', { text })
export const fetchCaptcha = () => api.get('/captcha/')

export default api
