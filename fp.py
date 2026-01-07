import pygame
import sys
import random
import cv2
import mediapipe as mp
import math
import requests
import time
import threading
import os

# --- Performance Optimization for EXE ---
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # Suppress heavy logging

# --- PyInstaller Fix for MediaPipe ---
# When running as an EXE, PyInstaller unpacks data to a temporary folder (_MEIPASS)
# We need to ensure MediaPipe finds its models there.
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
    os.chdir(base_path)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

# --- Configuration ---
# Set this to your live URL once deployed (e.g., "https://yourname.pythonanywhere.com/api")
PRODUCTION_URL = "https://Shalcoder1.pythonanywhere.com/api" 
LOCAL_URL = "http://localhost:5000/api"
API_URL = PRODUCTION_URL if PRODUCTION_URL else LOCAL_URL

# --- Pygame Setup ---
pygame.init()

# LAPTOP OPTIMIZED LAYOUT
CAMERA_WIDTH = 320
CAMERA_HEIGHT = 240
GAME_WIDTH = 640
GAME_HEIGHT = 480
LEADERBOARD_WIDTH = 300
SCREEN_WIDTH = CAMERA_WIDTH + GAME_WIDTH + LEADERBOARD_WIDTH
SCREEN_HEIGHT = GAME_HEIGHT

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("AeroGesture - Vision Controlled Flight")
clock = pygame.time.Clock()

# Fonts
title_font = pygame.font.Font(None, 60)
game_font = pygame.font.Font(None, 40)
small_font = pygame.font.Font(None, 24)

# --- Colors ---
BG_DARK = (10, 10, 25)
NEON_CYAN = (0, 255, 240)
NEON_MAGENTA = (255, 0, 150)
NEON_LIME = (50, 255, 50)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# --- Physics Constants ---
GRAVITY = 1700.0
FLAP_STRENGTH = -550.0
PIPE_SPEED = 240.0
MAX_FALL_SPEED = 800.0

# --- Game Variables ---
PIPE_GAP = 180
PIPE_SPAWN_TIME = 2.0
pipe_timer = 0
SCORE = 0
GAME_STATE = "USERNAME"
USERNAME = ""
PLAYER_ID = None
START_TIME = 0
LEADERBOARD_DATA = []
LAST_LEADERBOARD_UPDATE = 0

# --- Threaded Gesture Controller ---
class GestureController:
    def __init__(self):
        # Using 0 for first camera, try to be robust
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0)
            
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1, 
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            model_complexity=0 
        )
        
        self.frame_surface = None
        self.gesture_flap = False
        self.is_pinching = False
        self.running = True
        self.lock = threading.Lock()
        
        # Buffer for smoothing
        self.smooth_dist = 0
        self.ema_alpha = 0.3 
        
        self.thread = threading.Thread(target=self.update, daemon=True)
        self.thread.start()

    def update(self):
        while self.running:
            success, frame = self.cap.read()
            if not success:
                time.sleep(0.1)
                continue
            
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb)
            
            flap_trigger = False
            
            if results.multi_hand_landmarks:
                lm = results.multi_hand_landmarks[0]
                h, w, _ = frame.shape
                
                # Tips: 4 (Thumb), 8 (Index)
                # Base for scale: 0 (Wrist), 5 (Index Base/MCP)
                thumb_tip = lm.landmark[4]
                index_tip = lm.landmark[8]
                wrist = lm.landmark[0]
                index_base = lm.landmark[5]
                
                # Pixel coordinates
                p_thumb = (thumb_tip.x * w, thumb_tip.y * h)
                p_index = (index_tip.x * w, index_tip.y * h)
                p_wrist = (wrist.x * w, wrist.y * h)
                p_base = (index_base.x * w, index_base.y * h)
                
                # Distance between tips
                dist = math.hypot(p_thumb[0]-p_index[0], p_thumb[1]-p_index[1])
                
                # Scale normalization: using distance from wrist to index base as hand size
                hand_size = math.hypot(p_wrist[0]-p_base[0], p_wrist[1]-p_base[1])
                if hand_size == 0: hand_size = 1
                
                # Relative distance (percentage of hand size)
                rel_dist = (dist / hand_size) * 100
                
                # Smoothing
                if self.smooth_dist == 0: self.smooth_dist = rel_dist
                self.smooth_dist = (self.ema_alpha * rel_dist) + ((1 - self.ema_alpha) * self.smooth_dist)
                
                # GESTURE THRESHOLDS (Recalibrated for Stable Tracking)
                # These settings match the 'tightness' of the original Pro mode 
                # but work with the more stable Wrist-to-Base measurement.
                TRIGGER = 45 
                RELEASE = 65
                
                if self.smooth_dist < TRIGGER:
                    if not self.is_pinching:
                        flap_trigger = True
                        self.is_pinching = True
                    cv2.line(frame, (int(p_thumb[0]), int(p_thumb[1])), (int(p_index[0]), int(p_index[1])), (0, 255, 0), 4)
                elif self.smooth_dist > RELEASE:
                    self.is_pinching = False
                    cv2.line(frame, (int(p_thumb[0]), int(p_thumb[1])), (int(p_index[0]), int(p_index[1])), (0, 255, 255), 2)
                else:
                    cv2.line(frame, (int(p_thumb[0]), int(p_thumb[1])), (int(p_index[0]), int(p_index[1])), (255, 0, 0), 2)
                
                # Draw landmarks
                cv2.circle(frame, (int(p_thumb[0]), int(p_thumb[1])), 6, (255, 0, 255), -1)
                cv2.circle(frame, (int(p_index[0]), int(p_index[1])), 6, (0, 255, 255), -1)
                
                # Vision Debug Text
                cv2.putText(frame, f"Control: {int(self.smooth_dist)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            new_surface = pygame.surfarray.make_surface(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).swapaxes(0, 1))
            with self.lock:
                self.frame_surface = new_surface
                if flap_trigger: self.gesture_flap = True
            
            # Optimization: Dynamic sleep to prevent CPU hogging in standalone mode
            time.sleep(0.002)

    def get_state(self):
        with self.lock:
            flap = self.gesture_flap
            self.gesture_flap = False
            return flap, self.frame_surface

    def stop(self):
        self.running = False
        self.cap.release()

# --- Initialize Gesture Thread ---
gesture_cam = GestureController()

# --- Particles ---
particles = []
def add_particle(x, y, color):
    particles.append({
        'x': x, 'y': y,
        'vx': random.uniform(-40, 0),
        'vy': random.uniform(-15, 15),
        'life': 0.6,
        'color': color
    })

def update_draw_particles(surface, dt):
    for p in particles[:]:
        p['life'] -= dt
        p['x'] += p['vx'] * dt
        p['y'] += p['vy'] * dt
        if p['life'] <= 0:
            particles.remove(p)
            continue
        size = int(6 * (p['life'] / 0.6))
        if size > 0:
            pygame.draw.circle(surface, p['color'], (int(p['x']), int(p['y'])), size)

# --- Background ---
static_bg = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
static_bg.fill(BG_DARK)
for y in range(0, GAME_HEIGHT, 4):
    pygame.draw.line(static_bg, (20, 20, 60), (0, y), (GAME_WIDTH, y))

stars = [{'x': random.randint(0, GAME_WIDTH), 'y': random.randint(0, GAME_HEIGHT), 
          'speed': random.uniform(10, 60)} for _ in range(50)]

# --- Classes ---
class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.radius = 20
        self.rect = pygame.Rect(CAMERA_WIDTH + 100, GAME_HEIGHT // 2, self.radius*2, self.radius*2)
        self.velocity = 0
        self.angle = 0
        self.wing_angle = 0
        self.wing_dir = 1
    
    def flap(self):
        self.velocity = FLAP_STRENGTH
        add_particle(self.rect.centerx - CAMERA_WIDTH, self.rect.centery, YELLOW)

    def update(self, dt):
        self.velocity += GRAVITY * dt
        if self.velocity > MAX_FALL_SPEED: self.velocity = MAX_FALL_SPEED
        self.rect.y += self.velocity * dt
        
        # Rotation
        target_angle = -30 if self.velocity < 0 else 45
        self.angle += (target_angle - self.angle) * 8 * dt
        
        # Wing flap animation
        self.wing_angle += 700 * dt * self.wing_dir
        if abs(self.wing_angle) > 30: self.wing_dir *= -1
        
        if self.rect.top <= 0:
            self.rect.top = 0
            self.velocity = 0
        if self.rect.bottom >= GAME_HEIGHT:
            self.rect.bottom = GAME_HEIGHT
            return False
        return True

    def draw(self, surface):
        # Local coordinates on game surface
        lx = self.rect.centerx - CAMERA_WIDTH
        ly = self.rect.centery
        
        # 1. Body (Yellow)
        pygame.draw.circle(surface, YELLOW, (lx, ly), self.radius)
        pygame.draw.circle(surface, (0,0,0), (lx, ly), self.radius, 2)
        
        # 2. Eye
        eye_x = lx + 10
        eye_y = ly - 8
        pygame.draw.circle(surface, WHITE, (eye_x, eye_y), 8)
        pygame.draw.circle(surface, (0,0,0), (eye_x, eye_y), 8, 1)
        pygame.draw.circle(surface, (0,0,0), (eye_x + 3, eye_y), 3) # Pupil
        
        # 3. Beak (Orange)
        beak_pts = [(lx + 15, ly), (lx + 30, ly + 5), (lx + 15, ly + 10)]
        pygame.draw.polygon(surface, ORANGE, beak_pts)
        pygame.draw.polygon(surface, (0,0,0), beak_pts, 2)
        
        # 4. Wing (White)
        wing_y_off = math.sin(math.radians(self.wing_angle)) * 8
        wing_rect = pygame.Rect(lx - 20, ly - 5 + wing_y_off, 18, 12)
        pygame.draw.ellipse(surface, WHITE, wing_rect)
        pygame.draw.ellipse(surface, (0,0,0), wing_rect, 1)

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, height, is_bottom):
        super().__init__()
        self.width = 80
        self.height = height
        self.rect = pygame.Rect(CAMERA_WIDTH + x, 0, self.width, self.height)
        if is_bottom: self.rect.y = GAME_HEIGHT - self.height
        
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(NEON_LIME)
        # Detail
        pygame.draw.rect(self.image, (0, 100, 0), (self.width-15, 0, 15, self.height))
        pygame.draw.rect(self.image, (0, 60, 0), (0, 0, self.width, self.height), 3)
        # Cap
        cap_h = 25
        if is_bottom:
            pygame.draw.rect(self.image, (80, 255, 80), (0, 0, self.width, cap_h))
            pygame.draw.rect(self.image, (0, 60, 0), (0, 0, self.width, cap_h), 2)
        else:
            pygame.draw.rect(self.image, (80, 255, 80), (0, self.height - cap_h, self.width, cap_h))
            pygame.draw.rect(self.image, (0, 60, 0), (0, self.height - cap_h, self.width, cap_h), 2)

    def update(self, dt):
        self.rect.x -= PIPE_SPEED * dt
        if self.rect.right < CAMERA_WIDTH: self.kill()
            
    def draw(self, surface):
        surface.blit(self.image, (self.rect.x - CAMERA_WIDTH, self.rect.y))

def create_pipes():
    min_h = 55
    avail_h = GAME_HEIGHT - PIPE_GAP - (2 * min_h)
    top = min_h + random.uniform(0, 1) * avail_h
    return [Pipe(GAME_WIDTH + 50, int(top), False), Pipe(GAME_WIDTH + 50, int(GAME_HEIGHT - PIPE_GAP - top), True)]

# --- Reset ---
bird = Bird()
pipes = []

def reset_game():
    global bird, pipes, SCORE, GAME_STATE, pipe_timer, START_TIME
    bird = Bird()
    pipes = []
    SCORE = 0
    GAME_STATE = "PLAYING"
    pipe_timer = 0
    START_TIME = time.time()

# --- API (Now Threaded to prevent freezing) ---
def _bg_register(username, callback):
    try:
        r = requests.post(f"{API_URL}/player/register", json={"username": username}, timeout=3.0)
        if r.status_code == 200: callback(r.json().get('player_id'))
    except: callback(None)

def _bg_submit(p_id, score, dur, callback=None):
    try:
        requests.post(f"{API_URL}/score/submit", json={"player_id": p_id, "score": score, "duration": dur}, timeout=3.0)
        if callback: callback()
    except: pass

def _bg_fetch(callback):
    try:
        r = requests.get(f"{API_URL}/leaderboard?limit=10", timeout=3.0)
        if r.status_code == 200: callback(r.json().get('leaderboard', []))
    except: pass

def register_player(username):
    # This is still sync for the login screen but we'll add a connecting state
    threading.Thread(target=_bg_register, args=(username, lambda pid: setattr(sys.modules[__name__], 'PLAYER_ID', pid)), daemon=True).start()

def submit_score_async(p_id, score, dur):
    if not p_id: return
    threading.Thread(target=_bg_submit, args=(p_id, score, dur), daemon=True).start()

def fetch_leaderboard_async():
    def update_lb(data):
        setattr(sys.modules[__name__], 'LEADERBOARD_DATA', data)
    threading.Thread(target=_bg_fetch, args=(update_lb,), daemon=True).start()

# --- Main Game Loop ---
while True:
    dt = clock.tick(90) / 1000.0 # Adjusted for smoothness vs performance
    if dt > 0.05: dt = 0.05
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gesture_cam.stop()
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.KEYDOWN:
            if GAME_STATE == "USERNAME":
                if event.key == pygame.K_RETURN and USERNAME:
                    reset_game()
                    # Start registration in background - FIXED to be async
                    threading.Thread(target=_bg_register, args=(USERNAME, lambda pid: setattr(sys.modules[__name__], 'PLAYER_ID', pid)), daemon=True).start()
                elif event.key == pygame.K_BACKSPACE: USERNAME = USERNAME[:-1]
                elif event.unicode.isprintable() and len(USERNAME) < 12: USERNAME += event.unicode.upper()
            elif GAME_STATE == "PLAYING" and event.key == pygame.K_SPACE:
                bird.flap()
            elif GAME_STATE == "GAME_OVER" and event.key == pygame.K_ESCAPE:
                GAME_STATE = "USERNAME"; USERNAME = ""

    gesture_flap, cam_surface = gesture_cam.get_state()
    
    screen.fill((0,0,0))
    if cam_surface: screen.blit(cam_surface, (0,0))
    pygame.draw.rect(screen, NEON_CYAN, (0,0,CAMERA_WIDTH, CAMERA_HEIGHT), 2)
    
    game_s = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
    game_s.blit(static_bg, (0,0))
    for star in stars:
        star['x'] -= star['speed'] * dt
        if star['x'] < 0: star['x'] = GAME_WIDTH
        pygame.draw.circle(game_s, (200,200,255), (int(star['x']), int(star['y'])), 1)
            
    if GAME_STATE == "USERNAME":
        cx = GAME_WIDTH // 2
        game_s.blit(title_font.render("AeroGesture", True, NEON_MAGENTA), (cx-130, 130))
        game_s.blit(game_font.render("ENTER HERO NAME:", True, WHITE), (cx-130, 210))
        game_s.blit(game_font.render(USERNAME + "|", True, YELLOW), (cx-50, 260))
        game_s.blit(small_font.render("PINCH GESTURE TO START", True, NEON_LIME), (cx-120, 350))
        if gesture_flap and USERNAME: 
            # Quick sync check for ID, then go
            reset_game()
            threading.Thread(target=_bg_register, args=(USERNAME, lambda pid: setattr(sys.modules[__name__], 'PLAYER_ID', pid)), daemon=True).start()
            
    elif GAME_STATE == "PLAYING":
        if gesture_flap: bird.flap()
        if not bird.update(dt):
            GAME_STATE = "GAME_OVER"
            submit_score_async(PLAYER_ID, SCORE, time.time() - START_TIME)
            fetch_leaderboard_async()
        
        pipe_timer += dt
        if pipe_timer > PIPE_SPAWN_TIME:
            pipes.extend(create_pipes())
            pipe_timer = 0
            
        for p in pipes[:]:
            p.update(dt)
            if p.rect.colliderect(bird.rect):
                GAME_STATE = "GAME_OVER"
                submit_score_async(PLAYER_ID, SCORE, time.time() - START_TIME)
                fetch_leaderboard_async()
            if not getattr(p, 'scored', False) and p.rect.right < bird.rect.left and p.rect.y == 0:
                SCORE += 1; p.scored = True
        
        update_draw_particles(game_s, dt)
        for p in pipes: p.draw(game_s)
        bird.draw(game_s)
        game_s.blit(title_font.render(str(SCORE), True, WHITE), (GAME_WIDTH//2 - 20, 50))
        
    elif GAME_STATE == "GAME_OVER":
        for p in pipes: p.draw(game_s)
        bird.draw(game_s)
        cx = GAME_WIDTH // 2
        game_s.blit(title_font.render("GAME OVER", True, NEON_MAGENTA), (cx-120, 180))
        game_s.blit(game_font.render(f"SCORE: {SCORE}", True, WHITE), (cx-70, 240))
        game_s.blit(small_font.render("PINCH TO RETRY / ESC TO MENU", True, NEON_LIME), (cx-150, 320))
        if gesture_flap: reset_game()
        
    screen.blit(game_s, (CAMERA_WIDTH, 0))
    lb_x = CAMERA_WIDTH + GAME_WIDTH
    screen.blit(static_bg, (lb_x, 0), (0,0,LEADERBOARD_WIDTH, GAME_HEIGHT))
    screen.blit(small_font.render("GLOBAL TOP SCORES", True, NEON_MAGENTA), (lb_x + 50, 30))
    
    if time.time() - LAST_LEADERBOARD_UPDATE > 15:
        fetch_leaderboard_async()
        LAST_LEADERBOARD_UPDATE = time.time()
    
    if LEADERBOARD_DATA:
        for idx, row in enumerate(LEADERBOARD_DATA[:10]):
            score_val = row.get('best_score')
            if score_val is None: score_val = 0
            txt = f"#{idx+1} {row['username'][:12]:<12} {int(score_val)}"
            screen.blit(small_font.render(txt, True, WHITE), (lb_x + 20, 80 + idx*38))

    pygame.display.flip()
