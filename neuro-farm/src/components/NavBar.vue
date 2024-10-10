<template>
    <nav>
      <ul>
        <li><router-link :to="{ name: 'GameDetails' }">{{ $t('nav.gameDetails') }}</router-link></li>
        <li><router-link :to="{ name: 'PrivacyPolicy' }">{{ $t('nav.privacyPolicy') }}</router-link></li>
        <li><router-link :to="{ name: 'Register' }">{{ $t('nav.register') }}</router-link></li>
        <li><router-link :to="{ name: 'Login' }">{{ $t('nav.login') }}</router-link></li>
      </ul>
      <select v-model="$i18n.locale">
        <option value="zh">简体中文</option>
        <option value="zh-TW">繁體中文</option>
        <option value="en">English</option>
      </select>
    </nav>
  </template>
  
  <script>
  export default {
    name: 'NavBar',
  };
  </script>
  
  <style scoped>
  nav {
    background-color: #333;
    padding: 10px;
  }
  
  ul {
    list-style: none;
    display: flex;
  }
  
  li {
    margin-right: 15px;
  }
  
  a {
    color: #fff;
    text-decoration: none;
  }
  
  a.router-link-active {
    font-weight: bold;
  }
  
  select {
    margin-left: 15px;
  }
  </style>