import json

from app.connections import manager


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
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { margin-bottom: 20px; color: #00d4ff; }
        .stats {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px; margin-bottom: 30px;
        }
        .stat-card { background: #16213e; border-radius: 8px; padding: 20px; text-align: center; }
        .stat-value { font-size: 2.5em; font-weight: bold; color: #00d4ff; }
        .stat-label { color: #888; margin-top: 5px; }
        .connections { background: #16213e; border-radius: 8px; padding: 20px; }
        .connections h2 { margin-bottom: 15px; color: #00d4ff; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #2a2a4a; }
        th { color: #888; font-weight: 500; }
        .sid { font-family: monospace; color: #00d4ff; }
        .ip { font-family: monospace; color: #aaa; }
        .rooms { display: flex; flex-wrap: wrap; gap: 5px; }
        .room-tag { background: #0f3460; padding: 3px 8px; border-radius: 4px; font-size: 0.85em; }
        .empty { text-align: center; padding: 40px; color: #666; }
        .refresh-btn {
            background: #00d4ff; border: none; padding: 10px 20px;
            border-radius: 4px; cursor: pointer; margin-bottom: 20px;
        }
        .refresh-btn:hover { background: #00a8cc; }
        .status {
            display: inline-block; width: 10px; height: 10px;
            border-radius: 50%; background: #00ff00; margin-right: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1><span class="status"></span>VibeWeb SocketIO Dashboard</h1>
        <button class="refresh-btn" onclick="loadData()">Refresh</button>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value" id="conn-count">0</div>
                <div class="stat-label">Active Connections</div>
            </div>
        </div>
        <div class="connections">
            <h2>Connections</h2>
            <table>
                <thead>
                    <tr>
                        <th>Session ID</th>
                        <th>Client IP</th>
                        <th>Connected At</th>
                        <th>Rooms</th>
                    </tr>
                </thead>
                <tbody id="connections-body">
                </tbody>
            </table>
            <div class="empty" id="empty-msg">No active connections</div>
        </div>
    </div>
    <script>
        async function loadData() {
            const res = await fetch('/api/connections');
            const data = await res.json();

            document.getElementById('conn-count').textContent = data.count;
            const tbody = document.getElementById('connections-body');
            const emptyMsg = document.getElementById('empty-msg');

            if (data.connections.length === 0) {
                tbody.innerHTML = '';
                emptyMsg.style.display = 'block';
            } else {
                emptyMsg.style.display = 'none';
                tbody.innerHTML = data.connections.map(c => `
                    <tr>
                        <td class="sid">${c.sid}</td>
                        <td class="ip">${c.client_ip || '-'}</td>
                        <td>${new Date(c.connected_at).toLocaleString()}</td>
                        <td>
                            <div class="rooms">
                                ${c.rooms.map(r => `<span class="room-tag">${r}</span>`).join('')}
                            </div>
                        </td>
                    </tr>
                `).join('');
            }
        }
        loadData();
        setInterval(loadData, 5000);
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


async def dashboard_app(scope, receive, send):
    if scope["type"] != "http":
        return

    path = scope["path"]

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
    else:
        await send(
            {
                "type": "http.response.start",
                "status": 404,
                "headers": [[b"content-type", b"text/plain"]],
            }
        )
        await send({"type": "http.response.body", "body": b"Not Found"})
