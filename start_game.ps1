# Flappy Bird Arcade - Quick Start Game Script
# This script starts the Pygame application

Write-Host "🎮 Starting Flappy Bird Game..." -ForegroundColor Cyan
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

# Check if server is running
Write-Host ""
Write-Host "🔍 Checking if Flask server is running..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/stats/global" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✅ Server is running!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  WARNING: Flask server may not be running!" -ForegroundColor Yellow
    Write-Host "    Leaderboard features will not work." -ForegroundColor Yellow
    Write-Host "    To start server, run in another terminal: .\start_server.ps1" -ForegroundColor Cyan
}

# Start the game
Write-Host ""
Write-Host "🚀 Launching Flappy Bird Game..." -ForegroundColor Green
Write-Host "📹 Make sure your webcam is connected!" -ForegroundColor Cyan
Write-Host "👋 Show your hand and pinch to play!" -ForegroundColor Cyan
Write-Host ""

python game_multiplayer.py
