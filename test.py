import asyncio

from starlette.responses import JSONResponse

from mcp_tools import call_tool

async def test():
    await call_tool("Checkout", args={"site": "Amazon"})


asyncio.run(test())
