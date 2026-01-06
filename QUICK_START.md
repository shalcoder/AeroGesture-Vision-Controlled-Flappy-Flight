# 🎮 FLAPPY BIRD ARCADE - QUICK REFERENCE GUIDE

## ⚡ Quick Start (5 Steps)

### 1️⃣ Open First Terminal (Server)
```powershell
cd c:\Users\VISHAL\Downloads\flappybird
.\start_server.ps1
```
✅ **Keep this running!** You should see:
```
🎮 Flappy Bird Multiplayer Server Starting...
📊 Dashboard: http://localhost:5000
* Running on http://0.0.0.0:5000
```

### 2️⃣ Open Second Terminal (Game)
```powershell
cd c:\Users\VISHAL\Downloads\flappybird
.\start_game.ps1
```
✅ **Game window opens** (1840x600 pixels)

### 3️⃣ Enter Your Name
- Type your arcade username (max 15 chars)
- Press ENTER or PINCH to start

### 4️⃣ Play the Game
- **Pinch fingers** (thumb + index) to flap
- Avoid green pipes
- Beat high scores!

### 5️⃣ View Leaderboard
Open browser: http://localhost:5000

---

## 🎯 System Requirements

| Component | Required Version |
|-----------|-----------------|
| **Python** | **3.11.9** |
| **Webcam** | Any USB/Built-in |
| **OS** | Windows 10/11 |
| **Screen** | 1920x1080+ (for best experience) |

---

## 📦 Required Libraries

```
pygame==2.5.0          # Game graphics
opencv-python==4.8.0   # Camera
mediapipe==0.10.0      # Hand tracking
flask==3.0.0           # Web server
flask-cors==4.0.0      # API support
requests==2.31.0       # Networking
```

---

## 🎮 Game Controls

### Gesture Controls
- **👋 Show Hand** - Camera detects your hand
- **🤏 Pinch** - Thumb + Index finger < 30px apart = FLAP
- **✋ Open Hand** - Bird falls due to gravity

### Keyboard Controls (Backup)
- `SPACE` - Flap
- `ENTER` - Submit username / Start game
- `BACKSPACE` - Delete character
- `ESC` - Return to menu (after game over)
- `ALT+F4` - Quit

---

## 🖥️ Screen Layout

```
╔═══════════════════════════════════════════════════════════╗
║  📹 CAMERA (640px)  │  🎮 GAME (800px)  │ 🏆 BOARD (400px) ║
║                     │                   │                  ║
║  Live Hand Tracking │  Flappy Bird      │  Top 10 Players  ║
║  + Pinch Detection  │  Gameplay Area    │  Live Scores     ║
║                     │                   │                  ║
╚═══════════════════════════════════════════════════════════╝
                    Total: 1840x600 pixels
```

---

## 🌐 Web Dashboard URLs

| Page | URL | Description |
|------|-----|-------------|
| **Main Dashboard** | http://localhost:5000 | Stats + Top 10 |
| **Full Leaderboard** | http://localhost:5000/leaderboard | All players + filters |
| **API Docs** | http://localhost:5000/api/ | REST API |

---

## 🔧 Troubleshooting

### ❌ Camera Not Working
```
✓ Check webcam is plugged in
✓ Close other apps using camera (Zoom, Teams, etc.)
✓ Allow camera permissions in Windows Settings
✓ Ensure good lighting (bright room)
```

### ❌ Server Won't Start
```
✓ Check port 5000 is not in use
✓ Run: Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess
✓ Kill the process if needed
✓ Restart PowerShell as Administrator
```

### ❌ Pinch Not Detected
```
✓ Show FULL hand to camera (all 5 fingers visible)
✓ Improve lighting conditions
✓ Adjust PINCH_THRESHOLD in game_multiplayer.py (line 150)
✓ Check distance value shown on camera view
```

### ❌ Low FPS / Lag
```
✓ Close other applications
✓ Reduce camera resolution in game_multiplayer.py:
  CAMERA_WIDTH = 480
  CAMERA_HEIGHT = 360
✓ Lower MediaPipe confidence (line 445):
  min_detection_confidence=0.5
```

### ❌ Scores Not Saving
```
✓ Ensure Flask server is running (Terminal 1)
✓ Check http://localhost:5000 loads
✓ Look for connection errors in game terminal
✓ Check flappybird.db file was created
```

---

## 📊 Project Files

```
flappybird/
├── 🚀 start_server.ps1          # Quick start Flask (run first)
├── 🎮 start_game.ps1             # Quick start Game (run second)
├── 📝 README.md                  # Full documentation
├── 📋 QUICK_START.md             # This file!
├── 🐍 app.py                     # Flask backend + API
├── 🎯 game_multiplayer.py        # Main game (big screen)
├── 🎮 fp.py                      # Original single-player
├── 📦 requirements.txt           # Python dependencies
├── 💾 flappybird.db              # SQLite database (auto-created)
├── 📁 templates/
│   ├── dashboard.html            # Main web dashboard
│   └── leaderboard.html          # Full leaderboard page
└── 📁 venv/                      # Virtual environment (Python 3.11)
```

---

## 🎨 Visual Features

### Game Graphics
- ✨ Neon color scheme (Cyan, Pink, Yellow, Green)
- 💫 Gradient backgrounds
- 🔮 Smooth 60 FPS animations
- 🎭 Glow effects on text
- 💎 Premium arcade styling

### Web Dashboard
- 🌟 Glassmorphism design
- 🎆 50+ animated background particles
- 🌈 Color gradients and shimmer effects
- 📱 Fully responsive (mobile-friendly)
- 🔄 Auto-refresh every 10 seconds

---

## 🏆 Leaderboard Features

- 🥇 **Podium View** - Top 3 players with medals
- 📅 **Time Filters** - All Time / Today / This Week
- 📊 **Player Stats** - Best score, games played, average
- 🎯 **Live Updates** - Real-time score submissions
- 💫 **Animations** - Smooth slide-ins and transitions

---

## 📞 Need Help?

1. **Check README.md** for detailed documentation
2. **Verify Python 3.11** is installed: `py -3.11 --version`
3. **Ensure webcam works** in other apps first
4. **Check both terminals** for error messages
5. **Test API** by visiting http://localhost:5000

---

## 🎯 Gameplay Tips

### For Best Scores:
1. 🎯 **Timing is Everything** - Don't flap too early/late
2. 👀 **Look Ahead** - Focus on upcoming pipes
3. 🧘 **Stay Calm** - Smooth, controlled movements
4. 💪 **Practice Pinching** - Get comfortable with gesture
5. 📊 **Watch Top Players** - Learn from leaderboard

### Pinch Detection Tips:
- Keep hand **15-20 inches** from camera
- Ensure **bright lighting** (no shadows)
- Show **all fingers** clearly
- Make **crisp pinching motion**
- Watch **distance value** on camera view

---

## 🚀 Performance Tips

### For Smooth Gameplay:
```python
# In game_multiplayer.py, adjust these values:

# Reduce camera resolution (line 8-9):
CAMERA_WIDTH = 480   # Instead of 640
CAMERA_HEIGHT = 360  # Instead of 480

# Lower detection confidence (line 445):
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.5  # Instead of 0.7
)

# Increase pinch threshold for easier detection (line 150):
PINCH_THRESHOLD = 40  # Instead of 30
```

---

## ✅ Pre-Launch Checklist

Before playing, ensure:
- [ ] Python 3.11.9 installed (`py -3.11 --version`)
- [ ] Virtual environment created (`venv` folder exists)
- [ ] Dependencies installed (`pip list` shows pygame, mediapipe, etc.)
- [ ] Webcam connected and working
- [ ] Port 5000 is available
- [ ] Both PowerShell scripts exist (`start_server.ps1`, `start_game.ps1`)

---

## 🎉 Ready to Play!

```powershell
# Terminal 1:
.\start_server.ps1

# Terminal 2:
.\start_game.ps1
```

**🏆 Let's break some records! Good luck! 🚀**

---

_For detailed documentation, see README.md_
_Python 3.11.9 | Pygame 2.5.0 | MediaPipe 0.10.0 | Flask 3.0.0_
