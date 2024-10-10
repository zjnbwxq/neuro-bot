import { createI18n } from 'vue-i18n';
import zh from './locales/zh.json';
import zhTW from './locales/zh-TW.json';
import en from './locales/en.json';

const i18n = createI18n({
  legacy: false, // 使用 Composition API 模式
  locale: 'zh', // 设置默认语言
  fallbackLocale: 'en', // 设置回退语言
  messages: {
    zh,
    'zh-TW': zhTW,
    en
  }
});

export default i18n;