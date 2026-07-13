import contextlib
from collections.abc import AsyncIterator

import uvicorn
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Mount
from starlette.types import Receive, Scope, Send

import api
from mcp_tools import app
from data.confirmationDbManager import init_confirmation_db


session_manager = StreamableHTTPSessionManager(app=app)


async def handle_mcp(scope: Scope, receive: Receive, send: Send) -> None:
    await session_manager.handle_request(scope, receive, send)


@contextlib.asynccontextmanager
async def lifespan(_: Starlette) -> AsyncIterator[None]:
    # Initialize confirmation database on startup
    init_confirmation_db()
    async with session_manager.run():
        yield


middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
]

starlette_app = Starlette(
    routes=[
        Mount("/mcp", app=handle_mcp),
        *api.routes,
    ],
    middleware=middleware,
    lifespan=lifespan,
)

if __name__ == "__main__":
    uvicorn.run(starlette_app, host="0.0.0.0"
                                    "", port=8000)
