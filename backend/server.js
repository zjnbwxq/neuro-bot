require('dotenv').config();

const express = require('express');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { User } = require('./models'); // 假设您有一个 User 模型
const authMiddleware = require('./middleware/auth');
const sequelize = require('./config/database');

const app = express();

app.use(cors());
app.use(express.json());

// 辅助函数：验证邮箱格式
const isValidEmail = (email) => {
  // 简单的邮箱格式验证
  return /\S+@\S+\.\S+/.test(email);
};

// 临时登录路由
app.post('/api/auth/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    const user = await User.findOne({ where: { email } });
    if (!user) {
      return res.status(401).json({ message: '邮箱或密码错误' });
    }
    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      return res.status(401).json({ message: '邮箱或密码错误' });
    }
    const token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET, { expiresIn: '1h' });
    res.json({ token, userId: user.id });
  } catch (error) {
    console.error('登录错误:', error);
    res.status(500).json({ message: '服务器错误，请稍后再试' });
  }
});

// 受保护的路由示例
app.get('/api/user/profile', authMiddleware, async (req, res) => {
  try {
    const user = await User.findByPk(req.userId, { attributes: ['id', 'email'] });
    if (!user) {
      return res.status(404).json({ message: '用户不存在' });
    }
    res.json(user);
  } catch (error) {
    console.error('获取用户信息错误:', error);
    res.status(500).json({ message: '服务器错误，请稍后再试' });
  }
});

// 在 server.js 或专门的 authController.js 中
app.post('/api/auth/register', async (req, res) => {
  try {
    const { email, password } = req.body;
    // 验证邮箱格式
    if (!isValidEmail(email)) {
      return res.status(400).json({ message: '无效的邮箱格式' });
    }
    // 检查邮箱是否已被注册
    const existingUser = await User.findOne({ where: { email } });
    if (existingUser) {
      return res.status(400).json({ message: '该邮箱已被注册' });
    }
    // 加密密码
    const hashedPassword = await bcrypt.hash(password, 10);
    // 创建新用户
    const newUser = await User.create({ email, password: hashedPassword });
    res.status(201).json({ message: '注册成功', userId: newUser.id });
  } catch (error) {
    console.error('注册错误:', error);
    res.status(500).json({ message: '服务器错误，请稍后再试' });
  }
});

sequelize.authenticate()
  .then(() => {
    console.log('Database connection has been established successfully.');
    return sequelize.sync({ force: false });
  })
  .then(() => {
    console.log('Database synced');
    const PORT = process.env.PORT || 3000;
    app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
  })
  .catch(err => {
    console.error('Unable to connect to the database:', err);
  });
