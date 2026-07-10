from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.catalog import router as catalog_router
from app.api.search import router as search_router

app = FastAPI(title="Scoutly API", version="0.2.3")

# Scoutly does not use cookies or browser credentials yet, so a public API CORS
# policy is the simplest way to support localhost, Vercel production domains,
# and Vercel preview deployments while we are in MVP development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(search_router, prefix="/api")
app.include_router(catalog_router, prefix="/api")
