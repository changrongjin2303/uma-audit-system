FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 使用阿里云镜像源加速 (Debian)
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources || true

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .

# 优先安装 CPU 版 PyTorch 以减小镜像体积 (避免下载 900MB+ 的 CUDA 版)
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 安装Python依赖 (使用清华镜像源)
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制应用代码
COPY . .

# 创建上传和日志目录
RUN mkdir -p uploads logs

# 暴露端口
EXPOSE 8000

# 启动应用
CMD ["python", "main.py"]