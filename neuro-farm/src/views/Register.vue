<template>
    <div class="register">
      <h2>{{ $t('register.title') }}</h2>
      <form @submit.prevent="register">
        <div>
          <label for="email">{{ $t('register.email') }}</label>
          <input type="email" id="email" v-model="email" required>
        </div>
        <div>
          <label for="password">{{ $t('register.password') }}</label>
          <input type="password" id="password" v-model="password" required>
        </div>
        <button type="submit">{{ $t('register.submit') }}</button>
      </form>
      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </template>
  
  <script>
  import api from '@/services/api';

  export default {
    name: 'RegisterPage',
    data() {
      return {
        email: '',
        password: '',
        error: null
      }
    },
    methods: {
      async register() {
        try {
          await api.register(this.email, this.password);
          this.$router.push('/login');
        } catch (error) {
          this.error = error.message || '注册失败，请重试';
        }
      }
    }
  }
  </script>