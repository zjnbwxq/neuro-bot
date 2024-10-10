FROM node:14

# 设置工作目录
WORKDIR /usr/src/app

# 复制 package.json 和 package-lock.json（如果存在）
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制后端代码
COPY . .

# 暴露端口
EXPOSE 3000

# 运行应用
CMD ["node", "server.js"]