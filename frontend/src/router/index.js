import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/RegisterView.vue')
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue')
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('../views/Search.vue')
  },
  {
    path: '/stock/:code',
    name: 'StockDetail',
    component: () => import('../views/StockDetail.vue')
  },
  {
    path: '/watchlist',
    name: 'Watchlist',
    component: () => import('../views/Watchlist.vue')
  },
  {
    path: '/ipo',
    name: 'IPO',
    component: () => import('../views/IPO.vue')
  },
  {
    path: '/calendar',
    name: 'Calendar',
    component: () => import('../views/Calendar.vue')
  },
  {
    path: '/alerts',
    name: 'Alerts',
    component: () => import('../views/Alerts.vue')
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 检查登录状态
router.beforeEach((to, from, next) => {
  const token = sessionStorage.getItem('token')
  
  // 不需要登录的页面
  const publicPages = ['/login', '/register']
  
  if (!token && !publicPages.includes(to.path)) {
    // 未登录，跳转登录页
    next('/login')
  } else if (token && publicPages.includes(to.path)) {
    // 已登录，跳转首页
    next('/')
  } else {
    next()
  }
})

export default router
