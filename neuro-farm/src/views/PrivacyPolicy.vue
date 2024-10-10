<template>
    <div class="privacy-policy">
      <h1>{{ $t('privacyPolicy.title') }}</h1>
      <p>{{ $t('privacyPolicy.description') }}</p>
    </div>
  </template>
  
  <script>
  export default {
    name: 'PrivacyPolicy',
  };
  </script>
  
  <style scoped>
  .privacy-policy {
    padding: 20px;
    /* 在这里添加你的样式 */
  }
  </style>