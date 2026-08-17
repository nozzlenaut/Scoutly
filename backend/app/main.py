import asyncio
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
from app.api.qa import router as qa_router
from app.api.prices import router as prices_router
from app.api.keh import router as keh_router
from app.api.books import router as books_router
from app.api.shipping import router as shipping_router
from app.api.diagnostics import router as diagnostics_router
from app.api.search_audit import router as search_audit_router
from app.services.database import database_health, initialize_database
from app.services.data_migrations import apply_data_migrations
from app.services.admin_auth import AdminAuthorizationMiddleware
from app.services.market_price_collector import price_tracking_enabled, run_tracked_price_collector
from app.version import APP_VERSION


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    apply_data_migrations()

    price_tracking_task: asyncio.Task[None] | None = None
    if price_tracking_enabled():
        price_tracking_task = asyncio.create_task(run_tracked_price_collector())

    try:
        yield
    finally:
        if price_tracking_task is not None:
            price_tracking_task.cancel()
            try:
                await price_tracking_task
            except asyncio.CancelledError:
                pass


app = FastAPI(title="PriceSift API", version=APP_VERSION, lifespan=lifespan)
app.add_middleware(AdminAuthorizationMiddleware)

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
app.include_router(qa_router, prefix="/api")
app.include_router(prices_router, prefix="/api")
app.include_router(keh_router, prefix="/api")
app.include_router(books_router, prefix="/api")
app.include_router(shipping_router, prefix="/api")
app.include_router(diagnostics_router, prefix="/api")
app.include_router(search_audit_router, prefix="/api")
app.include_router(ebay_notifications_router, prefix="/api")
