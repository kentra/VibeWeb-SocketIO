import json
from typing import Any

import socketio

from app.connections import manager
from app.message_log import msg_logger

_sio: socketio.AsyncServer | None = None


def set_socketio_server(sio: socketio.AsyncServer) -> None:
    global _sio
    _sio = sio


def get_dashboard_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VibeWeb SocketIO Dashboard</title>
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a2e; color: #eee; min-height: 100vh; padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { margin-bottom: 20px; color: #00d4ff; }
        .stats {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px; margin-bottom: 30px;
        }
        .stat-card { background: #16213e; border-radius: 8px; padding: 20px; text-align: center; }
        .stat-value { font-size: 2.5em; font-weight: bold; color: #00d4ff; }
        .stat-label { color: #888; margin-top: 5px; }
        .panel { background: #16213e; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
        .panel h2 { margin-bottom: 15px; color: #00d4ff; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #2a2a4a; }
        th { color: #888; font-weight: 500; }
        .sid { font-family: monospace; color: #00d4ff; }
        .ip { font-family: monospace; color: #aaa; }
        .rooms { display: flex; flex-wrap: wrap; gap: 5px; }
        .room-tag { background: #0f3460; padding: 3px 8px; border-radius: 4px; font-size: 0.85em; }
        .empty { text-align: center; padding: 40px; color: #666; }
        .status {
            display: inline-block; width: 10px; height: 10px;
            border-radius: 50%; background: #00ff00; margin-right: 8px;
        }
        .status.disconnected { background: #ff4444; }
        .btn {
            background: #e74c3c; border: none; padding: 6px 12px;
            border-radius: 4px; cursor: pointer; color: white; font-size: 0.85em;
        }
        .btn:hover { background: #c0392b; }
        .btn:disabled { background: #555; cursor: not-allowed; }
        .clear-btn {
            background: #3498db; border: none; padding: 8px 16px;
            border-radius: 4px; cursor: pointer; color: white; margin-bottom: 10px;
        }
        .clear-btn:hover { background: #2980b9; }
        .log-container { max-height: 400px; overflow-y: auto; }
        .log-entry {
            padding: 8px 12px; border-bottom: 1px solid #2a2a4a;
            font-family: monospace; font-size: 0.85em;
        }
        .log-entry:nth-child(odd) { background: rgba(255,255,255,0.02); }
        .log-time { color: #666; margin-right: 10px; }
        .log-event { color: #00d4ff; margin-right: 10px; min-width: 100px; display: inline-block; }
        .log-from { color: #f39c12; margin-right: 10px; }
        .log-room { color: #9b59b6; margin-right: 10px; }
        .log-data { color: #2ecc71; word-break: break-all; }
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; }
        .tab {
            background: #16213e; border: none; padding: 10px 20px;
            border-radius: 4px; cursor: pointer; color: #888;
        }
        .tab.active { background: #00d4ff; color: #1a1a2e; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .toast {
            position: fixed; bottom: 20px; right: 20px;
            background: #2ecc71; color: white; padding: 12px 20px;
            border-radius: 4px; display: none;
        }
        .toast.error { background: #e74c3c; }
    </style>
</head>
<body>
    <div class="container">
        <h1><span class="status" id="ws-status"></span>VibeWeb SocketIO Dashboard</h1>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value" id="conn-count">0</div>
                <div class="stat-label">Active Connections</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="msg-count">0</div>
                <div class="stat-label">Messages Logged</div>
            </div>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="showTab('connections')">Connections</button>
            <button class="tab" onclick="showTab('logs')">Message Log</button>
        </div>

        <div id="connections-tab" class="tab-content active">
            <div class="panel">
                <h2>Connections</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Session ID</th>
                            <th>Client IP</th>
                            <th>Connected At</th>
                            <th>Rooms</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="connections-body">
                    </tbody>
                </table>
                <div class="empty" id="empty-msg">No active connections</div>
            </div>
        </div>

        <div id="logs-tab" class="tab-content">
            <div class="panel">
                <h2>Message Traffic</h2>
                <button class="clear-btn" onclick="clearLogs()">Clear Logs</button>
                <div class="log-container" id="log-container">
                    <div class="empty" id="empty-logs">No messages logged</div>
                </div>
            </div>
        </div>
    </div>
    <div class="toast" id="toast"></div>
    <script>
        let socket;
        let connections = {};
        let logs = [];

        function showToast(message, isError = false) {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.className = isError ? 'toast error' : 'toast';
            toast.style.display = 'block';
            setTimeout(() => toast.style.display = 'none', 3000);
        }

        function showTab(tabName) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            document.querySelector('.tab[onclick="showTab(\\''+tabName+'\\')"]').classList.add('active');
            document.getElementById(tabName+'-tab').classList.add('active');
        }

        function updateConnectionCount() {
            document.getElementById('conn-count').textContent = Object.keys(connections).length;
        }

        function renderConnections() {
            const tbody = document.getElementById('connections-body');
            const emptyMsg = document.getElementById('empty-msg');
            const connList = Object.values(connections);

            if (connList.length === 0) {
                tbody.innerHTML = '';
                emptyMsg.style.display = 'block';
            } else {
                emptyMsg.style.display = 'none';
                tbody.innerHTML = connList.map(c => '<tr>' +
                    '<td class="sid">' + c.sid + '</td>' +
                    '<td class="ip">' + (c.client_ip || '-') + '</td>' +
                    '<td>' + new Date(c.connected_at).toLocaleString() + '</td>' +
                    '<td><div class="rooms">' +
                    (c.rooms || []).map(r => '<span class="room-tag">'+r+'</span>').join('') +
                    '</div></td>' +
                    '<td><button class="btn" onclick="disconnectClient(\\''+c.sid+'\\')">' +
                    'Disconnect</button></td>' +
                    '</tr>').join('');
            }
            updateConnectionCount();
        }

        async function disconnectClient(sid) {
            if (!confirm('Disconnect client ' + sid + '?')) return;
            try {
                const res = await fetch('/api/disconnect/' + sid, { method: 'POST' });
                const data = await res.json();
                if (data.status === 'disconnected') {
                    showToast('Client ' + sid.substring(0,8) + ' disconnected');
                } else {
                    showToast(data.message || 'Failed to disconnect', true);
                }
            } catch (err) {
                showToast('Error disconnecting client', true);
            }
        }

        async function clearLogs() {
            try {
                const res = await fetch('/api/logs/clear', { method: 'POST' });
                const data = await res.json();
                if (data.status === 'cleared') {
                    logs = [];
                    renderLogs();
                    showToast('Logs cleared');
                }
            } catch (err) {
                showToast('Error clearing logs', true);
            }
        }

        function renderLogs() {
            const container = document.getElementById('log-container');

            document.getElementById('msg-count').textContent = logs.length;

            if (logs.length === 0) {
                container.innerHTML = '<div class="empty" id="empty-logs">No messages logged</div>';
            } else {
                container.innerHTML = logs.slice().reverse().map(l => {
                    const time = new Date(l.timestamp).toLocaleTimeString();
                    const from = l.from ? '<span class="log-from">['+l.from+']</span>' : '';
                    const room = l.room ? '<span class="log-room">to '+l.room+'</span>' : '';
                    const dataStr = l.data ? JSON.stringify(l.data) : '';
                    return '<div class="log-entry">' +
                        '<span class="log-time">' + time + '</span>' +
                        '<span class="log-event">' + l.event + '</span>' +
                        from + room +
                        '<span class="log-data">' + dataStr + '</span></div>';
                }).join('');
            }
        }

        async function loadInitialData() {
            try {
                const res = await fetch('/api/connections');
                const data = await res.json();
                connections = {};
                data.connections.forEach(c => connections[c.sid] = c);
                renderConnections();
            } catch (err) {
                console.error('Failed to load connections:', err);
            }

            try {
                const res = await fetch('/api/logs');
                const data = await res.json();
                logs = data.logs || [];
                renderLogs();
            } catch (err) {
                console.error('Failed to load logs:', err);
            }
        }

        function connectWebSocket() {
            socket = io(window.location.origin, { transports: ['websocket', 'polling'] });

            socket.on('connect', () => {
                socket.emit('join_room', 'admin_room');
                document.getElementById('ws-status').classList.remove('disconnected');
            });

            socket.on('disconnect', () => {
                document.getElementById('ws-status').classList.add('disconnected');
            });

            socket.on('admin:connection', (data) => {
                connections[data.sid] = { ...data, rooms: [] };
                renderConnections();
                showToast('Client connected: ' + data.sid.substring(0,8) + '...');
            });

            socket.on('admin:disconnection', (data) => {
                delete connections[data.sid];
                renderConnections();
                showToast('Client disconnected: ' + data.sid.substring(0,8) + '...');
            });

            socket.on('admin:message', (data) => {
                logs.push(data);
                renderLogs();
            });
        }

        loadInitialData();
        connectWebSocket();
    </script>
</body>
</html>"""


def get_connections_json() -> str:
    connections = [
        {
            "sid": c.sid,
            "client_ip": c.client_ip,
            "connected_at": c.connected_at.isoformat(),
            "rooms": list(c.rooms),
        }
        for c in manager.all()
    ]
    return json.dumps({"count": manager.count(), "connections": connections})


def get_logs_json() -> str:
    logs = [
        {
            "event": log.event,
            "from": log.from_sid,
            "room": log.to_room,
            "data": log.data,
            "timestamp": log.timestamp.isoformat(),
        }
        for log in msg_logger.all()
    ]
    return json.dumps({"count": len(logs), "logs": logs})


async def dashboard_app(scope: dict[str, Any], receive: Any, send: Any) -> None:
    if scope["type"] != "http":
        return

    path = scope["path"]
    method = scope["method"]

    if path == "/" or path == "/dashboard":
        response = get_dashboard_html()
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [[b"content-type", b"text/html; charset=utf-8"]],
            }
        )
        await send({"type": "http.response.body", "body": response.encode()})
    elif path == "/api/connections":
        response = get_connections_json()
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [[b"content-type", b"application/json"]],
            }
        )
        await send({"type": "http.response.body", "body": response.encode()})
    elif path == "/api/logs":
        response = get_logs_json()
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [[b"content-type", b"application/json"]],
            }
        )
        await send({"type": "http.response.body", "body": response.encode()})
    elif path == "/api/logs/clear" and method == "POST":
        msg_logger.clear()
        response = json.dumps({"status": "cleared"})
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [[b"content-type", b"application/json"]],
            }
        )
        await send({"type": "http.response.body", "body": response.encode()})
    elif path.startswith("/api/disconnect/") and method == "POST":
        sid = path.split("/api/disconnect/")[-1]
        if _sio is None:
            response = json.dumps({"status": "error", "message": "Server not initialized"})
            await send(
                {
                    "type": "http.response.start",
                    "status": 500,
                    "headers": [[b"content-type", b"application/json"]],
                }
            )
            await send({"type": "http.response.body", "body": response.encode()})
        elif manager.get(sid) is None:
            response = json.dumps({"status": "error", "message": "Client not found"})
            await send(
                {
                    "type": "http.response.start",
                    "status": 404,
                    "headers": [[b"content-type", b"application/json"]],
                }
            )
            await send({"type": "http.response.body", "body": response.encode()})
        else:
            await _sio.disconnect(sid)
            response = json.dumps({"status": "disconnected", "sid": sid})
            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [[b"content-type", b"application/json"]],
                }
            )
            await send({"type": "http.response.body", "body": response.encode()})
    else:
        await send(
            {
                "type": "http.response.start",
                "status": 404,
                "headers": [[b"content-type", b"text/plain"]],
            }
        )
        await send({"type": "http.response.body", "body": b"Not Found"})
