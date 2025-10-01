from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Self
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import Settings, get_settings
from app.api import api_router
from app.core.database import session_manager
from app.models import *  # noqa: F403


import logging
logger = logging.getLogger("uvicorn.info")
logger.setLevel(logging.INFO)


class FastApp(FastAPI):
    def __init__(self, settings: Settings, **kwargs: Any):
        self.settings = settings
        kwargs.setdefault("lifespan", self._lifespan)
        super().__init__(**kwargs)

    @asynccontextmanager
    async def _lifespan(self, _: Self, /) -> AsyncGenerator[None, Any]:        
        yield
        engine = session_manager.engine
        await engine.dispose()

    def _setup_middlewares(self) -> None:
        self.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _setup_routers(self) -> None:
        self.include_router(api_router)

    def setup(self) -> None:
        super().setup()

        self._setup_middlewares()
        self._setup_routers()


app = FastApp(settings=get_settings())