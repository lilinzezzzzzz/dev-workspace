################################################################################
# 一键部署开发环境 - Windows PowerShell 版本
################################################################################
#
# 功能: 自动完成 SSH 密钥检查、Docker 构建和服务启动
# 用法: .\setup.ps1
#

$ErrorActionPreference = "Stop"

# 颜色输出函数
function Write-Step($message) {
    Write-Host "`n[$([char]0x2192)] $message" -ForegroundColor Cyan
}

function Write-Success($message) {
    Write-Host "[✓] $message" -ForegroundColor Green
}

function Write-Error($message) {
    Write-Host "[✗] $message" -ForegroundColor Red
}

function Write-Warning($message) {
    Write-Host "[!] $message" -ForegroundColor Yellow
}

# 获取脚本所在目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Python 开发环境一键部署" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# ============================================================
# 步骤 1: 检查 Docker 环境
# ============================================================
Write-Step "检查 Docker 环境..."

try {
    $dockerVersion = docker --version 2>&1
    Write-Success "Docker 已安装: $dockerVersion"
} catch {
    Write-Error "Docker 未安装或未启动"
    Write-Host "请先安装 Docker Desktop: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

try {
    $composeVersion = docker-compose --version 2>&1
    Write-Success "Docker Compose 已安装: $composeVersion"
} catch {
    Write-Error "Docker Compose 未安装"
    exit 1
}

# ============================================================
# 步骤 2: 检查 SSH 密钥
# ============================================================
Write-Step "检查 SSH 密钥..."

$SshSourceDir = Join-Path $env:USERPROFILE ".ssh"
$SshTargetDir = Join-Path $ScriptDir "ssh-keys"
$rsaKey = Join-Path $SshSourceDir "id_rsa"
$ed25519Key = Join-Path $SshSourceDir "id_ed25519"

# 检查是否存在 SSH 密钥
if (-not (Test-Path $rsaKey) -and -not (Test-Path $ed25519Key)) {
    Write-Error "未找到 SSH 密钥文件"
    Write-Host ""
    Write-Host "请先生成 SSH 密钥:" -ForegroundColor Yellow
    Write-Host "  ssh-keygen -t rsa -b 4096" -ForegroundColor White
    Write-Host "  或" -ForegroundColor Yellow
    Write-Host "  ssh-keygen -t ed25519" -ForegroundColor White
    exit 1
}

Write-Success "检测到 SSH 密钥"

# ============================================================
# 步骤 3: 复制 SSH 密钥
# ============================================================
Write-Step "复制 SSH 密钥到项目目录..."

# 确保目标目录存在
if (-not (Test-Path $SshTargetDir)) {
    New-Item -ItemType Directory -Path $SshTargetDir -Force | Out-Null
}

# 复制密钥文件
$filesToCopy = @("id_rsa", "id_rsa.pub", "id_ed25519", "id_ed25519.pub")
$copiedCount = 0

foreach ($file in $filesToCopy) {
    $sourceFile = Join-Path $SshSourceDir $file
    if (Test-Path $sourceFile) {
        Copy-Item -Path $sourceFile -Destination $SshTargetDir -Force
        Write-Host "  已复制: $file" -ForegroundColor Gray
        $copiedCount++
    }
}

if ($copiedCount -eq 0) {
    Write-Error "没有复制任何密钥文件"
    exit 1
}

Write-Success "已复制 $copiedCount 个密钥文件"

# ============================================================
# 步骤 4: 设置私钥权限
# ============================================================
Write-Step "设置私钥文件权限..."

$privateKeys = @("id_rsa", "id_ed25519")
foreach ($key in $privateKeys) {
    $keyPath = Join-Path $SshTargetDir $key
    if (Test-Path $keyPath) {
        icacls $keyPath /inheritance:r /grant:r "$($env:USERNAME):(R)" 2>&1 | Out-Null
        Write-Host "  已设置权限: $key" -ForegroundColor Gray
    }
}

Write-Success "私钥权限设置完成"

# ============================================================
# 步骤 5: 构建 Docker 镜像
# ============================================================
Write-Step "构建 Docker 镜像 (可能需要几分钟)..."

try {
    docker-compose build --no-cache 2>&1 | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
    Write-Success "Docker 镜像构建完成"
} catch {
    Write-Error "Docker 镜像构建失败"
    exit 1
}

# ============================================================
# 步骤 6: 启动服务
# ============================================================
Write-Step "启动服务..."

try {
    docker-compose up -d 2>&1 | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
    Write-Success "服务启动完成"
} catch {
    Write-Error "服务启动失败"
    exit 1
}

# ============================================================
# 步骤 7: 等待健康检查
# ============================================================
Write-Step "等待服务就绪..."

Start-Sleep -Seconds 5

$status = docker-compose ps --format json 2>&1 | ConvertFrom-Json
$allHealthy = $true

foreach ($service in $status) {
    if ($service.State -eq "running") {
        Write-Host "  ✓ $($service.Name): 运行中" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $($service.Name): $($service.State)" -ForegroundColor Red
        $allHealthy = $false
    }
}

# ============================================================
# 完成
# ============================================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  部署完成!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "连接方式:" -ForegroundColor Cyan
Write-Host "  SSH 免密登录:  ssh -i ./ssh-keys/id_rsa root@localhost -p 10022" -ForegroundColor White
Write-Host "  SSH 密码登录:  ssh root@localhost -p 10022  (密码: 123456)" -ForegroundColor White
Write-Host "  进入容器:      docker exec -it python-venv bash" -ForegroundColor White
Write-Host ""
Write-Host "Redis 连接:" -ForegroundColor Cyan
Write-Host "  redis-cli -h localhost -p 6379 -a 123456" -ForegroundColor White
Write-Host ""
