import json

from mcp import types
from mcp.server import Server

from browser.manager import browserMgr
from sites import registry as sites, checkout, confirm, addItem
from sites import search, cart, trackOrder, orderDetails, fetchOrder

app = Server("shopping-mcp")

@app.list_tools()
async def list_tools():
    return[
        types.Tool(
            name="available_sites",
            description="Returns a list of available sites for shopping",
            inputSchema={"type": "object", "properties": {}}
        ),

        types.Tool(
            name="search_products",
            description="Search products and return designated amount of product's information",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description" : "Search term"},
                    "max_results": {"type": "integer", "description" : "Max number of results default 5"},
                    "site": {"type": "string", "description" : "The site to search if the site name is unknown first run available_sites tool"},
                },
                "required": ["query"]
            }
        ),

        types.Tool(
            name="Add_Item",
            description="Add items to users cart",
            inputSchema={
                "type": "object",
                "properties": {
                    "ProductID": {"type": "string", "description": "ProductID for which product will be added can be provided by user or find with search_products tool"},
                    "quantity": {"type": "integer", "description": "Quantity of item will be added to users cart"},
                    "site": {"type": "string","description": "The site to search if the site name is unknown first run available_sites tool"},
                },
                "required": ["ProductID"]
            }
        ),

        types.Tool(
            name="Check_Cart",
            description="Returns the list of items in Cart",
            inputSchema={
                "type": "object",
                "properties": {
                    "site": {"type": "string", "description": "The site to check the cart on, if the site name is unknown see available sites first run available_sites tool. Defaults to Amazon"},
                },
            }
        ),

        types.Tool(
            name="Fetch_Orders",
            description="return orders with OrderID and product names in it",
            inputSchema={
                "type": "object",
                "properties": {
                    "site": {"type": "string",
                             "description": "The site to check the shipment details on, if the site name is unknown see available sites first run available_sites tool. Defaults to Amazon"},},
                    "refresh": {"type": "string",
                                "description": '(true/false) if user state a newly created order, ask for it specify or previous call made with false as parameter return empty set make this true for complete recheck otherwise keep false for faster result'}
            }
        ),

        types.Tool(
            name="Order_Details",
            description="return ordered Items and status briefly use Track_Order with same OrderID for more detailed status about shipment",
            inputSchema={
                "type": "object",
                "properties": {
                    "site": {"type": "string",
                             "description": "The site to check the order details on, if the site name is unknown see available sites first run available_sites tool. Defaults to Amazon"},
                    "OrderID": {"type": "string",
                             "description": "a OrderID for identify the order If is not provided from the user use fetch_orders tool"},
                },
                "required": ["OrderID"]
            }
        ),
        types.Tool(
            name="Track_Order",
            description="return ordered Items shipment status doesn't contain information about product names use Order_Details tool with same OrderID for more detailed status about product names" ,
            inputSchema={
                "type": "object",
                "properties": {
                    "site": {"type": "string",
                             "description": "The site to check the shipment details on, if the site name is unknown see available sites first run available_sites tool. Defaults to Amazon"},
                    "OrderID": {"type": "string",
                                "description": "a OrderID for identify the order If is not provided from the user use Fetch_Orders tool"},
                },
                "required":["OrderID"]
            }
        ),
        types.Tool(
            name="Checkout",
            description="Get order summary and confirmation link. Returns: products, address, payment method, total price, confirmation_code (hash), PIN, and confirmation_link URL. User must visit the confirmation_link, review order details, and provide the PIN to the AI agent. Then use confirm_purchase with both code and PIN to complete the order.",
            inputSchema={
                "type": "object",
                "properties": {
                    "site": {"type": "string",
                             "description": "The site to checkout from. Defaults to Amazon"},
                },
            }
        ),
        types.Tool(
            name="confirm_purchase",
            description="Place the order using confirmation code and PIN. After user provides the 4-digit PIN from the confirmation page, call this tool with both the confirmation_code and the PIN to complete the purchase. Returns order_id if successful.",
            inputSchema={
                "type": "object",
                "properties": {
                    "site": {"type": "string",
                             "description": "The site to purchase from. Defaults to Amazon"},
                    "code": {"type": "string",
                             "description": "The confirmation_code from the Checkout tool response"},
                    "pin": {"type": "string",
                            "description": "The 4-digit PIN that the user sees on the confirmation page"},
                },
                "required": ["code", "pin"]
            }
        ),
    ]

@app.call_tool()
async def call_tool(name:str, args:dict) -> list[types.TextContent]:

    if name == "available_sites":
        return [types.TextContent(type="text", text=json.dumps(sites.get_available_sites()))]

    if name == "search_products":
        browser = browserMgr(url=f"https://www.amazon.com.tr", uselogin=False)
        browser.connect()
        result = search.search(browser, args["query"], args.get("max_results", 5,),site=args["site"])
        browser.quit()
        return [types.TextContent(type="text", text=json.dumps(result))]

    if name == "Add_Item":
        browser = browserMgr(url=f"https://www.amazon.com.tr", uselogin=True)
        browser.connect()
        result = addItem.addItem(browser,args.get("ProductID"),args.get("quantity"),args.get("site","Amazon"))
        browser.quit()
        return [types.TextContent(type="text", text=json.dumps(result))]

    if name == "Check_Cart":
        browser = browserMgr(url=f"https://www.amazon.com.tr", uselogin=True)
        browser.connect()
        result = cart.check_cart(browser,site=args.get("site", "Amazon"))
        browser.quit()
        return [types.TextContent(type="text", text=json.dumps(result))]

    if name == "Fetch_Orders":
        if args.get("refresh") in (False, "false", "False"):
            result = fetchOrder.orders(refresh=args.get("refresh"),site=args.get("site", "Amazon"))
            return [types.TextContent(type="text", text=json.dumps(result))]

        browser = browserMgr(url=f"https://www.amazon.com.tr", uselogin=True)
        browser.connect()
        result = fetchOrder.orders(refresh=args.get("refresh", False), browser=browser, site=args.get("site", "Amazon"))
        browser.quit()
        return [types.TextContent(type="text", text=json.dumps(result))]

    if name == "Order_Details":
        browser = browserMgr(url=f"https://www.amazon.com.tr", uselogin=True)
        browser.connect()
        result = orderDetails.check(browser,orderID=args.get("OrderID"),site=args.get("site", "Amazon"))
        browser.quit()
        return [types.TextContent(type="text", text=json.dumps(result))]

    if name == "Track_Order":
        browser = browserMgr(url=f"https://www.amazon.com.tr", uselogin=True)
        browser.connect()
        result = trackOrder.track(browser,orderID=args.get("OrderID"),site=args.get("site", "Amazon"))
        browser.quit()
        return [types.TextContent(type="text", text=json.dumps(result))]

    if name == "Checkout":
        browser = browserMgr(url=f"https://www.amazon.com.tr", uselogin=True)
        browser.connect()
        result = checkout.checkout(browser,site=args.get("site", "Amazon"))
        browser.quit()
        return [types.TextContent(type="text", text=json.dumps(result))]

    if name == "confirm_purchase":
        browser = browserMgr(url=f"https://www.amazon.com.tr", uselogin=True)
        browser.connect()
        result = confirm.purchase(browser, code=args.get("code"), pin=args.get("pin"), site=args.get("site", "Amazon"))
        browser.quit()
        return [types.TextContent(type="text", text=json.dumps(result))]


    raise ValueError(f"Unknown tool: {name}")
