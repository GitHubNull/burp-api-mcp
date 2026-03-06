#!/usr/bin/env pwsh
#Requires -Version 5.1

<#
.SYNOPSIS
    Burp Suite Montoya API MCP Server - Windows PowerShell Launcher
.DESCRIPTION
    一键启动脚本，自动检查环境、安装依赖、构建数据库并启动 MCP 服务端
.NOTES
    版本: 1.0.0
    作者: Burp API MCP Server Contributors
    协议: Apache 2.0
#>

[CmdletBinding()]
param(
    [switch]$SkipDbCheck,
    [switch]$ForceRebuild,
    [int]$Port = 8000,
    [string]$Host = "0.0.0.0"
)

# 设置严格模式
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# 颜色配置
$Colors = @{
    Info    = "Cyan"
    OK      = "Green"
    Warning = "Yellow"
    Error   = "Red"
    Title   = "Blue"
    Reset   = "White"
}

# 配置
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvDir = Join-Path $ScriptDir ".venv"
$PythonCmd = Join-Path $VenvDir "Scripts\python.exe"
$UvCmd = "uv"
$DbFile = Join-Path $ScriptDir "burp_api.db"
$ServerPort = $Port
$ServerHost = $Host

# 切换到脚本所在目录
Set-Location -Path $ScriptDir

# 辅助函数
function Write-Status {
    param([string]$Message)
    Write-Host "[$($Colors.Info)INFO$($Colors.Reset)] $Message" -ForegroundColor $Colors.Info
}

function Write-OK {
    param([string]$Message)
    Write-Host "[$($Colors.OK)OK$($Colors.Reset)] $Message" -ForegroundColor $Colors.OK
}

function Write-Error {
    param([string]$Message)
    Write-Host "[$($Colors.Error)ERROR$($Colors.Reset)] $Message" -ForegroundColor $Colors.Error
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[$($Colors.Warning)WARNING$($Colors.Reset)] $Message" -ForegroundColor $Colors.Warning
}

function Show-Banner {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor $Colors.Title
    Write-Host "║                                                              ║" -ForegroundColor $Colors.Title
    Write-Host "║   Burp Suite Montoya API MCP Server Launcher                 ║" -ForegroundColor $Colors.Title
    Write-Host "║   一键启动脚本 - Windows PowerShell 版本                     ║" -ForegroundColor $Colors.Title
    Write-Host "║                                                              ║" -ForegroundColor $Colors.Title
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor $Colors.Title
    Write-Host ""
}

function Show-ErrorBox {
    param([string]$Title, [string[]]$Lines)
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor $Colors.Error
    Write-Host "║                                                              ║" -ForegroundColor $Colors.Error
    Write-Host "║  ⚠️  $Title" -ForegroundColor $Colors.Error -NoNewline
    Write-Host "$(' ' * (59 - $Title.Length))║" -ForegroundColor $Colors.Error
    Write-Host "║                                                              ║" -ForegroundColor $Colors.Error
    foreach ($Line in $Lines) {
        Write-Host "║  $Line" -ForegroundColor $Colors.Error -NoNewline
        Write-Host "$(' ' * (59 - $Line.Length))║" -ForegroundColor $Colors.Error
    }
    Write-Host "║                                                              ║" -ForegroundColor $Colors.Error
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor $Colors.Error
    Write-Host ""
}

function Show-SuccessBox {
    param([string]$Message)
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor $Colors.OK
    Write-Host "║                                                              ║" -ForegroundColor $Colors.OK
    Write-Host "║  ✅ $Message" -ForegroundColor $Colors.OK -NoNewline
    Write-Host "$(' ' * (59 - $Message.Length))║" -ForegroundColor $Colors.OK
    Write-Host "║                                                              ║" -ForegroundColor $Colors.OK
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor $Colors.OK
    Write-Host ""
}

function Show-WarningBox {
    param([string]$Title, [string[]]$Lines)
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor $Colors.Warning
    Write-Host "║                                                              ║" -ForegroundColor $Colors.Warning
    Write-Host "║  ⚠️  $Title" -ForegroundColor $Colors.Warning -NoNewline
    Write-Host "$(' ' * (59 - $Title.Length))║" -ForegroundColor $Colors.Warning
    Write-Host "║                                                              ║" -ForegroundColor $Colors.Warning
    foreach ($Line in $Lines) {
        Write-Host "║  $Line" -ForegroundColor $Colors.Warning -NoNewline
        Write-Host "$(' ' * (59 - $Line.Length))║" -ForegroundColor $Colors.Warning
    }
    Write-Host "║                                                              ║" -ForegroundColor $Colors.Warning
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor $Colors.Warning
    Write-Host ""
}

function Show-InfoBox {
    param([string]$Title, [string[]]$Lines)
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor $Colors.Info
    Write-Host "║                                                              ║" -ForegroundColor $Colors.Info
    Write-Host "║  🗄️  $Title" -ForegroundColor $Colors.Info -NoNewline
    Write-Host "$(' ' * (59 - $Title.Length))║" -ForegroundColor $Colors.Info
    Write-Host "║                                                              ║" -ForegroundColor $Colors.Info
    foreach ($Line in $Lines) {
        Write-Host "║  $Line" -ForegroundColor $Colors.Info -NoNewline
        Write-Host "$(' ' * (59 - $Line.Length))║" -ForegroundColor $Colors.Info
    }
    Write-Host "║                                                              ║" -ForegroundColor $Colors.Info
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor $Colors.Info
    Write-Host ""
}

# 主逻辑
Show-Banner

# 检查 uv
Write-Status "检查 uv 安装..."
try {
    $UvVersion = & $UvCmd --version 2>$null
    if ($LASTEXITCODE -ne 0) { throw }
    Write-OK "uv 已安装 ($UvVersion)"
}
catch {
    Show-ErrorBox "未检测到 uv 包管理器" @(
        "请先安装 uv：",
        "",
        "PowerShell:",
        "irm https://astral.sh/uv/install.ps1 | iex",
        "",
        "或访问：https://docs.astral.sh/uv/getting-started/"
    )
    exit 1
}

# 检查/创建虚拟环境
Write-Status "检查虚拟环境..."
if (-not (Test-Path -Path $VenvDir)) {
    Write-Status "虚拟环境不存在，正在创建..."
    try {
        & $UvCmd venv 2>&1 | Out-Null
        Write-OK "虚拟环境创建完成"
    }
    catch {
        Write-Error "创建虚拟环境失败: $_"
        exit 1
    }
}
else {
    Write-OK "虚拟环境已存在"
}

# 检查 Python
if (-not (Test-Path -Path $PythonCmd)) {
    Write-Warning "虚拟环境中的 Python 不存在，尝试重新创建..."
    Remove-Item -Path $VenvDir -Recurse -Force -ErrorAction SilentlyContinue
    & $UvCmd venv 2>&1 | Out-Null
}

# 安装依赖
Write-Status "安装/更新依赖..."
try {
    $Output = & $UvCmd sync 2>&1
    if ($LASTEXITCODE -ne 0) { throw $Output }
    Write-OK "依赖安装完成"
}
catch {
    Write-Error "依赖安装失败: $_"
    exit 1
}

# 处理强制重建数据库
if ($ForceRebuild -and (Test-Path -Path $DbFile)) {
    Write-Warning "强制重建数据库..."
    Remove-Item -Path $DbFile -Force
}

# 检查数据库
Write-Status "检查数据库文件..."
if (-not (Test-Path -Path $DbFile) -and -not $SkipDbCheck) {
    Show-InfoBox "数据库文件不存在，需要构建" @(
        "这将解析所有 Java API 文件并创建索引...",
        "预计耗时 1-2 分钟"
    )
    
    Write-Status "正在构建数据库，请稍候..."
    try {
        & $UvCmd run python scripts\parse_and_import.py 2>&1
        if ($LASTEXITCODE -ne 0) { throw }
        Show-SuccessBox "数据库构建完成！"
    }
    catch {
        Write-Error "数据库构建失败: $_"
        exit 1
    }
}
elseif (Test-Path -Path $DbFile) {
    $DbSize = (Get-Item -Path $DbFile).Length / 1KB
    Write-OK "数据库文件已存在: $DbFile ($([math]::Round($DbSize, 2)) KB)"
}
else {
    Write-Warning "跳过数据库检查"
}

# 检查端口占用
Write-Status "检查端口 $ServerPort 是否被占用..."
$PortInUse = Get-NetTCPConnection -LocalPort $ServerPort -ErrorAction SilentlyContinue | Where-Object { $_.State -eq "Listen" }
if ($PortInUse) {
    $Process = Get-Process -Id $PortInUse.OwningProcess -ErrorAction SilentlyContinue
    $ProcessName = if ($Process) { $Process.ProcessName } else { "Unknown" }
    
    Show-WarningBox "端口 $ServerPort 已被占用" @(
        "占用进程: $ProcessName (PID: $($PortInUse.OwningProcess))",
        "",
        "请：",
        "1. 关闭占用该端口的程序",
        "2. 或使用 -Port 参数指定其他端口"
    )
    exit 1
}
Write-OK "端口 $ServerPort 可用"

# 显示启动信息
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor $Colors.OK
Write-Host "║                                                              ║" -ForegroundColor $Colors.OK
Write-Host "║  🚀 启动 MCP Server...                                       ║" -ForegroundColor $Colors.OK
Write-Host "║                                                              ║" -ForegroundColor $Colors.OK
Write-Host "║  服务地址: http://$ServerHost`:$ServerPort" -ForegroundColor $Colors.OK -NoNewline
Write-Host "$(' ' * (50 - $ServerHost.Length - ([string]$ServerPort).Length))║" -ForegroundColor $Colors.OK
Write-Host "║  MCP SSE:  http://$ServerHost`:$ServerPort/sse" -ForegroundColor $Colors.OK -NoNewline
Write-Host "$(' ' * (47 - $ServerHost.Length - ([string]$ServerPort).Length))║" -ForegroundColor $Colors.OK
Write-Host "║                                                              ║" -ForegroundColor $Colors.OK
Write-Host "║  按 Ctrl+C 停止服务                                         ║" -ForegroundColor $Colors.OK
Write-Host "║                                                              ║" -ForegroundColor $Colors.OK
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor $Colors.OK
Write-Host ""

# 设置 Ctrl+C 处理
[Console]::TreatControlCAsInput = $true

# 启动服务器
try {
    # 使用 Start-Process 来保持对 Ctrl+C 的控制
    $Process = Start-Process -FilePath $UvCmd -ArgumentList "run", "python", "scripts\run_server.py" -NoNewWindow -PassThru
    
    # 等待进程或用户输入
    while ($Process.HasExited -eq $false) {
        if ([Console]::KeyAvailable) {
            $Key = [Console]::ReadKey($true)
            if ($Key.Key -eq "C" -and $Key.Modifiers -eq "Control") {
                Write-Host ""
                Write-Status "接收到停止信号..."
                $Process.Kill()
                break
            }
        }
        Start-Sleep -Milliseconds 100
    }
    
    if ($Process.ExitCode -ne 0 -and $Process.ExitCode -ne -1) {
        throw "Server exited with code $($Process.ExitCode)"
    }
    
    Write-Host ""
    Write-Status "服务已停止"
    Write-Host ""
}
catch {
    Write-Host ""
    Write-Error "服务器异常退出: $_"
    Write-Host ""
    exit 1
}
