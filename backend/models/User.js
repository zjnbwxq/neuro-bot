const { DataTypes } = require('sequelize');
const sequelize = require('../config/database'); // 假设您有一个数据库配置文件

const User = sequelize.define('User', {
  email: {
    type: DataTypes.STRING,
    allowNull: false,
    unique: true,
    validate: {
      isEmail: true
    }
  },
  password: {
    type: DataTypes.STRING,
    allowNull: false
  }
});

module.exports = User;
