from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.catalog import router as catalog_router
from app.api.search import router as search_router
from app.api.ebay_notifications import router as ebay_notifications_router
from app.api.outbound import router as outbound_router
from app.api.feedback import router as feedback_router
from app.api.analytics import router as analytics_router
from app.services.database import database_health, initialize_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(title="Scoutly API", version="0.5.8", lifespan=lifespan)

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
def health_check() -> dict:
    storage = database_health()
    status = "ok" if not storage["configured"] or storage["connected"] else "degraded"
    return {"status": status, "storage": storage}


app.include_router(search_router, prefix="/api")
app.include_router(catalog_router, prefix="/api")
app.include_router(outbound_router, prefix="/api")
app.include_router(feedback_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(ebay_notifications_router, prefix="/api")
