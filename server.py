import contextlib
from collections.abc import AsyncIterator

import uvicorn
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Mount

import api
from mcp_tools import app as mcp

from mcp.server.transport_security import TransportSecuritySettings

mcp_http_app = mcp.streamable_http_app(
    streamable_http_path="/",
    json_response=True,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=["ALLOWED_HOSTS"],
        allowed_origins=[],
    ),
)


@contextlib.asynccontextmanager
async def lifespan(_: Starlette) -> AsyncIterator[None]:
    async with mcp.session_manager.run():
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
        *api.routes,
        Mount("/mcp", app=mcp_http_app),
    ],
    middleware=middleware,
    lifespan=lifespan,
)


if __name__ == "__main__":
    uvicorn.run(
        starlette_app,
        host="0.0.0.0",
        port=8000,
    )