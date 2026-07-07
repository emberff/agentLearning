# -*- coding: utf-8 -*-
<#
.SYNOPSIS
启动三国狼人杀游戏

.DESCRIPTION
设置 API Key 并启动游戏
#>

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  三国狼人杀 - 游戏启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否已设置 API Key
if (-not $env:DASHSCOPE_API_KEY) {
    Write-Host "请输入您的 DASHSCOPE_API_KEY:" -ForegroundColor Yellow
    $apiKey = Read-Host
    
    if ([string]::IsNullOrWhiteSpace($apiKey)) {
        Write-Host "错误: API Key 不能为空！" -ForegroundColor Red
        exit 1
    }
    
    $env:DASHSCOPE_API_KEY = $apiKey
    Write-Host "✅ API Key 已设置" -ForegroundColor Green
} else {
    Write-Host "✅ API Key 已设置" -ForegroundColor Green
}

Write-Host ""
Write-Host "正在启动游戏..." -ForegroundColor Cyan
Write-Host ""

# 运行游戏
python main.py
