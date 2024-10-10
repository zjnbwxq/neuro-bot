<template>
    <div class="login">
      <h2>{{ $t('login.title') }}</h2>
      <form @submit.prevent="login">
        <div>
          <label for="email">{{ $t('login.email') }}</label>
          <input type="email" id="email" v-model="email" required>
        </div>
        <div>
          <label for="password">{{ $t('login.password') }}</label>
          <input type="password" id="password" v-model="password" required>
        </div>
        <button type="submit">{{ $t('login.submit') }}</button>
      </form>
      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </template>
  
  <script>
  import api from '@/services/api';

  export default {
    name: 'LoginPage',
    data() {
      return {
        email: '',
        password: '',
        error: null
      }
    },
    methods: {
      async login() {
        try {
          console.log('Attempting to login with:', this.email); // 添加日志
          const result = await api.login(this.email, this.password);
          console.log('Login result:', result); // 添加日志
          this.$router.push('/user-center');
        } catch (error) {
          console.error('Login error:', error); // 添加详细的错误日志
          this.error = error.message || '登录失败，请重试';
        }
      }
    }
  }
  </script>