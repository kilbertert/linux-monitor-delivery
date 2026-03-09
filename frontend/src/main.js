import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from './views/Dashboard.vue'
import History from './views/History.vue'
import Processes from './views/Processes.vue'
import Alerts from './views/Alerts.vue'
import Export from './views/Export.vue'
import './style.css'
import App from './App.vue'

const routes = [
  { path: '/', component: Dashboard },
  { path: '/history', component: History },
  { path: '/processes', component: Processes },
  { path: '/alerts', component: Alerts },
  { path: '/export', component: Export }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const app = createApp(App)
app.use(router)
app.mount('#app')
