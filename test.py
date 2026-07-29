import asyncio

from mcp_tools import call_tool


async def test():
    result = await call_tool("search_products", args={"site": "amazon","query":"notebook bilgisayar","max_results": 10})
    print(result)


asyncio.run(test())
