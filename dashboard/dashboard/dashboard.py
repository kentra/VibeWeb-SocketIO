from typing import Any

import reflex as rx
import socketio
from pydantic import BaseModel

_socket_client: socketio.Client | None = None


class Connection(BaseModel):
    sid: str = ""
    connected_at: str = ""
    rooms: list[str] = []
    user_agent: str = "Unknown"


class DashboardState(rx.State):
    connections: list[Connection] = []
    total_connections: int = 0
    is_connected: bool = False
    server_url: str = "http://localhost:8000"
    connection_status: str = "Disconnected"
    selected_connection: Connection | None = None

    def set_server_url(self, value: str) -> None:
        self.server_url = value

    def connect_to_server(self) -> None:
        global _socket_client

        if _socket_client and _socket_client.connected:
            return

        _socket_client = socketio.Client()

        state = self

        @_socket_client.event
        def connect():
            state.is_connected = True
            state.connection_status = "Connected"
            _socket_client.emit("admin_subscribe")

        @_socket_client.event
        def disconnect():
            state.is_connected = False
            state.connection_status = "Disconnected"

        @_socket_client.on("admin:connection_update")
        def on_connection_update(data):
            state.handle_connection_update(data)

        @_socket_client.on("admin:room_update")
        def on_room_update(data):
            state.handle_room_update(data)

        try:
            _socket_client.connect(self.server_url)
            self.connection_status = "Connecting..."
        except Exception as e:
            self.connection_status = f"Error: {str(e)}"
            self.is_connected = False

    def disconnect_from_server(self) -> None:
        global _socket_client

        if _socket_client and _socket_client.connected:
            _socket_client.disconnect()
        _socket_client = None
        self.is_connected = False
        self.connection_status = "Disconnected"
        self.connections = []
        self.total_connections = 0

    def handle_connection_update(self, data: dict[str, Any]) -> None:
        update_type = data.get("type")
        connection_data = data.get("connection", {})
        total = data.get("total", 0)

        if update_type == "connect":
            existing = next(
                (c for c in self.connections if c.sid == connection_data.get("sid")), None
            )
            if not existing:
                client_info = connection_data.get("client_info", {})
                conn = Connection(
                    sid=connection_data.get("sid", ""),
                    connected_at=connection_data.get("connected_at", ""),
                    rooms=connection_data.get("rooms", []),
                    user_agent=client_info.get("user_agent", "Unknown") or "Unknown",
                )
                self.connections.insert(0, conn)
        elif update_type == "disconnect":
            self.connections = [c for c in self.connections if c.sid != connection_data.get("sid")]

        self.total_connections = total

    def handle_room_update(self, data: dict[str, Any]) -> None:
        update_type = data.get("type")
        sid = data.get("sid")
        room = data.get("room")

        for conn in self.connections:
            if conn.sid == sid:
                if update_type == "join" and room not in conn.rooms:
                    conn.rooms.append(room)
                elif update_type == "leave" and room in conn.rooms:
                    conn.rooms.remove(room)

    def refresh_connections(self) -> None:
        global _socket_client

        if _socket_client and _socket_client.connected:
            result = _socket_client.call("admin_get_connections")
            if result:
                self.connections = [
                    Connection(
                        sid=c.get("sid", ""),
                        connected_at=c.get("connected_at", ""),
                        rooms=c.get("rooms", []),
                        user_agent=c.get("client_info", {}).get("user_agent", "Unknown")
                        or "Unknown",
                    )
                    for c in result.get("connections", [])
                ]
                self.total_connections = result.get("total", 0)

    def select_connection(self, sid: str) -> None:
        self.selected_connection = next((c for c in self.connections if c.sid == sid), None)

    def clear_selection(self) -> None:
        self.selected_connection = None


def connection_card(conn: Connection) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.badge(
                    conn.sid[:8],
                    color_scheme="blue",
                    variant="soft",
                ),
                rx.text(
                    conn.connected_at[:19],
                    size="2",
                    color="gray",
                ),
                justify="between",
                width="100%",
            ),
            rx.hstack(
                rx.text("Rooms:", size="2", weight="bold"),
                rx.hstack(
                    rx.foreach(
                        conn.rooms,
                        lambda room: rx.badge(
                            room, color_scheme="green", variant="outline", size="1"
                        ),
                    ),
                    wrap="wrap",
                ),
                align="start",
                width="100%",
            ),
            rx.box(
                rx.text("Client Info:", size="2", weight="bold"),
                rx.text(
                    conn.user_agent[:50],
                    size="1",
                    color="gray",
                ),
                width="100%",
            ),
            align="start",
            width="100%",
        ),
        width="100%",
        on_click=lambda: DashboardState.select_connection(conn.sid),
        cursor="pointer",
        _hover={"bg": rx.color("gray", 3)},
    )


def connection_detail() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Connection Details"),
            rx.dialog.description(
                rx.cond(
                    DashboardState.selected_connection,
                    DashboardState.selected_connection.sid,
                    "",
                ),
                size="2",
            ),
            rx.vstack(
                rx.text(
                    "Connected At:",
                    weight="bold",
                    size="2",
                ),
                rx.text(
                    rx.cond(
                        DashboardState.selected_connection,
                        DashboardState.selected_connection.connected_at,
                        "N/A",
                    ),
                    size="2",
                ),
                rx.divider(),
                rx.text("Rooms:", weight="bold", size="2"),
                rx.foreach(
                    DashboardState.selected_connection.rooms,
                    lambda room: rx.badge(room, color_scheme="green"),
                ),
                rx.divider(),
                rx.text("User Agent:", weight="bold", size="2"),
                rx.text(
                    rx.cond(
                        DashboardState.selected_connection,
                        DashboardState.selected_connection.user_agent,
                        "Unknown",
                    ),
                    size="2",
                ),
                width="100%",
                margin_top="1rem",
            ),
            rx.hstack(
                rx.dialog.close(
                    rx.button("Close", variant="soft"),
                ),
                justify="end",
                margin_top="1rem",
            ),
            max_width="500px",
        ),
        open=DashboardState.selected_connection is not None,
        on_open_change=DashboardState.clear_selection,
    )


def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.hstack(
                rx.heading("SocketIO Dashboard", size="8"),
                rx.badge(
                    f"{DashboardState.total_connections} connections",
                    color_scheme=rx.cond(DashboardState.is_connected, "green", "gray"),
                    size="2",
                ),
                justify="between",
                width="100%",
            ),
            rx.card(
                rx.hstack(
                    rx.hstack(
                        rx.box(
                            rx.box(
                                width="10px",
                                height="10px",
                                border_radius="50%",
                                bg=rx.cond(DashboardState.is_connected, "green", "red"),
                            ),
                            style=rx.cond(
                                DashboardState.is_connected,
                                {"animation": "pulse 2s infinite"},
                                {},
                            ),
                        ),
                        rx.text(
                            DashboardState.connection_status,
                            size="3",
                            weight="medium",
                        ),
                    ),
                    rx.hstack(
                        rx.input(
                            placeholder="Server URL",
                            value=DashboardState.server_url,
                            on_change=DashboardState.set_server_url,
                            size="2",
                            width="250px",
                        ),
                        rx.button(
                            "Connect",
                            on_click=DashboardState.connect_to_server,
                            disabled=DashboardState.is_connected,
                            size="2",
                        ),
                        rx.button(
                            "Disconnect",
                            on_click=DashboardState.disconnect_from_server,
                            disabled=~DashboardState.is_connected,
                            variant="soft",
                            color_scheme="red",
                            size="2",
                        ),
                        rx.button(
                            "Refresh",
                            on_click=DashboardState.refresh_connections,
                            disabled=~DashboardState.is_connected,
                            variant="outline",
                            size="2",
                        ),
                    ),
                    justify="between",
                    width="100%",
                ),
                width="100%",
            ),
            rx.box(
                rx.foreach(
                    DashboardState.connections,
                    connection_card,
                ),
                width="100%",
                max_height="60vh",
                overflow_y="auto",
            ),
            connection_detail(),
            align="start",
            width="100%",
            spacing="4",
        ),
        max_width="800px",
        padding_y="2rem",
    )


app = rx.App(
    theme=rx.theme(
        appearance="dark",
        has_background=True,
        radius="medium",
        accent_color="blue",
    ),
)
app.add_page(index, title="SocketIO Dashboard")
