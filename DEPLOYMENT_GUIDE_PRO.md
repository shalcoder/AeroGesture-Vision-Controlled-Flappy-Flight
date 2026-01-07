# 🚀 AeroVision AI - Deployment & Hosting Guide

This guide explains how to host your **Global Leaderboard Website** and package your **Gesture Game Client** for others to play.

---

## 🌐 Part 1: Hosting the Web Dashboard (PythonAnywhere)

PythonAnywhere is the best choice for this project because it supports **Persistent SQLite Databases** for free.

### 1. Preparations
*   Ensure your `requirements.txt` is updated.
*   Make sure your code is pushed to your GitHub: `https://github.com/shalcoder/AeroGesture-Vision-Controlled-Flappy-Flight.git`

### 2. PythonAnywhere Setup
1.  **Create an account** at [PythonAnywhere.com](https://www.pythonanywhere.com/).
2.  Go to **Consoles** -> **Bash** and clone your repo:
    ```bash
    git clone https://github.com/shalcoder/AeroGesture-Vision-Controlled-Flappy-Flight.git
    ```
3.  **Create a Virtual Env**:
    ```bash
    mkvirtualenv --python=/usr/bin/python3.11 flappy-env
    pip install -r requirements.txt
    ```
4.  Go to the **Web** tab -> **Add a new web app**.
    *   Choose **Manual Configuration**.
    *   Select **Python 3.11**.
5.  In the **Web** tab config:
    *   **Source code**: `/home/YOUR_USERNAME/AeroGesture-Vision-Controlled-Flappy-Flight`
    *   **Working directory**: same as source code.
    *   **Virtualenv**: `/home/YOUR_USERNAME/.virtualenvs/flappy-env`
6.  Edit the **WSGI configuration file** (link found in the Web tab):
    *   Delete everything and paste:
    ```python
    import sys
    import os

    path = '/home/YOUR_USERNAME/AeroGesture-Vision-Controlled-Flappy-Flight'
    if path not in sys.path:
        sys.path.append(path)

    from app import app as application
    ```
7.  **Reload** the web app. Your dashboard is now LIVE at `http://YOUR_USERNAME.pythonanywhere.com`.

---

## 🦅 Part 2: Distributing the Game Client (.EXE)

To let your friends play without installing Python, you can turn `fp.py` into a single Windows Executable.

### 1. Install PyInstaller
In your local terminal:
```powershell
pip install pyinstaller
```

### 2. Create the EXE
Run this command in your project folder:
```powershell
pyinstaller --noconsole --onefile --name "AeroVision_Flappy" fp.py
```

*   `--noconsole`: Hides the black CMD window when the game starts.
*   `--onefile`: Packs everything into a single `.exe` file.
*   `--name`: Rename the file to something cool.

### 3. Share it!
Inside the new `dist/` folder, you will find `AeroVision_Flappy.exe`. 
1.  Update the `PRODUCTION_URL` in `fp.py` to your new PythonAnywhere URL before building if you want the scores to save online!
2.  Send the `.exe` to your friends. They just need a webcam!

---

## 🛠️ Part 3: Sustainability & Scale
*   **Database**: Since we use SQLite, the database file `flappybird.db` will stay on the server.
*   **Performance**: If the website gets thousands of hits, consider switching `app.py` to use **PostgreSQL** (Render.com is better for that).
