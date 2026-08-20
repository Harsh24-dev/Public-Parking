import { createRouter, createWebHistory } from 'vue-router'
import Home from '../components/Home.vue'
import Login from '../components/Login.vue'
import Register from '../components/Register.vue'
import AdminDashboard from '../components/AdminDashboard.vue';
import AdminUser from '../components/AdminUser.vue';
import AddLot from '../components/AddLot.vue';
import AdminSummary from '../components/AdminSummary.vue';
import AdminSearch from '../components/AdminSearch.vue';
import UserDashboard from '../components/UserDashboard.vue';
import UserParkHistory from '../components/UserParkHistory.vue';
import UserSummary from '../components/UserSummary.vue';


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home,
    },
    {
      path:'/login',
      name:'Login',
      component: Login,
    },
    {
      path:'/register',
      name:'Register',
      component: Register,
    },
    {
      path: '/admin_dashboard',
      name: 'AdminDashboard',
      component: AdminDashboard,
    },
    {
      path: '/admin_user',
      name: 'AdminUser',
      component: AdminUser,
    },
    {
      path: '/add_lot',
      name: 'AddLot',
      component: AddLot,
    },
    {
      path: '/admin_summary',
      name: 'AdminSummary',
      component: AdminSummary,
    },
    {
      path: '/admin_search',
      name:'AdminSearch',
      component: AdminSearch,
    },
    {
      path: '/user_dashboard',
      name: 'UserDashboard',
      component: UserDashboard,
    },
    {
      path: '/user_park_history',
      name: 'UserParkHistory',
      component: UserParkHistory,
    },
    {
      path: '/user_summary',
      name: 'UserSummary',
      component: UserSummary,
    },
  ]
})

export default router
