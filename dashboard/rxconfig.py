import reflex as rx

config = rx.Config(
    app_name="dashboard",
    title="SocketIO Dashboard",
    frontend_port=3001,
    backend_port=8001,
    env=rx.Env.DEV,
)
