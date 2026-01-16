import reflex as rx

config = rx.Config(
    app_name="biodiagnostico_app",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ],
    # Configurações do servidor
    frontend_port=3000,
    backend_port=8000,
)