import reflex as rx
import os

RAILWAY_PUBLIC_DOMAIN = os.getenv("RAILWAY_PUBLIC_DOMAIN", "")
API_URL = os.getenv("API_URL", "http://localhost:8000")

def _parse_cors_origins(raw: str) -> list[str]:
    defaults = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    # Auto-detect Railway domain
    if RAILWAY_PUBLIC_DOMAIN:
        defaults.append(f"https://{RAILWAY_PUBLIC_DOMAIN}")
    # Derive origin from API_URL (covers production)
    if API_URL and API_URL.startswith("http"):
        api_origin = API_URL.rstrip("/")
        if api_origin not in defaults:
            defaults.append(api_origin)
    if not raw:
        return defaults
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    return origins + defaults

config = rx.Config(
    app_name="biodiagnostico_app",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ],
    frontend_port=3000,
    backend_port=8000,
    api_url=API_URL,
    cors_allowed_origins=_parse_cors_origins(os.getenv("CORS_ALLOWED_ORIGINS", "")),
)
