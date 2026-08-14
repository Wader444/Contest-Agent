"""Flask Web Dashboard for Contest Agent Control"""
from flask import Flask, jsonify, render_template_string
from agent.scheduler import ContestAgent

app = Flask(__name__)
agent = ContestAgent()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎯 Weekly Contest Agent</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            max-width: 500px;
            width: 100%;
            box-shadow: 0 25px 50px rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.1);
        }
        h1 { text-align: center; margin-bottom: 10px; font-size: 28px; }
        .subtitle { text-align: center; color: #8892b0; margin-bottom: 30px; font-size: 14px; }
        .status-card {
            background: rgba(0,0,0,0.2);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 25px;
        }
        .status-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
            font-size: 18px;
            font-weight: 600;
        }
        .status-dot {
            width: 12px; height: 12px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        .status-dot.running { background: #00d26a; box-shadow: 0 0 10px #00d26a; }
        .status-dot.stopped { background: #ff4757; }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .info-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            font-size: 14px;
        }
        .info-row:last-child { border-bottom: none; }
        .info-label { color: #8892b0; }
        .info-value { color: #ccd6f6; font-weight: 500; }
        .controls {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 15px;
        }
        .btn {
            padding: 14px 20px;
            border: none;
            border-radius: 10px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        .btn:hover { transform: translateY(-2px); }
        .btn:active { transform: translateY(0); }
        .btn-start { background: linear-gradient(135deg, #00d26a, #00a854); color: #fff; }
        .btn-stop { background: linear-gradient(135deg, #ff4757, #e84118); color: #fff; }
        .btn-run { background: linear-gradient(135deg, #3742fa, #2f3542); color: #fff; grid-column: span 2; }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
        .footer {
            text-align: center;
            margin-top: 20px;
            font-size: 12px;
            color: #8892b0;
        }
        .footer a { color: #64ffda; text-decoration: none; }
        .toast {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            border-radius: 10px;
            color: #fff;
            font-weight: 500;
            opacity: 0;
            transform: translateX(100px);
            transition: all 0.4s ease;
            z-index: 1000;
        }
        .toast.show { opacity: 1; transform: translateX(0); }
        .toast.success { background: #00d26a; }
        .toast.error { background: #ff4757; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Contest Agent</h1>
        <p class="subtitle">Weekly Coding Contest Notifier</p>

        <div class="status-card">
            <div class="status-header">
                <div class="status-dot {{ status.running and 'running' or 'stopped' }}"></div>
                <span>{{ status.running and "Running" or "Stopped" }}</span>
            </div>
            <div class="info-row">
                <span class="info-label">📱 Phone</span>
                <span class="info-value">{{ status.phone }}</span>
            </div>
            <div class="info-row">
                <span class="info-label">🌐 Platforms</span>
                <span class="info-value">{{ status.platforms_enabled | length }} active</span>
            </div>
            <div class="info-row">
                <span class="info-label">⏰ Last Run</span>
                <span class="info-value">{{ status.last_run and status.last_run[:19].replace("T", " ") or "Never" }}</span>
            </div>
            <div class="info-row">
                <span class="info-label">📅 Next Run</span>
                <span class="info-value">{{ status.next_run and status.next_run[:19].replace("T", " ") or "N/A" }}</span>
            </div>
        </div>

        <div class="controls">
            <button class="btn btn-start" onclick="action('/start')" {{ status.running and 'disabled' or '' }}>
                ▶️ Start
            </button>
            <button class="btn btn-stop" onclick="action('/stop')" {{ not status.running and 'disabled' or '' }}>
                ⏹️ Stop
            </button>
            <button class="btn btn-run" onclick="action('/run-now')">
                🚀 Run Now
            </button>
        </div>

        <div class="footer">
            <a href="/status" target="_blank">View JSON Status</a> • 
            <a href="https://github.com/yourusername/coding-contest-agent" target="_blank">GitHub</a>
        </div>
    </div>

    <div class="toast" id="toast"></div>

    <script>
        function action(url) {
            fetch(url)
                .then(r => r.json())
                .then(data => {
                    showToast(data.success ? '✅ Success!' : '❌ Failed', data.success);
                    setTimeout(() => location.reload(), 800);
                })
                .catch(err => showToast('❌ Error: ' + err, false));
        }
        function showToast(msg, success) {
            const t = document.getElementById('toast');
            t.textContent = msg;
            t.className = 'toast ' + (success ? 'success' : 'error') + ' show';
            setTimeout(() => t.classList.remove('show'), 3000);
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    status = agent.status()
    return render_template_string(HTML_TEMPLATE, status=status)

@app.route("/start")
def start():
    success = agent.start()
    return jsonify({"success": success, "running": agent.running})

@app.route("/stop")
def stop():
    success = agent.stop()
    return jsonify({"success": success, "running": agent.running})

@app.route("/run-now")
def run_now():
    # Run in background thread so request doesn't hang
    import threading
    t = threading.Thread(target=agent.run_now)
    t.daemon = True
    t.start()
    return jsonify({"success": True, "message": "Manual run triggered in background"})

import os

@app.route("/status")
@app.route("/api/status")
def status():
    return jsonify(agent.status())

@app.route("/api/run-now")
def api_run_now():
    return run_now()

def run_dashboard(host="0.0.0.0", port=5000):
    """Run the Flask dashboard"""
    if os.getenv("AUTO_START", "true").lower() == "true":
        print("⏰ Auto-starting background scheduler...")
        agent.start()
    print(f"🌐 Dashboard starting at http://{host}:{port}")
    app.run(host=host, port=port, debug=False, use_reloader=False)
