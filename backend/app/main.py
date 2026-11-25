from fastapi import FastAPI

app = FastAPI(
    title="Gestor de Recetas API",
    description="API para el seguimiento de recetas, retiros en farmacia y recordatorios.",
    version="0.1.0",
)


@app.get("/health", tags=["sistema"])
def verificar_estado() -> dict[str, str]:
    """Verifica que el servicio del backend este activo."""
    return {"status": "ok"}
