import asyncio
import os

import uvicorn
from beanie import init_beanie
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import ValidationError
from starlette import status
from starlette.responses import PlainTextResponse

from api.config import get_settings
from api.models.catalog import DatasetMetadataDOC
from api.models.user import Submission, User
from api.routes.catalog import router as catalog_router
from api.routes.discovery import router as discovery_router
from api.exceptions import RepositoryException


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RepositoryException)
async def http_exception_handler(request, exc):
    return PlainTextResponse(f"Repository exception response[{str(exc.detail)}]", status_code=exc.status_code)


@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc: ValidationError):
    return PlainTextResponse(f"Request data validation errors: {str(exc)}",
                             status_code=status.HTTP_400_BAD_REQUEST)


@app.on_event("startup")
async def startup_db_client():
    settings = get_settings()
    app.mongodb_client = AsyncIOMotorClient(settings.db_connection_string)
    app.mongodb = app.mongodb_client[settings.database_name]
    await init_beanie(database=app.mongodb, document_models=[DatasetMetadataDOC, User, Submission])


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()


@app.get("/")
async def health_check():
    return JSONResponse(status_code=200, content={"status": "healthy"})


app.include_router(catalog_router, tags=["Dataset"], prefix="/api/catalog")
app.include_router(discovery_router, tags=["Discovery"], prefix="/api/discovery")

parent_dir = os.path.dirname(__file__)
static_dir = os.path.join(parent_dir, "models/schemas")
app.mount("/api/schemas", StaticFiles(directory=static_dir), name="schemas")

openapi_schema = get_openapi(
    title="I-GUIDE Catalog API",
    version="1.0",
    description="Standardized interface with validation for managing catalog",
    routes=app.routes,
)
app.openapi_schema = openapi_schema


class Server(uvicorn.Server):
    def handle_exit(self, sig: int, frame) -> None:
        return super().handle_exit(sig, frame)


async def main():
    """Run FastAPI"""

    server = Server(config=uvicorn.Config(app, workers=1, loop="asyncio", host="0.0.0.0", port=8000, forwarded_allow_ips="*"))
    api = asyncio.create_task(server.serve())

    await asyncio.wait([api])


if __name__ == "__main__":
    asyncio.run(main())
