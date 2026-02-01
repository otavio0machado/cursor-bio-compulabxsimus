import reflex as rx
import os

def _parse_cors_origins(raw: str) -> list[str]:
    if not raw:
        return ["http://localhost:3000", "http://127.0.0.1:3000"]
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    return origins or ["http://localhost:3000", "http://127.0.0.1:3000"]

config = rx.Config(
    app_name="biodiagnostico_app",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ],
    # Configurações do servidor
    frontend_port=3000,
    backend_port=8000,
    api_url=os.getenv("API_URL", "http://localhost:8000"),
    cors_allowed_origins=_parse_cors_origins(os.getenv("CORS_ALLOWED_ORIGINS", "")),
)
