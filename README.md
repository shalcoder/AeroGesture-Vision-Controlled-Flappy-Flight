# 🎮 Flappy Bird Arcade - Multiplayer Gesture-Controlled Game

A premium, gesture-controlled Flappy Bird game with multiplayer leaderboard, modern UI, and Flask backend. Optimized for **big screen displays** with side-by-side camera and gameplay views.

---

## 📋 System Requirements

### Required Software
| Software | Version Required | Purpose |
|----------|-----------------|---------|
| **Python** | **3.11.9** | Main programming language |
| **Webcam** | Any USB/Built-in | Hand gesture detection |
| **Operating System** | Windows 10/11 | PowerShell commands |

### Python Libraries (Exact Versions)

```txt
pygame==2.5.0          # Game engine and graphics
opencv-python==4.8.0   # Camera capture and image processing
mediapipe==0.10.0      # Hand tracking and gesture recognition
flask==3.0.0           # Web server backend
flask-cors==4.0.0      # Cross-origin resource sharing
requests==2.31.0       # HTTP client for API calls
```

**Note**: These versions are tested and confirmed to work together on Python 3.11.

---

## 🛠️ Installation Guide

### Step 1: Verify Python Version

Open PowerShell in the project directory and check your Python version:

```powershell
python --version
# Should show: Python 3.9.0 (or other version)

py -3.11 --version
# Should show: Python 3.11.9
```

✅ **You MUST use Python 3.11** for this project due to MediaPipe compatibility.

### Step 2: Create Virtual Environment (Already Created)

The virtual environment is already set up in the `venv` folder using Python 3.11:

```powershell
# This was already done for you:
# py -3.11 -m venv venv
```

### Step 3: Activate Virtual Environment

**Every time** you open a new terminal, activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

You should see `(venv)` at the beginning of your command prompt.

### Step 4: Install All Dependencies

Install all required packages (already done if setup completed):

```powershell
pip install -r requirements.txt
```

This installs:
- pygame 2.5.0+
- opencv-python 4.8.0+
- mediapipe 0.10.0+
- flask 3.0.0+
- flask-cors 4.0.0+
- requests 2.31.0+

---

## 🚀 Running the Application

### 🎯 Quick Start (Recommended)

Use the provided PowerShell scripts for easy launching:

**Terminal 1 - Start Server:**
```powershell
.\start_server.ps1
```

**Terminal 2 - Start Game:**
```powershell
.\start_game.ps1
```

### 📝 Manual Start (Alternative)

### ⚠️ IMPORTANT: Run in Two Separate Terminals


You need to run **TWO applications simultaneously**:
1. Flask Backend Server (for leaderboard/database)
2. Pygame Game (the actual game)

### Terminal 1️⃣: Start Flask Backend Server

1. Open PowerShell in project directory
2. Activate virtual environment:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
3. Start the Flask server:
   ```powershell
   python app.py
   ```
4. You should see:
   ```
   🎮 Flappy Bird Multiplayer Server Starting...
   📊 Dashboard: http://localhost:5000
   🏆 Leaderboard: http://localhost:5000/leaderboard
   🔌 API: http://localhost:5000/api/
   * Running on http://0.0.0.0:5000
   ```

✅ **Keep this terminal running!** Do not close it.

### Terminal 2️⃣: Launch the Game

1. Open a **NEW** PowerShell window in project directory
2. Activate virtual environment:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
3. Launch the game:
   ```powershell
   python game_multiplayer.py
   ```
4. The game window will open (1840x600 pixels)

✅ **The game is now running!**

### 🌐 Access Web Dashboard (Optional)

While both are running, open your browser:
- **Main Dashboard**: http://localhost:5000
- **Full Leaderboard**: http://localhost:5000/leaderboard

---

## ✨ Features

### 🕹️ Game Features
- 👋 **Gesture Control** - Pinch your fingers to make the bird flap
- 📹 **Live Camera Feed** - Real-time hand tracking visualization (640x480)
- 🎨 **Modern Neon UI** - Premium arcade-style graphics with smooth animations
- 🏆 **Live Leaderboard** - Real-time top players display during gameplay
- 👤 **Player Profiles** - Arcade-style username entry system
- 📊 **Big Screen Layout** - Total: 1840x600px (Camera: 640px + Game: 800px + Leaderboard: 400px)

### 🌐 Web Dashboard
- 📊 **Global Statistics** - Total players, games, highest scores, playtime
- 🏅 **Top 10 Leaderboard** - Beautiful glassmorphism design with gradients
- 🎭 **Animated Particles** - 50+ floating particles in background
- 📱 **Responsive Design** - Works on desktop, tablet, mobile
- 🔄 **Auto-Refresh** - Real-time data updates every 10 seconds
- 💎 **Premium Animations** - Smooth transitions, hover effects, shimmer

### 🏆 Leaderboard Page
- 🥇 **Podium Display** - Animated top 3 players with medals
- 📅 **Time Filtering** - All Time, Today, This Week views
- 💎 **Premium Animations** - Slide-ins, fades, hover effects
- 🎯 **Detailed Stats** - Best score, games played, average score, rank

---

## 🎮 How to Play


### Controls
1. **Enter Username** - Type your name (max 15 characters) and press ENTER or PINCH
2. **Pinch to Flap** - Bring your thumb and index finger together (< 30px distance)
3. **Avoid Pipes** - Navigate through the green pipes
4. **Score Points** - Each pipe you pass = 1 point
5. **Beat Records** - Your score is automatically submitted to the leaderboard

### Keyboard Shortcuts
- `SPACE` - Alternative flap control
- `ENTER` - Submit username / Start game
- `BACKSPACE` - Delete character when entering username
- `ESC` - Return to username screen (after game over)
- `ALT+F4` / Close window - Exit game

### Game States
1. **USERNAME** - Enter your player name
2. **PLAYING** - Active gameplay
3. **GAME_OVER** - Score submitted, pinch to restart

## 📐 Screen Layout

```
┌──────────────┬─────────────────┬──────────────┐
│   CAMERA     │      GAME       │  LEADERBOARD │
│   640x480    │    800x600      │   400x600    │
│              │                 │              │
│  Live Hand   │  Flappy Bird    │  Top 10      │
│  Tracking    │  Gameplay       │  Players     │
│              │                 │              │
└──────────────┴─────────────────┴──────────────┘
        Total Width: 1840px
```

## 🗄️ Database Schema

### Players Table
- `id` - Primary key
- `username` - Unique player name
- `created_at` - Registration timestamp

### Scores Table
- `id` - Primary key
- `player_id` - Foreign key to players
- `score` - Game score
- `created_at` - Submission timestamp

### Game Sessions Table
- `id` - Primary key
- `player_id` - Foreign key to players
- `score` - Final score
- `duration` - Game duration in seconds
- `pipes_passed` - Number of pipes passed
- `created_at` - Session timestamp

## 🌐 API Endpoints

### POST `/api/player/register`
Register a new player or get existing player ID
```json
{
  "username": "PLAYER1"
}
```

### POST `/api/score/submit`
Submit a game score
```json
{
  "player_id": 1,
  "score": 42,
  "duration": 87.5,
  "pipes_passed": 42
}
```

### GET `/api/leaderboard?limit=10&period=all`
Get leaderboard (periods: all, today, week)

### GET `/api/player/<id>/stats`
Get detailed player statistics

### GET `/api/stats/global`
Get global game statistics

## 🎨 Design Features

### Visual Effects
- ✨ Gradient backgrounds with animated transitions
- 💫 Particle effects on web dashboard
- 🌈 Neon color scheme (cyan, pink, yellow, green)
- 🔮 Glassmorphism panels with backdrop blur
- 💎 Smooth hover animations and transitions
- 🎭 Text shadows and glow effects
- 🌟 Shimmer effects on cards

### Performance Optimizations
- 🚀 60 FPS gameplay
- ⚡ Efficient camera processing
- 🎯 Optimized collision detection
- 📊 Throttled API calls
- 💾 Lightweight SQLite database

## 📂 Project Structure

```
flappybird/
├── app.py                      # Flask backend server
├── game_multiplayer.py         # Main Pygame application
├── fp.py                       # Original single-player version
├── requirements.txt            # Python dependencies
├── flappybird.db              # SQLite database (auto-created)
├── templates/
│   ├── dashboard.html         # Main web dashboard
│   └── leaderboard.html       # Full leaderboard page
└── venv/                      # Python virtual environment
```

## 🔧 Troubleshooting

### Camera not detecting
- Ensure webcam is connected and not used by another application
- Check camera permissions in Windows Settings
- Adjust `min_detection_confidence` in MediaPipe settings

### Server connection failed
- Make sure Flask server is running on port 5000
- Check if another application is using port 5000
- Disable firewall temporarily to test

### Low FPS / Lag
- Close other applications
- Reduce `CAMERA_WIDTH` and `CAMERA_HEIGHT` in game_multiplayer.py
- Lower MediaPipe detection confidence
- Disable leaderboard auto-refresh

### Pinch not registering
- Ensure good lighting conditions
- Show full hand to camera
- Adjust `PINCH_THRESHOLD` value (default: 30)
- Check distance value in camera view

## 🎯 Future Enhancements

- 🌍 Online multiplayer with WebSockets
- 🎵 Sound effects and background music
- 🏅 Achievements and badges system
- 📈 Detailed player analytics dashboard
- 🎨 Customizable bird skins
- 🌙 Dark/Light theme toggle
- 📱 Mobile web interface
- 🎮 Joystick support
- 🔐 User authentication
- 💬 Chat system

## 📝 Technology Stack

- **Game Engine**: Pygame 2.5.0
- **Computer Vision**: MediaPipe, OpenCV
- **Backend**: Flask 3.0.0
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Fonts**: Google Fonts (Orbitron, Rajdhani)

## 📄 License

This project is created for educational purposes.

## 👨‍💻 Credits

Developed with ❤️ using:
- Python 3.11
- Gesture recognition powered by MediaPipe
- Modern UI inspired by arcade gaming

---

## 🎮 Ready to Play!

1. Start Flask server: `python app.py`
2. Launch game: `python game_multiplayer.py`
3. Visit dashboard: http://localhost:5000

**Let's set some high scores! 🚀**
