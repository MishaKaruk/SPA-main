const MAX_W = 320
const MAX_H = 240

export function resizeImage(file) {
  return new Promise((resolve, reject) => {
    const img = new Image()
    const reader = new FileReader()
    reader.onerror = reject
    img.onerror = () => reject(new Error('cannot decode the image'))
    reader.onload = (e) => (img.src = e.target.result)
    img.onload = () => {
      const scale = Math.min(MAX_W / img.width, MAX_H / img.height, 1)
      const w = Math.round(img.width * scale)
      const h = Math.round(img.height * scale)
      const c = document.createElement('canvas')
      c.width = w
      c.height = h
      c.getContext('2d').drawImage(img, 0, 0, w, h)
      const type = file.type === 'image/png' ? 'image/png' : 'image/jpeg'
      c.toBlob((blob) => resolve(new File([blob], file.name, { type: blob.type })), type, 0.9)
    }
    reader.readAsDataURL(file)
  })
}
