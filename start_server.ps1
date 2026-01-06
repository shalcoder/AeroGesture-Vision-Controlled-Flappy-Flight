# Flappy Bird Arcade - Quick Start Script
# This script starts the Flask server

Write-Host "🎮 Starting Flappy Bird Arcade Server..." -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-Not (Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run setup first: py -3.11 -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "📦 Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Check Python version
Write-Host "🐍 Python version:" -ForegroundColor Yellow
python --version

# Start Flask server
Write-Host ""
Write-Host "🚀 Starting Flask Backend Server..." -ForegroundColor Green
Write-Host "📊 Dashboard will be available at: http://localhost:5000" -ForegroundColor Cyan
Write-Host "🏆 Leaderboard: http://localhost:5000/leaderboard" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  IMPORTANT: Keep this window open!" -ForegroundColor Yellow
Write-Host "    Open a NEW terminal and run: .\start_game.ps1" -ForegroundColor Yellow
Write-Host ""

python app.py
