import json

from mcp.server.mcpserver import MCPServer

from browser.manager import browserMgr
from sites import registry as sites, checkout, confirm, addItem
from sites import search, cart, trackOrder, orderDetails, fetchOrder


app = MCPServer("shopping-mcp")


def _json(data) -> str:
    return json.dumps(data)


def _site_or_default(site: str | None) -> str:
    return site or "Amazon"


@app.tool()
async def available_sites() -> str:
    return _json(sites.available_sites())


@app.tool()
async def search_products(
    query: str,
    max_results: int = 5,
    site: str = "Amazon",
) -> str:
    site = _site_or_default(site)
    browser = browserMgr(url=sites.get_base_url(site), uselogin=False)
    try:
        browser.connect()
        result = search.search(
            browser,
            query,
            max_results,
            site=site,
        )
        return _json(result)
    finally:
        browser.quit()


@app.tool(name="Add_Item")
async def add_item(
    ProductID: str,
    quantity: int = 1,
    site: str = "Amazon",
) -> str:
    site = _site_or_default(site)
    browser = browserMgr(url=sites.get_base_url(site), uselogin=True)
    try:
        browser.connect()
        result = addItem.addItem(browser, ProductID, quantity, site)
        return _json(result)
    finally:
        browser.quit()


@app.tool(name="Check_Cart")
async def check_cart(site: str = "Amazon") -> str:
    site = _site_or_default(site)
    browser = browserMgr(url=sites.get_base_url(site), uselogin=True)
    try:
        browser.connect()
        result = cart.check_cart(browser, site=site)
        return _json(result)
    finally:
        browser.quit()


@app.tool(name="Fetch_Orders")
async def fetch_orders(
    site: str = "Amazon",
    refresh: bool = False,
) -> str:
    site = _site_or_default(site)

    if not refresh:
        result = fetchOrder.orders(refresh=False, site=site)
        return _json(result)

    browser = browserMgr(url=sites.get_base_url(site), uselogin=True)
    try:
        browser.connect()
        result = fetchOrder.orders(
            refresh=True,
            browser=browser,
            site=site,
        )
        return _json(result)
    finally:
        browser.quit()


@app.tool(name="Order_Details")
async def order_details(
    OrderID: str,
    site: str = "Amazon",
) -> str:
    site = _site_or_default(site)
    browser = browserMgr(url=sites.get_base_url(site), uselogin=True)
    try:
        browser.connect()
        result = orderDetails.check(browser, orderID=OrderID, site=site)
        return _json(result)
    finally:
        browser.quit()


@app.tool(name="Track_Order")
async def track_order(
    OrderID: str,
    site: str = "Amazon",
) -> str:
    site = _site_or_default(site)
    browser = browserMgr(url=sites.get_base_url(site), uselogin=True)
    try:
        browser.connect()
        result = trackOrder.track(browser, orderID=OrderID, site=site)
        return _json(result)
    finally:
        browser.quit()


@app.tool(name="Checkout")
async def checkout_cart(site: str = "Amazon") -> str:
    site = _site_or_default(site)
    browser = browserMgr(url=sites.get_base_url(site), uselogin=True)
    try:
        browser.connect()
        result = checkout.checkout(browser, site=site)
        return _json(result)
    finally:
        browser.quit()


@app.tool()
async def confirm_purchase(
    code: str,
    pin: str,
    site: str = "Amazon",
) -> str:
    site = _site_or_default(site)
    browser = browserMgr(url=sites.get_base_url(site), uselogin=True)
    try:
        browser.connect()
        result = confirm.purchase(
            browser,
            code=code,
            pin=pin,
            site=site,
        )
        return _json(result)
    finally:
        browser.quit()