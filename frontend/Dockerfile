# 多阶段构建 - 构建阶段
FROM node:18-alpine AS builder

WORKDIR /app

# 设置 npm 镜像和 Alpine 镜像
RUN npm config set registry https://registry.npmmirror.com && \
    sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories

# 复制package文件
COPY package*.json ./

# 清理缓存并重新安装依赖
RUN rm -rf node_modules package-lock.json
RUN npm install

# 复制源代码
COPY . .

# 构建项目
RUN npm run build

# 生产阶段
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]