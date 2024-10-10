require('dotenv').config();

module.exports = {
  jwtSecret: process.env.JWT_SECRET || 'development_secret',
  // 其他配置项...
};
