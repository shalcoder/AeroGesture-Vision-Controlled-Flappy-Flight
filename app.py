from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Handle database path for deployment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'flappybird.db')

def get_db():
    """Create a database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with required tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Players table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Scores table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (player_id) REFERENCES players (id)
        )
    ''')
    
    # Game sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            duration REAL,
            pipes_passed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (player_id) REFERENCES players (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

@app.route('/')
def index():
    """Serve the dashboard"""
    return render_template('dashboard.html')

@app.route('/leaderboard')
def leaderboard_page():
    """Serve the leaderboard page"""
    return render_template('leaderboard.html')

# ============= API ENDPOINTS =============

@app.route('/api/player/register', methods=['POST'])
def register_player():
    """Register a new player or get existing player"""
    data = request.json
    username = data.get('username', '').strip()
    
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Try to insert new player
        cursor.execute('INSERT INTO players (username) VALUES (?)', (username,))
        conn.commit()
        player_id = cursor.lastrowid
        message = 'Player registered successfully'
    except sqlite3.IntegrityError:
        # Player already exists, get their ID
        cursor.execute('SELECT id FROM players WHERE username = ?', (username,))
        player_id = cursor.fetchone()[0]
        message = 'Player already exists'
    
    conn.close()
    
    return jsonify({
        'success': True,
        'player_id': player_id,
        'username': username,
        'message': message
    })

@app.route('/api/score/submit', methods=['POST'])
def submit_score():
    """Submit a game score"""
    data = request.json
    player_id = data.get('player_id')
    score = data.get('score')
    duration = data.get('duration', 0)
    pipes_passed = data.get('pipes_passed', score)
    
    if not player_id or score is None:
        return jsonify({'error': 'player_id and score are required'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Insert score
    cursor.execute(
        'INSERT INTO scores (player_id, score) VALUES (?, ?)',
        (player_id, score)
    )
    
    # Insert game session
    cursor.execute(
        'INSERT INTO game_sessions (player_id, score, duration, pipes_passed) VALUES (?, ?, ?, ?)',
        (player_id, score, duration, pipes_passed)
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': 'Score submitted successfully',
        'score': score
    })

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get leaderboard data"""
    limit = request.args.get('limit', 10, type=int)
    period = request.args.get('period', 'all')  # all, today, week
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Build query based on period
    query = '''
        SELECT 
            p.username,
            MAX(s.score) as best_score,
            COUNT(s.id) as games_played,
            AVG(s.score) as avg_score,
            p.created_at as joined_date
        FROM players p
        LEFT JOIN scores s ON p.id = s.player_id
    '''
    
    if period == 'today':
        query += " WHERE DATE(s.created_at) = DATE('now') "
    elif period == 'week':
        query += " WHERE DATE(s.created_at) >= DATE('now', '-7 days') "
    
    query += '''
        GROUP BY p.id
        ORDER BY best_score DESC
        LIMIT ?
    '''
    
    cursor.execute(query, (limit,))
    leaderboard = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'success': True,
        'leaderboard': leaderboard,
        'period': period,
        'total_players': len(leaderboard)
    })

@app.route('/api/player/<int:player_id>/stats', methods=['GET'])
def get_player_stats(player_id):
    """Get detailed stats for a specific player"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get player info
    cursor.execute('SELECT * FROM players WHERE id = ?', (player_id,))
    player = cursor.fetchone()
    
    if not player:
        conn.close()
        return jsonify({'error': 'Player not found'}), 404
    
    # Get stats
    cursor.execute('''
        SELECT 
            COUNT(*) as total_games,
            MAX(score) as best_score,
            AVG(score) as avg_score,
            SUM(score) as total_score,
            AVG(duration) as avg_duration
        FROM game_sessions
        WHERE player_id = ?
    ''', (player_id,))
    
    stats = dict(cursor.fetchone())
    
    # Get recent games
    cursor.execute('''
        SELECT score, duration, pipes_passed, created_at
        FROM game_sessions
        WHERE player_id = ?
        ORDER BY created_at DESC
        LIMIT 10
    ''', (player_id,))
    
    recent_games = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'success': True,
        'player': dict(player),
        'stats': stats,
        'recent_games': recent_games
    })

@app.route('/api/stats/global', methods=['GET'])
def get_global_stats():
    """Get global game statistics"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            COUNT(DISTINCT player_id) as total_players,
            COUNT(*) as total_games,
            MAX(score) as highest_score,
            AVG(score) as avg_score,
            SUM(duration) as total_playtime
        FROM game_sessions
    ''')
    
    stats = dict(cursor.fetchone())
    
    # Get top scorer
    cursor.execute('''
        SELECT p.username, MAX(s.score) as score
        FROM players p
        JOIN scores s ON p.id = s.player_id
        GROUP BY p.id
        ORDER BY score DESC
        LIMIT 1
    ''')
    
    top_player = cursor.fetchone()
    if top_player:
        stats['top_player'] = dict(top_player)
    
    conn.close()
    
    return jsonify({
        'success': True,
        'stats': stats
    })

if __name__ == '__main__':
    print("Flappy Bird Multiplayer Server Starting...")
    print("Dashboard: http://localhost:5000")
    print("Leaderboard: http://localhost:5000/leaderboard")
    print("API: http://localhost:5000/api/")
    app.run(debug=True, host='0.0.0.0', port=5000)
