import { createRouter, createWebHistory } from 'vue-router';
import GameDetails from '@/views/GameDetails.vue';
import PrivacyPolicy from '@/views/PrivacyPolicy.vue';
import RegisterPage from '@/views/Register.vue'; // 更新这里
import LoginPage from '@/views/Login.vue'; // 更新这里
import UserCenterPage from '@/views/UserCenter.vue';

const routes = [
  {
    path: '/',
    redirect: '/game-details'
  },
  {
    path: '/game-details',
    name: 'GameDetails',
    component: GameDetails
  },
  {
    path: '/privacy-policy',
    name: 'PrivacyPolicy',
    component: PrivacyPolicy
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterPage // 更新这里
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage // 更新这里
  },
  {
    path: '/user-center',
    name: 'UserCenter',
    component: UserCenterPage
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL), // 修改这里
  routes
});

export default router;