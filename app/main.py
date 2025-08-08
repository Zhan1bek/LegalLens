from fastapi import FastAPI
from app.api.routers.documents import router as docs_router
from app.api.routers.analysis import router as analysis_router
from app.core.logging import logger
from app.core.config import get_settings
from app.api.routers.chat import router as chat_router


app = FastAPI(title="LegalLens AI")
app.include_router(docs_router)
app.include_router(analysis_router)
app.include_router(chat_router)
settings = get_settings()
