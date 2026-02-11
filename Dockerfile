FROM buildpack-deps:bookworm

ENV TZ=Etc/UTC \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    TERM=xterm-256color \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PYTHON_INSTALL_DIR=/opt/python \
    UV_PYTHON_PREFERENCE=only-managed \
    UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple

WORKDIR /app

# 启用 bash 颜色支持
RUN echo "set mouse=" >> /root/.vimrc && \
    echo 'export PS1="\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ "' >> /root/.bashrc && \
    echo 'alias ls="ls --color=auto"' >> /root/.bashrc && \
    echo 'alias ll="ls -lh --color=auto"' >> /root/.bashrc && \
    echo 'alias grep="grep --color=auto"' >> /root/.bashrc && \
    echo 'export TERM=xterm-256color' >> /root/.bashrc
# 替换为阿里云镜像源（Debian Bookworm）
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

# 基础工具 + sshd
# buildpack-deps 已包含: curl, wget, git, build-essential
RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server \
    vim unzip \
    iproute2 net-tools iputils-ping lsof \
    bubblewrap \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv（官方推荐方式）
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:/opt/python/bin:$PATH"

# 使用 uv 安装多个 Python 版本
RUN uv python install 3.11.10 && \
    uv python install 3.12.9 && \
    uv python pin 3.11.10

# 验证安装的 Python 版本
RUN uv python list

# 准备 sshd 与 host keys
RUN mkdir -p /var/run/sshd && ssh-keygen -A

# root 密码（dev only）
RUN echo 'root:123456' | chpasswd

# sshd 基本配置：允许 root+密码；关闭反向 DNS；降低爆破窗口
RUN sed -ri 's/^#?PermitRootLogin .*/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -ri 's/^#?PasswordAuthentication .*/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    sed -ri 's/^#?ChallengeResponseAuthentication .*/ChallengeResponseAuthentication no/' /etc/ssh/sshd_config && \
    sed -ri 's/^#?UsePAM .*/UsePAM yes/' /etc/ssh/sshd_config && \
    sed -ri 's/^#?UseDNS .*/UseDNS no/' /etc/ssh/sshd_config && \
    sed -ri 's/^#?MaxAuthTries .*/MaxAuthTries 3/' /etc/ssh/sshd_config && \
    sed -ri 's/^#?ClientAliveInterval .*/ClientAliveInterval 60/' /etc/ssh/sshd_config && \
    sed -ri 's/^#?ClientAliveCountMax .*/ClientAliveCountMax 3/' /etc/ssh/sshd_config && \
    sed -ri 's@^#?AuthorizedKeysFile .*@AuthorizedKeysFile .ssh/authorized_keys@' /etc/ssh/sshd_config && \
    mkdir -p /root/.ssh && chmod 700 /root/.ssh

# 复制入口脚本：处理 SSH 密钥并启动 sshd
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 轻量健康检查：确认 22 已监听
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD sh -c "ss -lnt | grep -q ':22 ' || exit 1"

ENTRYPOINT ["/entrypoint.sh"]
