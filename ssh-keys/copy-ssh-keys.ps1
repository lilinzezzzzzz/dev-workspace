################################################################################
# 复制SSH密钥脚本 - Windows PowerShell版本
################################################################################
#
# 功能: 将当前用户的SSH密钥复制到当前目录
# 用法: .\copy-ssh-keys.ps1
#

# 设置错误处理
$ErrorActionPreference = "Stop"

# 获取脚本所在目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SshSourceDir = Join-Path $env:USERPROFILE ".ssh"

# 颜色输出函数
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-ColorOutput Green "========================================"
Write-ColorOutput Green "  SSH密钥复制工具 (Windows)"
Write-ColorOutput Green "========================================"
Write-Output ""

# 检查源目录是否存在
if (-not (Test-Path $SshSourceDir)) {
    Write-ColorOutput Red "错误: SSH目录不存在: $SshSourceDir"
    Write-ColorOutput Yellow "请先生成SSH密钥: ssh-keygen -t ed25519"
    exit 1
}

# 检查私钥文件是否存在
$ed25519Key = Join-Path $SshSourceDir "id_ed25519"
$rsaKey = Join-Path $SshSourceDir "id_rsa"

if (-not (Test-Path $ed25519Key) -and -not (Test-Path $rsaKey)) {
    Write-ColorOutput Red "错误: 未找到SSH密钥文件 (id_ed25519 或 id_rsa)"
    Write-ColorOutput Yellow "请先生成SSH密钥:"
    Write-Output "  ssh-keygen -t ed25519"
    Write-Output "  或"
    Write-Output "  ssh-keygen -t rsa -b 4096"
    exit 1
}

Write-ColorOutput Green "✓ 检测到SSH密钥"
Write-Output ""

Write-ColorOutput Yellow "源目录: $SshSourceDir"
Write-ColorOutput Yellow "目标目录: $ScriptDir"
Write-Output ""

# 列出将要复制的文件
Write-Output "将复制以下文件:"
try {
    Get-ChildItem -Path $SshSourceDir -File | ForEach-Object {
        Write-Output "  $($_.Name) ($([math]::Round($_.Length/1KB, 2)) KB)"
    }
} catch {
    Write-Output "  (无文件)"
}
Write-Output ""

# 询问确认
$confirmation = Read-Host "确认复制? (y/n)"
if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
    Write-ColorOutput Yellow "操作已取消"
    exit 0
}

# 复制文件
Write-ColorOutput Green "开始复制..."

# 定义要复制的文件列表
$filesToCopy = @(
    "id_rsa",
    "id_rsa.pub",
    "id_ed25519",
    "id_ed25519.pub",
    "config",
    "known_hosts",
    "known_hosts.old"
)

$copiedCount = 0

foreach ($file in $filesToCopy) {
    $sourceFile = Join-Path $SshSourceDir $file
    if (Test-Path $sourceFile) {
        try {
            # 如果目标文件已存在且权限受限，先恢复写入权限以允许覆盖
            $targetFile = Join-Path $ScriptDir $file
            if (Test-Path $targetFile) {
                icacls $targetFile /grant "$($env:USERNAME):(M)" 2>&1 | Out-Null
            }
            Copy-Item -Path $sourceFile -Destination $ScriptDir -Force
            Write-Host "  " -NoNewline
            Write-ColorOutput Green "✓ 已复制: $file"
            $copiedCount++
        } catch {
            Write-Host "  " -NoNewline
            Write-ColorOutput Red "✗ 复制失败: $file - $($_.Exception.Message)"
        }
    }
}

Write-Output ""
if ($copiedCount -eq 0) {
    Write-ColorOutput Yellow "警告: 没有找到任何SSH密钥文件"
    Write-ColorOutput Yellow "建议生成新密钥: ssh-keygen -t ed25519 -f `"$ScriptDir\id_ed25519`""
} else {
    Write-ColorOutput Green "✓ 成功复制 $copiedCount 个文件"
    Write-Output ""
    Write-ColorOutput Yellow "提示:"
    Write-Output "  1. 这些密钥文件已被 .gitignore 排除，不会提交到Git"
    Write-Output "  2. 私钥文件包含敏感信息，请妥善保管"
    Write-Output "  3. 可以使用以下命令连接到容器:"
    Write-Output "     ssh -i `"$ScriptDir\id_ed25519`" root@localhost -p 10022"
}

Write-Output ""
Write-ColorOutput Green "========================================"
Write-ColorOutput Green "  操作完成"
Write-ColorOutput Green "========================================"
