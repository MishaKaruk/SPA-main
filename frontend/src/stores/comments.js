import { defineStore } from 'pinia'
import { listRoots } from '../api'

export const useCommentsStore = defineStore('comments', {
  state: () => ({
    roots: [],
    count: 0,
    page: 1,
    ordering: '-created_at',
    loading: false,
  }),
  actions: {
    async fetchRoots() {
      this.loading = true
      try {
        const { data } = await listRoots({ page: this.page, ordering: this.ordering })
        this.roots = data.results
        this.count = data.count
      } finally {
        this.loading = false
      }
    },
    setOrdering(field) {
      this.ordering = this.ordering === field ? `-${field}` : field
      this.page = 1
      return this.fetchRoots()
    },
    setPage(page) {
      this.page = page
      return this.fetchRoots()
    },
    prependComment(comment) {
      if (!comment.parent) this.roots.unshift(comment)
    },
  },
})
