import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ThreadView from '../views/ThreadView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/thread/:id', name: 'thread', component: ThreadView, props: true },
  ],
})

export default router
