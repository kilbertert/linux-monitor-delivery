import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from './views/Dashboard.vue'
import History from './views/History.vue'
import './style.css'
import App from './App.vue'

const routes = [
  { path: '/', component: Dashboard },
  { path: '/history', component: History }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const app = createApp(App)
app.use(router)
app.mount('#app')
