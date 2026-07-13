import hashlib
import random

from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select

from browser.manager import browserMgr
from data.dbManager import fetch_orders,insert_orders
from data.confirmationDbManager import save_pending_confirmation, confirm_order, complete_order


def search(browser:browserMgr,query,itemcount=5):
    global price
    bot = browser
    browser.navigate("https://www.amazon.com.tr/s?k=" + query)

    allProducts = bot.driver.find_elements(By.CSS_SELECTOR, "[data-component-type='s-search-result']")

    products = []

    for product in allProducts:
        productDict = {}
        productDict["asin"] = product.get_attribute("data-asin")

        try:
            productDict["title"] = product.find_element(By.CSS_SELECTOR, "h2 span").text
        except:
            productDict["title"] = None

        try:
            productDict["price"] = product.find_element(By.CSS_SELECTOR, ".a-price-whole").text
        except:
            productDict["price"] = None

        try:
            productDict["rating"] = product.find_element(By.CSS_SELECTOR, ".a-icon_alt").text
        except:
            productDict["rating"] = None

        try:
            productDict["reviews"] = product.find_element(By.CSS_SELECTOR, ".a-size-mini.puis-normal-weight-text").text
        except:
            productDict["reviews"] = None

        try:
            productDict["url"] = f"https://www.amazon.com.tr/dp/{productDict['asin']}"
        except:
            productDict["url"] = None

        try:
            productDict["stock"] = product.find_element(By.CSS_SELECTOR, ".a-color-price").text
        except:
            productDict["stock"] = None

        products.append(productDict)

    products = products[:itemcount]

    bot.quit()
    return products

def check_cart(browser:browserMgr):
    if browser.uselogin == False:
        return "You need to login first"

    bot = browser
    browser.navigate("https://www.amazon.com.tr/cart")

    active_cart = bot.driver.find_element(By.ID, "sc-active-cart")

    item_elements = active_cart.find_elements(By.CSS_SELECTOR, "div.sc-list-item[data-asin]")

    items = []
    for el in item_elements:
        asin = el.get_attribute("data-asin")
        price_raw = el.get_attribute("data-price")
        quantity_raw = el.get_attribute("data-quantity")

        title = None
        try:
            title_el = el.find_element(By.CSS_SELECTOR, "span.a-truncate-full.a-offscreen")
            title = title_el.get_attribute("textContent").strip()
        except Exception:
            try:
                title_el = el.find_element(By.CSS_SELECTOR, "a.sc-product-title")
                title = title_el.get_attribute("textContent").strip()
            except Exception:
                pass

        price_display = None
        try:
            price_el = el.find_element(By.CSS_SELECTOR, "div.sc-apex-cart-price span.a-offscreen")
            price_display = price_el.get_attribute("textContent").strip()
        except Exception:
            try:
                price_el = el.find_element(By.CSS_SELECTOR, ".sc-item-price-block .a-price .a-offscreen")
                price_display = price_el.get_attribute("textContent").strip()
            except Exception:
                pass

        items.append({
            "asin": asin,
            "title": title,
            "price": float(price_raw) if price_raw else None,
            "price_display": price_display,
            "quantity": int(quantity_raw) if quantity_raw else None,
        })

    return items

def addItem(browser:browserMgr, productID:str, quantity:int):
    browser.navigate("https://www.amazon.com.tr/dp/" + productID)
    try:
        qty_dropdown = WebDriverWait(browser.driver, 10).until(
            EC.presence_of_element_located((By.ID, "quantity"))
        )
        select = Select(qty_dropdown)

        try:
            select.select_by_value(str(quantity))
        except NoSuchElementException:
            available = [o.get_attribute("value") for o in select.options]
            raise ValueError(
                f"İstenen adet ({quantity}) bu üründe seçilemiyor. "
                f"Mevcut seçenekler: {available}"
            )

        print(f"quanity set for {quantity}")


        product_name = _safe_text(browser.driver, By.ID, "productTitle", default=None)

        add_btn = WebDriverWait(browser.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "add-to-cart-button"))
        )
        browser.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_btn)
        add_btn.click()

        print(f"product added to cart: {product_name} x {quantity}")

        return {
            "product_name": product_name,
            "quantity": quantity,
        }

    except TimeoutException as e:
        print(f"one of the needed element not found: {e}")
        return None

def fetchOrderDB():
    return fetch_orders()

def fetchOrders(browser:browserMgr):

    browser.navigate("https://www.amazon.com.tr/gp/css/order-history")
    wait = browser.wait
    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".order-card.js-order-card"))
    )
    order_cards = browser.driver.find_elements(By.CSS_SELECTOR, ".order-card.js-order-card")
    orders = []
    for card in order_cards:
        order_data = {
            "order_id": None,
            "order_date": None,
            "items": []
        }
        #order date
        try:
            header_items = card.find_elements(By.CSS_SELECTOR, ".order-header__header-list-item")
            for item in header_items:
                try:
                    label = item.find_element(By.CSS_SELECTOR, ".a-color-secondary.a-text-caps").text.strip()
                    if "Sipariş Tarihi" in label:
                        date_el = item.find_element(
                            By.CSS_SELECTOR, ".a-row .a-size-base.a-color-secondary"
                        )
                        order_data["order_date"] = date_el.text.strip()
                        break
                except Exception:
                    continue
        except Exception:
            pass
        #Order ID
        try:
            order_id_el = card.find_element(By.CSS_SELECTOR, ".yohtmlc-order-id span:not(.a-color-secondary.a-text-caps)")
            order_data["order_id"] = order_id_el.text.strip()
        except Exception:
            try:
                slot_id = card.get_attribute("data-csa-c-slot-id")
                if slot_id:
                    order_data["order_id"] = slot_id.split(".")[-1]
            except Exception:
                pass

        #Product names
        product_links = card.find_elements(
            By.CSS_SELECTOR, ".yohtmlc-product-title a.a-link-normal"
        )

        for link_el in product_links:
            title = link_el.text.strip()
            href = link_el.get_attribute("href")

            asin = None
            if href:
                try:
                    asin = href.split("/dp/")[1].split("?")[0].split("/")[0]
                except IndexError:
                    asin = None

            order_data["items"].append({
                "title": title,
                "url": href,
                "asin": asin
            })



        orders.append(order_data)
        insert_orders(orders)

    return orders

def orderDetails(browser:browserMgr, orderID, ):

    browser.navigate("https://www.amazon.com.tr/gp/your-account/order-details?orderID=" + orderID)
    wait = browser.wait

    container = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-component="shipments"]'))
    )

    shipments = []

    shipment_boxes = container.find_elements(By.CSS_SELECTOR, ".a-box-group > .a-box")

    for box in shipment_boxes:
        shipment_data = {
            "status_title": None,
            "status_detail": None,
            "items": []
        }

        #Shipment status
        try:
            status_block = box.find_element(By.CSS_SELECTOR, '[data-component="shipmentStatus"]')

            try:
                title_el = status_block.find_element(By.CSS_SELECTOR, "h4.od-status-message .a-text-bold")
                shipment_data["status_title"] = title_el.text.strip()
            except Exception:
                pass

            try:
                detail_el = status_block.find_element(By.CSS_SELECTOR, "div.od-status-message span")
                shipment_data["status_detail"] = detail_el.text.strip()
            except Exception:
                pass
        except Exception:
            pass

        #Purchased item names
        try:
            items_block = box.find_element(By.CSS_SELECTOR, '[data-component="purchasedItems"]')
            title_blocks = items_block.find_elements(By.CSS_SELECTOR, '[data-component="itemTitle"]')

            for tb in title_blocks:
                try:
                    link_el = tb.find_element(By.CSS_SELECTOR, "a.a-link-normal")
                    title = link_el.text.strip()
                    href = link_el.get_attribute("href")

                    asin = None
                    if href:
                        try:
                            asin = href.split("/dp/")[1].split("?")[0].split("/")[0]
                        except IndexError:
                            asin = None

                    shipment_data["items"].append({
                        "title": title,
                        "url": href,
                        "asin": asin
                    })
                except Exception:
                    continue
        except Exception:
            pass

        shipments.append(shipment_data)

    return shipments

def track(browser:browserMgr, orderID):
    browser.navigate("https://www.amazon.com.tr/gp/your-account/order-details?orderID=" + orderID)
    browser.driver.find_element(By.XPATH, "//a[normalize-space()='Kargo takibi']").click()

    wait = browser.wait

    container = wait.until(
        EC.presence_of_element_located((By.ID, "tracking-events-container"))
    )

    trigger = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.tracking-events-modal-trigger"))
    )

    browser.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", trigger)

    try:
        trigger.click()
    except Exception:
        browser.driver.execute_script("arguments[0].click();", trigger)


    result = {"carrier": None, "tracking_id": None, "events": []}

    try:
        carrier_el = container.find_element(By.CLASS_NAME, "tracking-event-carrier-header")
        carrier_text = carrier_el.text.strip()
        result["carrier"] = carrier_text.split(":", 1)[-1].strip() if ":" in carrier_text else carrier_text
    except Exception:
        pass

    try:
        tracking_el = container.find_element(By.CLASS_NAME, "tracking-event-trackingId-text")
        tracking_text = tracking_el.text.strip()
        result["tracking_id"] = tracking_text.split(":", 1)[-1].strip() if ":" in tracking_text else tracking_text
    except Exception:
        pass

    date_groups = container.find_elements(
        By.XPATH,
        './/div[contains(@class,"a-row") and .//span[contains(@class,"tracking-event-date")]]'
    )

    for group in date_groups:
        try:
            date_text = group.find_element(By.CLASS_NAME, "tracking-event-date").text.strip()
        except Exception:
            continue

        event_rows = group.find_elements(
            By.XPATH,
            './/div[contains(@class,"a-row") and contains(@class,"a-spacing-large")]'
        )

        for row in event_rows:
            time_text = _safe_text(row, By.CLASS_NAME,"tracking-event-time")
            message_text = _safe_text(row, By.CLASS_NAME, "tracking-event-message")
            location_text = _safe_text(row, By.CLASS_NAME, "tracking-event-location")

            result["events"].append({
                "date": date_text,
                "time": time_text,
                "message": message_text,
                "location": location_text,
            })

    return result

def checkout_summary(browser:browserMgr):
    summary = _checkout_scrap(browser)
    code = _generate_confirmation_code(summary)
    pin = _generate_pin()

    save_pending_confirmation(code, pin, summary)

    summary = {
        "confirmation_code": code,
        "confirmation_link": f"/confirm/{code}",
        "adres": summary.get("adres", ""),
        "odeme_yontemi": summary.get("odeme_yontemi", ""),
        "urun": summary.get("urun", ""),
        "toplam": summary.get("toplam", ""),
    }
    print(summary)
    return summary

def purchase(browser:browserMgr, code:str, pin:str):
    # Verify PIN against database
    is_valid, message = confirm_order(code, pin)
    
    if not is_valid:
        print(f"Purchase failed: {message}")
        return {"success": False, "error": message}
    
    # PIN is valid, proceed with purchase
    try:
        btn = WebDriverWait(browser.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "submitOrderButtonId"))
        )
        browser.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        btn.click()
        print("Order Placed")
        order_id = _get_latest_order_id(browser)
        
        if order_id:
            complete_order(code, order_id)
            return {"success": True, "order_id": order_id}
        else:
            return {"success": False, "error": "Order placed but could not retrieve order ID"}
            
    except (NoSuchElementException, TimeoutException) as e:
        print(f"button not found: {e}")
        return {"success": False, "error": str(e)}

def _get_latest_order_id(browser) -> str | None:
    orders = fetchOrders(browser)

    if not orders:
        print("no orders found")
        return None

    latest_order = orders[0]
    order_id = latest_order.get("order_id")

    if not order_id:
        print("no orderID.")
        return None

    print(f"new order ID: {order_id}")
    return order_id

def _checkout_scrap(browser:browserMgr):
    browser.navigate("https://www.amazon.com.tr/gp/cart/view.html")
    checkout_btn = WebDriverWait(browser.driver, 10).until( EC.element_to_be_clickable((By.NAME, "proceedToRetailCheckout")))
    checkout_btn.click()

    checkout = {
        "adres": _safe_text(browser.driver, By.ID, "deliver-to-address-text"),
        "odeme_yontemi": _safe_text(browser.driver, By.ID, "payment-option-text-default"),
        "urun": _safe_text(browser.driver, By.ID, "col-item-block-description"),
        "toplam": _safe_text(browser.driver, By.ID, "subtotals-marketplace-table"),
    }
    return checkout

def _generate_confirmation_code(summary: dict):
    raw = "|".join([
        summary.get("adres", ""),
        summary.get("odeme_yontemi", ""),
        summary.get("urun", ""),
        summary.get("toplam", ""),
    ])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def _generate_pin():
    """Generate a random 4-digit PIN."""
    return str(random.randint(1000, 9999))

def _safe_text(driver, by, value, default="not found"):
    try:
        el = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((by, value))
        )
        return el.text.strip()
    except (NoSuchElementException, TimeoutException):
        return default