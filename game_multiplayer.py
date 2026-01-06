import pygame
import sys
import random
import cv2
import mediapipe as mp
import math
import requests
import time
from datetime import datetime

# --- Configuration ---
API_URL = "http://localhost:5000/api"
BIG_SCREEN_MODE = True

# --- Pygame Setup ---
pygame.init()

# Big screen layout: Camera (640x480) + Game (800x600) + Leaderboard panel (400x600)
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
GAME_WIDTH = 800
GAME_HEIGHT = 600
LEADERBOARD_WIDTH = 400
SCREEN_WIDTH = CAMERA_WIDTH + GAME_WIDTH + LEADERBOARD_WIDTH
SCREEN_HEIGHT = max(CAMERA_HEIGHT, GAME_HEIGHT)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("🎮 Gesture Flappy Bird - Multiplayer Arcade")
clock = pygame.time.Clock()

# Fonts
title_font = pygame.font.Font(None, 80)
game_font = pygame.font.Font(None, 50)
small_font = pygame.font.Font(None, 30)
tiny_font = pygame.font.Font(None, 24)

# --- Colors (Premium Arcade Theme) ---
BG_DARK = (15, 15, 35)
BG_GRADIENT_TOP = (20, 20, 50)
BG_GRADIENT_BOTTOM = (10, 10, 30)
NEON_BLUE = (0, 255, 255)
NEON_PINK = (255, 0, 255)
NEON_GREEN = (0, 255, 100)
NEON_YELLOW = (255, 255, 0)
NEON_ORANGE = (255, 150, 0)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
BRONZE = (205, 127, 50)
WHITE = (255, 255, 255)
PANEL_BG = (25, 25, 55, 200)
TEXT_SHADOW = (0, 0, 0)

# --- Game Variables ---
GRAVITY = 0.25
BIRD_FLAP = -6.5
PIPE_SPEED = 4
PIPE_GAP = 220
PIPE_FREQUENCY = 1800
LAST_PIPE = 0
SCORE = 0
GAME_STATE = "USERNAME"  # USERNAME, PLAYING, GAME_OVER
FLAP_COOLDOWN = 200
LAST_FLAP_TIME = 0
USERNAME = ""
PLAYER_ID = None
START_TIME = 0
LEADERBOARD_DATA = []
LAST_LEADERBOARD_UPDATE = 0

# --- API Functions ---
def register_player(username):
    """Register player and get player ID"""
    try:
        response = requests.post(f"{API_URL}/player/register", 
                               json={"username": username},
                               timeout=2)
        if response.status_code == 200:
            data = response.json()
            return data.get('player_id')
    except:
        print("⚠️ Could not connect to server, playing offline")
    return None

def submit_score(player_id, score, duration):
    """Submit score to server"""
    if not player_id:
        return
    try:
        requests.post(f"{API_URL}/score/submit",
                     json={
                         "player_id": player_id,
                         "score": score,
                         "duration": duration,
                         "pipes_passed": score
                     },
                     timeout=2)
    except:
        print("⚠️ Could not submit score")

def fetch_leaderboard():
    """Fetch leaderboard from server"""
    try:
        response = requests.get(f"{API_URL}/leaderboard?limit=10", timeout=2)
        if response.status_code == 200:
            data = response.json()
            return data.get('leaderboard', [])
    except:
        pass
    return []

# --- Drawing Functions ---
def draw_gradient_bg():
    """Draw gradient background"""
    for y in range(SCREEN_HEIGHT):
        ratio = y / SCREEN_HEIGHT
        r = int(BG_GRADIENT_TOP[0] * (1 - ratio) + BG_GRADIENT_BOTTOM[0] * ratio)
        g = int(BG_GRADIENT_TOP[1] * (1 - ratio) + BG_GRADIENT_BOTTOM[1] * ratio)
        b = int(BG_GRADIENT_TOP[2] * (1 - ratio) + BG_GRADIENT_BOTTOM[2] * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

def draw_text_with_shadow(text, font, color, x, y, center=True):
    """Draw text with shadow effect"""
    # Shadow
    shadow = font.render(text, True, TEXT_SHADOW)
    shadow_rect = shadow.get_rect(center=(x + 3, y + 3)) if center else shadow.get_rect(topleft=(x + 3, y + 3))
    screen.blit(shadow, shadow_rect)
    # Main text
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(x, y)) if center else surf.get_rect(topleft=(x, y))
    screen.blit(surf, rect)
    return rect

def draw_panel(x, y, width, height, color=PANEL_BG):
    """Draw semi-transparent panel"""
    panel = pygame.Surface((width, height), pygame.SRCALPHA)
    panel.fill(color)
    # Border glow
    pygame.draw.rect(panel, NEON_BLUE + (100,), (0, 0, width, height), 3)
    screen.blit(panel, (x, y))

def draw_username_screen():
    """Draw username entry screen"""
    draw_gradient_bg()
    
    # Title
    draw_text_with_shadow("🎮 FLAPPY BIRD ARCADE 🎮", title_font, NEON_PINK, SCREEN_WIDTH // 2, 100)
    draw_text_with_shadow("GESTURE CONTROLLED", game_font, NEON_BLUE, SCREEN_WIDTH // 2, 180)
    
    # Input panel
    panel_width = 600
    panel_height = 200
    panel_x = (SCREEN_WIDTH - panel_width) // 2
    panel_y = 300
    draw_panel(panel_x, panel_y, panel_width, panel_height)
    
    # Instructions
    draw_text_with_shadow("Enter Your Name:", game_font, WHITE, SCREEN_WIDTH // 2, panel_y + 40)
    
    # Username box
    username_text = USERNAME + "|" if len(USERNAME) < 15 else USERNAME
    color = NEON_GREEN if len(USERNAME) > 0 else WHITE
    draw_text_with_shadow(username_text, game_font, color, SCREEN_WIDTH // 2, panel_y + 100)
    
    # Start instruction
    if len(USERNAME) > 0:
        draw_text_with_shadow("Press ENTER or PINCH to Start!", small_font, NEON_YELLOW, SCREEN_WIDTH // 2, panel_y + 160)
    
    # Controls info
    draw_text_with_shadow("🤏 PINCH to Flap  |  ✋ Show Hand to Play", tiny_font, NEON_BLUE, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)

def draw_game_screen():
    """Draw the main game screen with all panels"""
    draw_gradient_bg()
    
    # Draw divider lines
    pygame.draw.line(screen, NEON_BLUE, (CAMERA_WIDTH, 0), (CAMERA_WIDTH, SCREEN_HEIGHT), 3)
    pygame.draw.line(screen, NEON_BLUE, (CAMERA_WIDTH + GAME_WIDTH, 0), (CAMERA_WIDTH + GAME_WIDTH, SCREEN_HEIGHT), 3)
    
    # Labels
    draw_text_with_shadow("📹 CAMERA", small_font, NEON_BLUE, CAMERA_WIDTH // 2, 20)
    draw_text_with_shadow("🎮 GAME", small_font, NEON_GREEN, CAMERA_WIDTH + GAME_WIDTH // 2, 20)
    draw_text_with_shadow("🏆 TOP PLAYERS", small_font, NEON_YELLOW, CAMERA_WIDTH + GAME_WIDTH + LEADERBOARD_WIDTH // 2, 20)

def draw_leaderboard():
    """Draw leaderboard on the right panel"""
    global LEADERBOARD_DATA, LAST_LEADERBOARD_UPDATE
    
    # Update leaderboard every 5 seconds
    current_time = time.time()
    if current_time - LAST_LEADERBOARD_UPDATE > 5:
        LEADERBOARD_DATA = fetch_leaderboard()
        LAST_LEADERBOARD_UPDATE = current_time
    
    start_x = CAMERA_WIDTH + GAME_WIDTH + 20
    start_y = 60
    
    if not LEADERBOARD_DATA:
        draw_text_with_shadow("No scores yet!", tiny_font, WHITE, 
                            CAMERA_WIDTH + GAME_WIDTH + LEADERBOARD_WIDTH // 2, 200)
        return
    
    # Draw top 10 scores
    for i, entry in enumerate(LEADERBOARD_DATA[:10]):
        y = start_y + i * 50
        
        # Rank
        rank = i + 1
        rank_colors = {1: GOLD, 2: SILVER, 3: BRONZE}
        rank_color = rank_colors.get(rank, WHITE)
        
        # Medal for top 3
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"{rank}.")
        
        # Player name
        username = entry['username'][:12] if entry['username'] else "Anonymous"
        score = int(entry['best_score']) if entry['best_score'] else 0
        
        # Draw rank
        draw_text_with_shadow(medal, small_font, rank_color, start_x + 30, y, center=False)
        
        # Draw username
        draw_text_with_shadow(username, tiny_font, WHITE, start_x + 80, y, center=False)
        
        # Draw score
        draw_text_with_shadow(str(score), small_font, rank_color, start_x + 320, y, center=False)

def draw_score_display():
    """Draw current score in game area"""
    score_x = CAMERA_WIDTH + GAME_WIDTH // 2
    score_y = 70
    
    # Player name
    draw_text_with_shadow(f"Player: {USERNAME}", small_font, NEON_BLUE, score_x, score_y - 30)
    
    # Score
    draw_text_with_shadow(f"Score: {SCORE}", game_font, NEON_YELLOW, score_x, score_y)

def draw_game_over_screen():
    """Draw game over overlay"""
    # Semi-transparent overlay
    overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (CAMERA_WIDTH, 0))
    
    center_x = CAMERA_WIDTH + GAME_WIDTH // 2
    center_y = GAME_HEIGHT // 2
    
    # Game Over text
    draw_text_with_shadow("GAME OVER!", title_font, NEON_PINK, center_x, center_y - 100)
    
    # Score
    draw_text_with_shadow(f"Final Score: {SCORE}", game_font, NEON_YELLOW, center_x, center_y)
    
    # Restart instruction
    draw_text_with_shadow("PINCH to Play Again", small_font, NEON_GREEN, center_x, center_y + 80)
    draw_text_with_shadow("ESC for New Player", tiny_font, WHITE, center_x, center_y + 130)

# --- Game Classes ---
class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        # Draw stylized bird
        pygame.draw.circle(self.image, NEON_YELLOW, (20, 20), 20)
        pygame.draw.circle(self.image, WHITE, (25, 15), 5)  # Eye
        self.rect = self.image.get_rect(center=(CAMERA_WIDTH + 150, GAME_HEIGHT // 2))
        self.velocity = 0

    def flap(self):
        self.velocity = BIRD_FLAP

    def update(self):
        self.velocity += GRAVITY
        self.rect.y += int(self.velocity)

        if self.rect.top <= 50:
            self.rect.top = 50
            self.velocity = 0
        
        if self.rect.bottom >= GAME_HEIGHT:
            self.rect.bottom = GAME_HEIGHT
            self.velocity = 0
            return False
        return True

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, is_bottom=True):
        super().__init__()
        self.width = 80
        self.height = random.randint(150, 400)
        
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        # Gradient pipe
        for i in range(self.height):
            ratio = i / self.height
            color = (0, int(150 + 100 * ratio), 0)
            pygame.draw.rect(self.image, color, (0, i, self.width, 1))
        
        # Border
        pygame.draw.rect(self.image, NEON_GREEN, (0, 0, self.width, self.height), 3)
        
        if is_bottom:
            self.rect = self.image.get_rect(bottomleft=(CAMERA_WIDTH + x, GAME_HEIGHT))
        else:
            self.rect = self.image.get_rect(topleft=(CAMERA_WIDTH + x, 50))

    def update(self):
        self.rect.x -= PIPE_SPEED
        if self.rect.right < CAMERA_WIDTH:
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# --- Game Functions ---
def create_pipes():
    """Generate pipe pair"""
    gap_y = random.randint(250, GAME_HEIGHT - 250)
    
    bottom_pipe = Pipe(GAME_WIDTH + 50, is_bottom=True)
    top_pipe = Pipe(GAME_WIDTH + 50, is_bottom=False)
    
    bottom_pipe.rect.top = gap_y + PIPE_GAP // 2
    top_pipe.rect.bottom = gap_y - PIPE_GAP // 2
    
    return bottom_pipe, top_pipe

def reset_game():
    """Reset game state"""
    global bird, pipe_group, SCORE, GAME_STATE, LAST_PIPE, score_pipe_passed, START_TIME
    bird = Bird()
    pipe_group = pygame.sprite.Group()
    SCORE = 0
    GAME_STATE = "PLAYING"
    LAST_PIPE = pygame.time.get_ticks() - PIPE_FREQUENCY + 500
    score_pipe_passed = False
    START_TIME = time.time()

# --- MediaPipe Setup ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# --- OpenCV Setup ---
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
PINCH_THRESHOLD = 30

# --- Initialize ---
bird = Bird()
pipe_group = pygame.sprite.Group()
score_pipe_passed = False

# --- Main Game Loop ---
running = True
while running:
    current_time = pygame.time.get_ticks()
    
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if GAME_STATE == "USERNAME":
                if event.key == pygame.K_RETURN and len(USERNAME) > 0:
                    PLAYER_ID = register_player(USERNAME)
                    reset_game()
                elif event.key == pygame.K_BACKSPACE:
                    USERNAME = USERNAME[:-1]
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.unicode.isprintable() and len(USERNAME) < 15:
                    USERNAME += event.unicode.upper()
            
            elif GAME_STATE == "PLAYING":
                if event.key == pygame.K_SPACE:
                    bird.flap()
            
            elif GAME_STATE == "GAME_OVER":
                if event.key == pygame.K_ESCAPE:
                    GAME_STATE = "USERNAME"
                    USERNAME = ""
                    PLAYER_ID = None

    # --- Gesture Recognition ---
    success, frame = cap.read()
    if success:
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        
        gesture_flap = False

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            
            h, w, _ = frame.shape
            thumb_pos = (int(thumb_tip.x * w), int(thumb_tip.y * h))
            index_pos = (int(index_tip.x * w), int(index_tip.y * h))
            
            cv2.circle(frame, thumb_pos, 10, (255, 0, 255), -1)
            cv2.circle(frame, index_pos, 10, (0, 255, 255), -1)
            
            distance = math.hypot(thumb_pos[0] - index_pos[0], thumb_pos[1] - index_pos[1])
            
            if distance < PINCH_THRESHOLD:
                gesture_flap = True
                cv2.line(frame, thumb_pos, index_pos, (0, 255, 0), 5)
            
            # Display distance
            cv2.putText(frame, f"Pinch: {int(distance)}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Display game state on camera
        state_text = {"USERNAME": "ENTER NAME", "PLAYING": "PLAYING", "GAME_OVER": "GAME OVER"}
        cv2.putText(frame, state_text.get(GAME_STATE, ""), (10, h - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        
        # Convert to pygame surface and display
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (CAMERA_WIDTH, CAMERA_HEIGHT))
        frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        
    # --- Game Logic ---
    if GAME_STATE == "USERNAME":
        draw_username_screen()
        if success:
            screen.blit(frame_surface, (0, 0))
        
        # Allow starting with pinch
        if gesture_flap and len(USERNAME) > 0 and (current_time - LAST_FLAP_TIME > 500):
            PLAYER_ID = register_player(USERNAME)
            reset_game()
            LAST_FLAP_TIME = current_time
    
    elif GAME_STATE == "PLAYING":
        # Handle flap
        if gesture_flap and (current_time - LAST_FLAP_TIME > FLAP_COOLDOWN):
            bird.flap()
            LAST_FLAP_TIME = current_time
        
        # Update
        game_over_by_fall = not bird.update()
        pipe_group.update()
        
        # Create pipes
        if current_time - LAST_PIPE > PIPE_FREQUENCY:
            pipe_pair = create_pipes()
            pipe_group.add(pipe_pair[0])
            pipe_group.add(pipe_pair[1])
            LAST_PIPE = current_time
            score_pipe_passed = False
        
        # Collision
        if pygame.sprite.spritecollide(bird, pipe_group, False) or game_over_by_fall:
            GAME_STATE = "GAME_OVER"
            duration = time.time() - START_TIME
            submit_score(PLAYER_ID, SCORE, duration)
            LEADERBOARD_DATA = fetch_leaderboard()  # Refresh immediately
        
        # Scoring
        if not score_pipe_passed and len(pipe_group) > 0:
            if pipe_group.sprites()[0].rect.right < bird.rect.left:
                SCORE += 1
                score_pipe_passed = True
        
        # Draw
        draw_game_screen()
        if success:
            screen.blit(frame_surface, (0, 0))
        
        # Game area background
        game_bg = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        game_bg.fill((100, 150, 255))
        screen.blit(game_bg, (CAMERA_WIDTH, 0))
        
        pipe_group.draw(screen)
        bird.draw(screen)
        draw_score_display()
        draw_leaderboard()
    
    elif GAME_STATE == "GAME_OVER":
        # Keep last frame
        draw_game_screen()
        if success:
            screen.blit(frame_surface, (0, 0))
        
        # Game area background
        game_bg = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        game_bg.fill((100, 150, 255))
        screen.blit(game_bg, (CAMERA_WIDTH, 0))
        
        pipe_group.draw(screen)
        bird.draw(screen)
        draw_game_over_screen()
        draw_leaderboard()
        
        # Restart with pinch
        if gesture_flap and (current_time - LAST_FLAP_TIME > 500):
            reset_game()
            LAST_FLAP_TIME = current_time

    pygame.display.flip()
    clock.tick(60)

# Cleanup
cap.release()
pygame.quit()
sys.exit()
