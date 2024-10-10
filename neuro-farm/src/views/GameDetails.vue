<template>
    <div class="game-details">
      <h1>{{ $t('gameDetails.title') }}</h1>
      <p>{{ $t('gameDetails.description') }}</p>
    </div>
  </template>
  
  <script>
  export default {
    name: 'GameDetails',
  };
  </script>
  
  <style scoped>
  .game-details {
    padding: 20px;
    /* 在这里添加你的样式 */
  }
  </style>