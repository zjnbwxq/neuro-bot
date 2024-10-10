<template>
  <div class="user-center">
    <h2>{{ $t('userCenter.title') }}</h2>
    <p v-if="user">{{ $t('userCenter.welcome', { email: user.email }) }}</p>
    <p v-else>{{ $t('userCenter.loading') }}</p>
  </div>
</template>

<script>
import api from '@/services/api';

export default {
  name: 'UserCenterPage',
  data() {
    return {
      user: null
    }
  },
  async created() {
    try {
      this.user = await api.getUserProfile();
    } catch (error) {
      console.error('Failed to load user profile:', error);
      // 可以在这里处理错误，比如重定向到登录页面
    }
  }
}
</script>
