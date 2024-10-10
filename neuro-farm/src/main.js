import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import i18n from './i18n';
import { setAuthToken } from './services/api';
import axios from 'axios';

// 从本地存储中恢复 token
const token = localStorage.getItem('token');
if (token) {
  setAuthToken(token);
}

axios.defaults.baseURL = process.env.VUE_APP_API_URL || 'http://localhost:3000/api';

const app = createApp(App);
app.use(router);
app.use(i18n);
app.mount('#app');