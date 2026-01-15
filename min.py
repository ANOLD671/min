from flask import Flask, render_template_string, request, jsonify, Response
import logging
import time
import os
from datetime import datetime
import requests

app = Flask(__name__)

# Configuration
CONFIG = {
    'app_name': 'Live Sports Channels',
    'version': '3.0',
    'telegram_bot': '@streamer671_bot',
    'telegram_channel': '@livefootball671',
    'github_url': 'https://github.com/yourusername/telegram-sports-app'
}

# Live Streams Data
LIVE_STREAMS = [
    {
        'id': 1,
        'name': 'PREMIER SPORTS',
        'icon': '⚽',
        'category': 'sports',
        'stream_url': 'https://hesgoal.cam/stream/sandbox.html?id=https://lovecdn.ru/daddy.php?stream=beINSPORTSUS',
        'backup_url': 'https://hesgoal.cam/stream/sandbox.html?id=https://lovecdn.ru/daddy.php?stream=beINSPORTSUS',
        'quality': '720p'
    },
    {
        'id': 2,
        'name': 'SKY SPORTS PREMIER LEAGUE',
        'icon': '🔴',
        'category': 'premier_league', 
        'stream_url': 'https://hesgoal.cam/stream/sandbox.html?id=https://lovecdn.ru/daddy.php?stream=SkySportsFootballUK',
        'backup_url': 'https://hesgoal.cam/stream/sandbox.html?id=https://lovecdn.ru/daddy.php?stream=SkySportsFootballUK',
        'quality': '720p'
    },
    {
        'id': 3,
        'name': 'SKY SPORTS MAIN',
        'icon': '📺',
        'category': 'sports',
        'stream_url': 'https://river-3-369.rtbcdn.ru/stream/genetta-312.m9.rutube.ru/oT0wVAMoYwJpS32nJYsInA/1764688448/9585fdae92af45f113fdcc9f6c4ba442/360p_stream.m3u8',
        'backup_url': 'https://river-3-369.rtbcdn.ru/stream/genetta-312.m9.rutube.ru/oT0wVAMoYwJpS32nJYsInA/1764688448/9585fdae92af45f113fdcc9f6c4ba442/360p_stream.m3u8',
        'quality': '720p'
    },
    {
        'id': 4,
        'name': 'LALIGA',
        'icon': '⚽',
        'category': 'sports',
        'stream_url': 'https://hesgoal.cam/stream/sandbox.html?id=https://lovecdn.ru/daddy.php?stream=SkySportsFootballUK',
        'backup_url': 'https://hesgoal.cam/stream/sandbox.html?id=https://lovecdn.ru/daddy.php?stream=SkySportsFootballUK',
        'quality': '720p'
    },
    {
        'id': 5,
        'name': 'SKY SPORTS F1',
        'icon': '🏎️',
        'category': 'racing',
        'stream_url': 'https://river-1.rutube.ru/stream/genetta-311.m9.rutube.ru/cANFchkiqlXk6oqaVyV3cA/1764688524/e5df6984021365a58b3ba22dab2f670a/1080p_stream.m3u8',
        'backup_url': 'https://river-1.rutube.ru/stream/genetta-311.m9.rutube.ru/cANFchkiqlXk6oqaVyV3cA/1764688524/e5df6984021365a58b3ba22dab2f670a/1080p_stream.m3u8',
        'quality': '720p'
    },
    {
        'id': 6,
        'name': 'NBA BASKETBALL',
        'icon': '🏀',
        'category': 'basketball',
        'stream_url': 'https://river-1.rutube.ru/stream/genetta-512.ost.rutube.ru/XtU2cRILbOrnWrnYKTTPCg/1764688569/d01241e9fd2bc2d65dbf6d74cca02f89/1080p_stream.m3u8',
        'backup_url': 'https://river-1.rutube.ru/stream/genetta-512.ost.rutube.ru/XtU2cRILbOrnWrnYKTTPCg/1764688569/d01241e9fd2bc2d65dbf6d74cca02f89/1080p_stream.m3u8',
        'quality': '576p'
    }
]

# HTML Template with embedded CSS and JavaScript
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Sports Channels - Python Flask</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            color: #ffffff;
            min-height: 100vh;
            padding: 20px;
            line-height: 1.6;
        }
        
        .container {
            max-width: 600px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .header h1 {
            font-size: 24px;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #6a11cb, #2575fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .status-indicator {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #4CAF50;
            animation: pulse 2s infinite;
        }
        
        .python-badge {
            background: linear-gradient(135deg, #3776ab, #ffd343);
            color: white;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 12px;
            margin-top: 10px;
            display: inline-block;
        }
        
        .video-container {
            background: #000;
            border-radius: 12px;
            overflow: hidden;
            margin: 20px 0;
            position: relative;
        }
        
        #videoPlayer {
            width: 100%;
            height: 250px;
            display: none;
        }
        
        .video-placeholder {
            width: 100%;
            height: 250px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: #111;
            color: #b8b8b8;
            text-align: center;
        }
        
        .channels-grid {
            display: grid;
            gap: 12px;
            margin: 20px 0;
        }
        
        .channel-card {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }
        
        .channel-card:hover {
            transform: translateY(-2px);
            border-color: #6a11cb;
        }
        
        .channel-card.active {
            background: linear-gradient(135deg, #6a11cb, #2575fc);
            border-color: transparent;
        }
        
        .channel-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 8px;
        }
        
        .channel-icon {
            font-size: 20px;
        }
        
        .channel-name {
            font-weight: 600;
            font-size: 16px;
        }
        
        .channel-info {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            opacity: 0.8;
        }
        
        .controls {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin: 20px 0;
        }
        
        .btn {
            padding: 12px;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #6a11cb, #2575fc);
            color: white;
        }
        
        .btn-success {
            background: linear-gradient(135deg, #00b09b, #96c93d);
            color: white;
        }
        
        .btn-warning {
            background: linear-gradient(135deg, #ff416c, #ff4b2b);
            color: white;
        }
        
        .btn-info {
            background: linear-gradient(135deg, #2196F3, #21CBF3);
            color: white;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            opacity: 0.9;
        }
        
        .telegram-links {
            display: flex;
            gap: 10px;
            margin: 15px 0;
        }
        
        .telegram-links .btn {
            flex: 1;
        }
        
        .footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            opacity: 0.7;
            font-size: 14px;
        }
        
        .toast {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 10px;
            color: white;
            z-index: 1000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transform: translateX(150%);
            transition: transform 0.3s ease;
            max-width: 300px;
        }
        
        .toast.show {
            transform: translateX(0);
        }
        
        .toast.success { background: #4CAF50; }
        .toast.error { background: #f44336; }
        .toast.info { background: #2196F3; }
        .toast.warning { background: #FF9800; }
        
        .hidden {
            display: none !important;
        }
        
        .loading-spinner {
            width: 40px;
            height: 40px;
            border: 4px solid rgba(255, 255, 255, 0.3);
            border-top: 4px solid #2575fc;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 10px;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @media (max-width: 480px) {
            .container {
                padding: 10px;
            }
            
            .controls {
                grid-template-columns: 1fr;
            }
            
            #videoPlayer, .video-placeholder {
                height: 200px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚽ Live Sports Channels</h1>
            <div class="status-indicator">
                <span class="status-dot"></span>
                <span>All Systems Operational</span>
            </div>
            <div class="python-badge">Powered by Python Flask</div>
        </div>
        
        <!-- Video Player -->
        <div class="video-container">
            <video id="videoPlayer" controls playsinline webkit-playsinline>
                Your browser doesn't support video playback.
            </video>
            <div id="videoPlaceholder" class="video-placeholder">
                <div class="loading-spinner"></div>
                <p>Select a channel to start streaming</p>
                <small>Powered by {{ config.telegram_bot }}</small>
            </div>
        </div>
        
        <!-- Channels List -->
        <div class="channels-grid" id="channelsGrid">
            <!-- Channels will be loaded dynamically -->
        </div>
        
        <!-- Controls -->
        <div class="controls">
            <button class="btn btn-info" onclick="showAppInfo()">ℹ️ App Info</button>
            <button class="btn btn-primary" onclick="reloadStream()">🔄 Reload Stream</button>
            <button class="btn btn-success" onclick="checkAllStreams()">📡 Check Streams</button>
            <button class="btn btn-warning" onclick="closeApp()">❌ Close App</button>
        </div>
        
        <!-- Telegram Links -->
        <div class="telegram-links">
            <button class="btn btn-primary" onclick="openTelegramChannel()">📢 {{ config.telegram_channel }}</button>
            <button class="btn btn-primary" onclick="openTelegramBot()">🤖 {{ config.telegram_bot }}</button>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p><strong>Backend:</strong> Python Flask | <strong>Version:</strong> {{ config.version }}</p>
            <p><strong>Stream Source:</strong> {{ config.telegram_bot }} | <strong>Updates:</strong> {{ config.telegram_channel }}</p>
            <p>All streams are provided by {{ config.telegram_bot }}</p>
        </div>
    </div>
    
    <!-- Toast Container -->
    <div id="toastContainer"></div>

    <script>
        // Configuration
        const CONFIG = {{ config|tojson }};
        const STREAMS = {{ streams|tojson }};
        
        // Global variables
        let currentStream = null;
        let tg = null;
        
        // Initialize app
        function initializeApp() {
            loadChannels();
            setupTelegram();
            setupEventListeners();
            showToast('Python Flask App Ready!', 'success');
        }
        
        // Load channels into the grid
        function loadChannels() {
            const grid = document.getElementById('channelsGrid');
            grid.innerHTML = '';
            
            STREAMS.forEach(stream => {
                const channelCard = document.createElement('div');
                channelCard.className = 'channel-card';
                channelCard.innerHTML = `
                    <div class="channel-header">
                        <span class="channel-icon">${stream.icon}</span>
                        <span class="channel-name">${stream.name}</span>
                    </div>
                    <div class="channel-info">
                        <span>${stream.category.toUpperCase()}</span>
                        <span>${stream.quality}</span>
                    </div>
                `;
                
                channelCard.addEventListener('click', () => playStream(stream));
                grid.appendChild(channelCard);
            });
        }
        
        // Play selected stream
        function playStream(stream) {
            if (currentStream?.id === stream.id) {
                // Toggle play/pause if same stream
                const video = document.getElementById('videoPlayer');
                if (video.paused) {
                    video.play().catch(e => showToast('Tap play button to start', 'info'));
                } else {
                    video.pause();
                }
                return;
            }
            
            currentStream = stream;
            
            // Update UI
            document.querySelectorAll('.channel-card').forEach(card => card.classList.remove('active'));
            event.currentTarget.classList.add('active');
            
            const video = document.getElementById('videoPlayer');
            const placeholder = document.getElementById('videoPlaceholder');
            
            // Show loading
            placeholder.style.display = 'flex';
            video.style.display = 'none';
            
            // Set video source
            video.src = stream.stream_url;
            video.load();
            
            showToast(`Loading ${stream.name}...`, 'info');
            
            // Try to play automatically
            video.play().then(() => {
                placeholder.style.display = 'none';
                video.style.display = 'block';
                showToast(`Now playing: ${stream.name}`, 'success');
            }).catch(error => {
                // Autoplay failed, show play button
                placeholder.innerHTML = `
                    <div style="text-align: center;">
                        <div style="font-size: 48px; margin-bottom: 10px;">${stream.icon}</div>
                        <p>${stream.name}</p>
                        <button onclick="startPlayback()" style="
                            background: linear-gradient(135deg, #6a11cb, #2575fc);
                            color: white;
                            border: none;
                            padding: 10px 20px;
                            border-radius: 20px;
                            margin: 10px 0;
                            cursor: pointer;
                        ">▶️ Play Stream</button>
                        <small>Tap play to start streaming</small>
                    </div>
                `;
                showToast('Tap play to start streaming', 'info');
            });
        }
        
        // Start playback manually
        function startPlayback() {
            const video = document.getElementById('videoPlayer');
            const placeholder = document.getElementById('videoPlaceholder');
            
            video.play().then(() => {
                placeholder.style.display = 'none';
                video.style.display = 'block';
            }).catch(error => {
                showToast('Failed to play stream', 'error');
            });
        }
        
        // Reload current stream
        function reloadStream() {
            if (currentStream) {
                const video = document.getElementById('videoPlayer');
                const currentTime = video.currentTime;
                const wasPlaying = !video.paused;
                
                video.src = currentStream.stream_url;
                video.currentTime = currentTime;
                
                if (wasPlaying) {
                    video.play().catch(console.error);
                }
                
                showToast('Stream reloaded', 'success');
            } else {
                showToast('Select a channel first', 'warning');
            }
        }
        
        // Check all streams status
        async function checkAllStreams() {
            showToast('Checking stream status...', 'info');
            
            try {
                const response = await fetch('/api/streams/status');
                const data = await response.json();
                
                let working = 0;
                data.streams_status.forEach(stream => {
                    if (stream.status === 'online') working++;
                });
                
                showToast(`${working}/${data.streams_status.length} streams working`, 'success');
            } catch (error) {
                showToast('Error checking streams', 'error');
            }
        }
        
        // Telegram integration
        function setupTelegram() {
            if (window.Telegram && window.Telegram.WebApp) {
                tg = window.Telegram.WebApp;
                tg.expand();
                tg.ready();
                showToast('Telegram Mini App Activated!', 'success');
            }
        }
        
        // Telegram functions
        function openTelegramChannel() {
            window.open(`https://t.me/${CONFIG.telegram_channel.replace('@', '')}`, '_blank');
            showToast('Opening Telegram channel...', 'info');
        }
        
        function openTelegramBot() {
            window.open(`https://t.me/${CONFIG.telegram_bot.replace('@', '')}`, '_blank');
            showToast('Opening Telegram bot...', 'info');
        }
        
        function closeApp() {
            if (tg && tg.close) {
                tg.close();
            } else {
                showToast('In Telegram, this would close the app', 'info');
            }
        }
        
        // App info
        function showAppInfo() {
            alert(`${CONFIG.app_name} v${CONFIG.version}

Powered by Python Flask Backend

Features:
• Live sports streaming
• Multiple channels
• Telegram Mini App optimized
• Mobile responsive
• Real-time stream checking

Supported Platforms:
✅ Android devices
✅ iOS devices  
✅ Windows PCs
✅ Mac computers
✅ Telegram Mini Apps

Backend: Python Flask
Stream Source: ${CONFIG.telegram_bot}
Updates: ${CONFIG.telegram_channel}

All streams provided by ${CONFIG.telegram_bot}`);
        }
        
        // Event listeners
        function setupEventListeners() {
            const video = document.getElementById('videoPlayer');
            
            video.addEventListener('loadstart', () => {
                showToast('Loading stream...', 'info');
            });
            
            video.addEventListener('canplay', () => {
                showToast('Stream ready!', 'success');
            });
            
            video.addEventListener('error', () => {
                showToast('Stream error. Trying backup...', 'error');
                if (currentStream && currentStream.backup_url) {
                    video.src = currentStream.backup_url;
                    video.load();
                }
            });
            
            video.addEventListener('waiting', () => {
                showToast('Buffering...', 'info');
            });
        }
        
        // Toast notification system
        function showToast(message, type = 'info', duration = 3000) {
            const container = document.getElementById('toastContainer');
            const toast = document.createElement('div');
            toast.className = `toast ${type}`;
            toast.textContent = message;
            
            container.appendChild(toast);
            
            setTimeout(() => toast.classList.add('show'), 10);
            
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 300);
            }, duration);
        }
        
        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', initializeApp);
    </script>
</body>
</html>
'''

# Routes
@app.route('/')
def index():
    """Main page serving the Telegram Mini App"""
    return render_template_string(HTML_TEMPLATE, 
                                config=CONFIG, 
                                streams=LIVE_STREAMS)

@app.route('/api/streams')
def get_streams():
    """API endpoint to get all streams"""
    return jsonify({
        'status': 'success',
        'streams': LIVE_STREAMS,
        'timestamp': datetime.now().isoformat(),
        'total_streams': len(LIVE_STREAMS)
    })

@app.route('/api/streams/status')
def get_streams_status():
    """Check status of all streams"""
    streams_status = []
    
    for stream in LIVE_STREAMS:
        try:
            # Simple HEAD request to check if stream is accessible
            response = requests.head(stream['stream_url'], timeout=5)
            status = 'online' if response.status_code == 200 else 'offline'
        except:
            status = 'offline'
        
        streams_status.append({
            'id': stream['id'],
            'name': stream['name'],
            'status': status,
            'last_checked': datetime.now().isoformat()
        })
    
    return jsonify({
        'status': 'success',
        'streams_status': streams_status,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/stream/<int:stream_id>')
def get_stream(stream_id):
    """Get specific stream information"""
    stream = next((s for s in LIVE_STREAMS if s['id'] == stream_id), None)
    
    if not stream:
        return jsonify({'status': 'error', 'message': 'Stream not found'}), 404
    
    return jsonify({
        'status': 'success',
        'stream': stream
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'app': CONFIG['app_name'],
        'version': CONFIG['version'],
        'timestamp': datetime.now().isoformat(),
        'uptime': time.time() - app_start_time,
        'streams_count': len(LIVE_STREAMS)
    })

@app.route('/api/telegram/init')
def telegram_init():
    """Telegram Web App initialization endpoint"""
    init_data = request.args.get('initData', '')
    
    return jsonify({
        'status': 'success',
        'app_name': CONFIG['app_name'],
        'version': CONFIG['version'],
        'features': {
            'video_streaming': True,
            'multiple_channels': True,
            'stream_status_check': True,
            'telegram_integration': True
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/device/info')
def device_info():
    """Get device information"""
    user_agent = request.headers.get('User-Agent', '')
    
    device_info = {
        'user_agent': user_agent,
        'is_mobile': any(device in user_agent.lower() for device in ['mobile', 'android', 'iphone']),
        'is_telegram': 'telegram' in user_agent.lower(),
        'is_android': 'android' in user_agent.lower(),
        'is_ios': 'iphone' in user_agent.lower() or 'ipad' in user_agent.lower(),
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify(device_info)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

# Stream proxy endpoint (optional - for CORS issues)
@app.route('/proxy/stream/<int:stream_id>')
def proxy_stream(stream_id):
    """Proxy stream to handle CORS issues"""
    stream = next((s for s in LIVE_STREAMS if s['id'] == stream_id), None)
    
    if not stream:
        return jsonify({'status': 'error', 'message': 'Stream not found'}), 404
    
    try:
        response = requests.get(stream['stream_url'], stream=True)
        return Response(
            response.iter_content(chunk_size=8192),
            content_type=response.headers.get('content-type', 'video/mp4'),
            headers={
                'Access-Control-Allow-Origin': '*',
                'Cache-Control': 'no-cache'
            }
        )
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app_start_time = time.time()
    
    print(f"""
    🚀 Starting {CONFIG['app_name']} v{CONFIG['version']}
    📱 Telegram Bot: {CONFIG['telegram_bot']}
    📢 Telegram Channel: {CONFIG['telegram_channel']}
    🎥 Live Streams: {len(LIVE_STREAMS)} channels
    🌐 Server will run on port 5000
    
    Endpoints:
    • / - Main Mini App
    • /api/streams - Get all streams
    • /api/streams/status - Check stream status
    • /api/health - Health check
    • /api/telegram/init - Telegram init
    
    Press Ctrl+C to stop the server
    """)
    
    # REMOVE SSL FOR RENDER - They provide HTTPS automatically
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False  # Set to False for production
    )
