
from starlette.concurrency import run_in_threadpool
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse
from starlette.routing import Route

from browser.manager import browserMgr
from sites import cart, checkout, confirm, addItem
from sites import registry
from sites import search, trackOrder, orderDetails, fetchOrder
from data.confirmationDbManager import get_pending_confirmation


async def get_sites(request: Request) -> JSONResponse:
    return JSONResponse(registry.get_available_sites())


def _run_search(query: str, max_results: int, site: str):
    browser = browserMgr(url="https://www.amazon.com.tr", uselogin=False)
    try:
        browser.connect()
        return search.search(browser, query, max_results, site=site)
    finally:
        browser.quit()


async def search_products(request: Request) -> JSONResponse:
    params = request.query_params
    query = params.get("query")
    if not query:
        return JSONResponse({"error": "query parameter is required"}, status_code=400)

    site = params.get("site", "Amazon")
    try:
        max_results = int(params.get("max_results", 5))
    except ValueError:
        return JSONResponse({"error": "max_results must be an integer"}, status_code=400)

    # Selenium is blocking; run it off the event loop.
    result = await run_in_threadpool(_run_search, query, max_results, site)
    return JSONResponse(result)


def _run_cart(site: str):
    browser = browserMgr(url="https://www.amazon.com.tr", uselogin=True)
    browser.connect()
    result = cart.check_cart(browser, site=site)
    browser.quit()
    return result


async def check_cart(request: Request) -> JSONResponse:
    site = request.query_params.get("site", "Amazon")
    result = await run_in_threadpool(_run_cart, site)
    return JSONResponse(result)


def _run_add_item(product_id: str, quantity: int, site: str):
    browser = browserMgr(url="https://www.amazon.com.tr", uselogin=True)
    browser.connect()
    result = addItem.addItem(browser, product_id, quantity, site)
    browser.quit()
    return result


async def add_item(request: Request) -> JSONResponse:
    params = request.query_params
    product_id = params.get("product_id")
    if not product_id:
        return JSONResponse({"error": "product_id parameter is required"}, status_code=400)
    
    try:
        quantity = int(params.get("quantity", 1))
    except ValueError:
        return JSONResponse({"error": "quantity must be an integer"}, status_code=400)
    
    site = params.get("site", "Amazon")
    result = await run_in_threadpool(_run_add_item, product_id, quantity, site)
    return JSONResponse(result)


def _run_fetch_orders(site: str, refresh: bool = False):
    if not refresh:
        return fetchOrder.orders(refresh=refresh, site=site)
    
    browser = browserMgr(url="https://www.amazon.com.tr", uselogin=True)
    browser.connect()
    result = fetchOrder.orders(refresh=refresh, browser=browser, site=site)
    browser.quit()
    return result


async def fetch_orders(request: Request) -> JSONResponse:
    site = request.query_params.get("site", "Amazon")
    refresh_param = request.query_params.get("refresh", "false").lower()
    refresh = refresh_param in ("true", "1", "yes")
    
    result = await run_in_threadpool(_run_fetch_orders, site, refresh)
    return JSONResponse(result)


def _run_order_details(order_id: str, site: str):
    browser = browserMgr(url="https://www.amazon.com.tr", uselogin=True)
    browser.connect()
    result = orderDetails.check(browser, orderID=order_id, site=site)
    browser.quit()
    return result


async def order_details(request: Request) -> JSONResponse:
    order_id = request.query_params.get("order_id")
    if not order_id:
        return JSONResponse({"error": "order_id parameter is required"}, status_code=400)
    
    site = request.query_params.get("site", "Amazon")
    result = await run_in_threadpool(_run_order_details, order_id, site)
    return JSONResponse(result)


def _run_track_order(order_id: str, site: str):
    browser = browserMgr(url="https://www.amazon.com.tr", uselogin=True)
    browser.connect()
    result = trackOrder.track(browser, orderID=order_id, site=site)
    browser.quit()
    return result


async def track_order(request: Request) -> JSONResponse:
    order_id = request.query_params.get("order_id")
    if not order_id:
        return JSONResponse({"error": "order_id parameter is required"}, status_code=400)
    
    site = request.query_params.get("site", "Amazon")
    result = await run_in_threadpool(_run_track_order, order_id, site)
    return JSONResponse(result)


def _run_checkout(site: str):
    browser = browserMgr(url="https://www.amazon.com.tr", uselogin=True)
    browser.connect()
    result = checkout.checkout(browser, site=site)
    browser.quit()
    return result


async def checkout_handler(request: Request) -> JSONResponse:
    site = request.query_params.get("site", "Amazon")
    result = await run_in_threadpool(_run_checkout, site)
    return JSONResponse(result)


def _run_confirm_purchase(code: str, pin: str, site: str):
    browser = browserMgr(url="https://www.amazon.com.tr", uselogin=True)
    browser.connect()
    result = confirm.purchase(browser, code=code, pin=pin, site=site)
    browser.quit()
    return result


async def confirm_purchase(request: Request) -> JSONResponse:
    code = request.query_params.get("code")
    pin = request.query_params.get("pin")
    
    if not code:
        return JSONResponse({"error": "code parameter is required"}, status_code=400)
    
    if not pin:
        return JSONResponse({"error": "pin parameter is required"}, status_code=400)
    
    site = request.query_params.get("site", "Amazon")
    result = await run_in_threadpool(_run_confirm_purchase, code, pin, site)
    return JSONResponse(result)


async def confirmation_page(request: Request) -> HTMLResponse:
    hash_code = request.path_params.get("hash")
    
    if not hash_code:
        return HTMLResponse("<h1>Error: No confirmation code provided</h1>", status_code=400)
    
    confirmation = get_pending_confirmation(hash_code)
    
    if not confirmation:
        return HTMLResponse("<h1>Error: Confirmation not found or expired</h1>", status_code=404)
    
    if confirmation["status"] != "pending":
        return HTMLResponse(f"<h1>Error: Order already {confirmation['status']}</h1>", status_code=400)
    
    pin = confirmation["pin"]
    product_details = confirmation["product_details"]
    price = confirmation["price"]
    address = confirmation["address"]
    payment_method = confirmation["payment_method"]
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Order Confirmation</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }}
            .container {{
                background: white;
                border-radius: 10px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                max-width: 600px;
                width: 100%;
                padding: 40px;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            h1 {{
                color: #333;
                font-size: 28px;
                margin-bottom: 10px;
            }}
            .subtitle {{
                color: #666;
                font-size: 14px;
            }}
            .order-details {{
                background: #f8f9fa;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
                border-left: 4px solid #667eea;
            }}
            .detail-row {{
                display: flex;
                justify-content: space-between;
                padding: 10px 0;
                border-bottom: 1px solid #e0e0e0;
            }}
            .detail-row:last-child {{
                border-bottom: none;
            }}
            .detail-label {{
                color: #666;
                font-weight: 500;
            }}
            .detail-value {{
                color: #333;
                word-break: break-word;
                text-align: right;
                max-width: 50%;
            }}
            .pin-section {{
                background: #fff3cd;
                border: 2px solid #ffc107;
                border-radius: 8px;
                padding: 20px;
                margin: 30px 0;
                text-align: center;
            }}
            .pin-label {{
                color: #856404;
                font-size: 14px;
                margin-bottom: 10px;
                font-weight: 500;
            }}
            .pin-value {{
                font-size: 48px;
                font-weight: bold;
                color: #ffc107;
                font-family: 'Courier New', monospace;
                letter-spacing: 10px;
                margin: 20px 0;
            }}
            .pin-instruction {{
                color: #856404;
                font-size: 12px;
                margin-top: 10px;
            }}
            .button-section {{
                margin-top: 30px;
                text-align: center;
            }}
            button {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 12px 30px;
                font-size: 16px;
                border-radius: 5px;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
            }}
            button:active {{
                transform: translateY(0);
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                color: #999;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✓ Order Summary</h1>
                <p class="subtitle">Please review your order details below</p>
            </div>
            
            <div class="order-details">
                <div class="detail-row">
                    <span class="detail-label">Products:</span>
                    <span class="detail-value">{product_details}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Address:</span>
                    <span class="detail-value">{address}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Payment Method:</span>
                    <span class="detail-value">{payment_method}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Total Price:</span>
                    <span class="detail-value">{price}</span>
                </div>
            </div>
            
            <div class="pin-section">
                <div class="pin-label">Your Confirmation PIN:</div>
                <div class="pin-value">{pin}</div>
                <div class="pin-instruction">
                    Copy this PIN and provide it to the AI agent to confirm your purchase
                </div>
            </div>
            
            <div class="button-section">
                <button onclick="copyPinToClipboard()">📋 Copy PIN to Clipboard</button>
            </div>
            
            <div class="footer">
                <p>Order Confirmation Code: {hash_code[:16]}...</p>
                <p>This page will expire after your purchase is confirmed</p>
            </div>
        </div>
        
        <script>
            function copyPinToClipboard() {{
                const pin = '{pin}';
                navigator.clipboard.writeText(pin).then(() => {{
                    alert('PIN copied! You can now share it with the AI agent.');
                }}).catch(() => {{
                    alert('Failed to copy PIN. Please copy it manually: ' + pin);
                }});
            }}
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)


routes = [
    Route("/api/sites", get_sites, methods=["GET"]),
    Route("/api/search", search_products, methods=["GET"]),
    Route("/api/cart", check_cart, methods=["GET"]),
    Route("/api/add-item", add_item, methods=["GET"]),
    Route("/api/fetch-orders", fetch_orders, methods=["GET"]),
    Route("/api/order-details", order_details, methods=["GET"]),
    Route("/api/track-order", track_order, methods=["GET"]),
    Route("/api/checkout", checkout_handler, methods=["GET"]),
    Route("/api/confirm-purchase", confirm_purchase, methods=["GET"]),
    Route("/confirm/{hash}", confirmation_page, methods=["GET"]),
]
