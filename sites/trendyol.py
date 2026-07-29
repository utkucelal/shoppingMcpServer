import re
import time
from urllib.parse import quote_plus

from selenium.common import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from browser.manager import browserMgr
from data.orderDbManager import insert_orders, fetch_orders


def search(browser: browserMgr, query, itemcount=5):
    bot = browser
    browser.navigate("https://www.trendyol.com/sr?q=" + quote_plus(query))

    allProducts = WebDriverWait(bot.driver, bot.timeout).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-card"))
    )

    products = []

    for product in allProducts:
        productDict = {}

        productDict["id"] = product.get_attribute("id")

        try:
            brand = product.find_element(By.CSS_SELECTOR, ".product-brand").text
            name = product.find_element(By.CSS_SELECTOR, ".product-name").text
            productDict["title"] = f"{brand} {name}".strip()
        except:
            productDict["title"] = None

        try:
            try:
                productDict["price"] = product.find_element(By.CSS_SELECTOR, ".sale-price").text
            except:
                try:
                    productDict["price"] = product.find_element(By.CSS_SELECTOR, ".price-section").text
                except:
                    productDict["price"] = product.find_element(By.CSS_SELECTOR, ".price-value").text
        except:
            productDict["price"] = None

        try:
            productDict["rating"] = product.find_element(By.CSS_SELECTOR, ".average-rating").text
        except:
            productDict["rating"] = None

        try:
            productDict["reviews"] = product.find_element(By.CSS_SELECTOR, ".total-count").text.strip("()")
        except:
            productDict["reviews"] = None

        try:
            productDict["url"] = product.get_attribute("href")
        except:
            productDict["url"] = None

        try:
            productDict["badge"] = product.find_element(By.CSS_SELECTOR, ".simplified-badge-text").text
        except:
            productDict["badge"] = None

        products.append(productDict)

        if len(products) >= itemcount:
            break

    products = products[:itemcount]

    return products

def check_cart(browser:browserMgr):
    if browser.uselogin == False:
        return "You need to login first"

    bot = browser
    browser.navigate("https://www.trendyol.com/sepetim")

    items = []

    try:
        item_elements = WebDriverWait(bot.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.merchant-item-container"))
        )
    except Exception:
        return items

    for el in item_elements:
        raw_id = el.get_attribute("id")
        item_id = raw_id.replace("basket-item@", "") if raw_id else None

        title = None
        try:
            brand = el.find_element(By.CSS_SELECTOR, "span.product-brand-name").text.strip()
            name = el.find_element(By.CSS_SELECTOR, "span.product-name").text.strip()
            title = f"{brand} {name}".strip()
        except Exception:
            pass

        price_display = None
        price_raw = None
        try:
            price_el = el.find_element(By.CSS_SELECTOR, "div.basket-product-price-text")
            price_display = price_el.text.strip()

            cleaned_price = price_display.replace(" TL", "").replace(".", "").replace(",", ".")
            price_raw = float(cleaned_price)
        except Exception:
            pass

        quantity_val = None
        try:
            quantity_el = el.find_element(By.CSS_SELECTOR, "input.quantity-selector")
            quantity_raw = quantity_el.get_attribute("value")
            quantity_val = int(quantity_raw) if quantity_raw else None
        except Exception:
            pass

        items.append({
            "item_id": item_id,
            "title": title,
            "price": price_raw,
            "price_display": price_display,
            "quantity": quantity_val,
        })

    return items

def addItem(browser:browserMgr, productID:str, quantity:int):
    url = f"https://www.trendyol.com/brand/product-name-p-{productID}"
    browser.navigate(url)

    try:
        title_el = WebDriverWait(browser.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1.product-title"))
        )
        product_name = title_el.text.strip()


        add_btn = WebDriverWait(browser.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.add-to-cart-button"))
        )

        browser.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_btn)

        for i in range(quantity):
            add_btn.click()
            print(f"Ürün sepete eklendi (Adet: {i + 1})")
            time.sleep(1)

        print(f"product added to cart: {product_name}")

        return {
            "product_name": product_name,
            "quantity": quantity,
        }

    except TimeoutException as e:
        print(f"one of the needed element not found: {e}")
        return None

def fetchOrderDB():
    return fetch_orders()

def fetchOrders(browser: browserMgr):
    browser.navigate("https://www.trendyol.com/hesabim/siparislerim")
    wait = browser.wait

    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".order-list-item-wrapper"))
    )

    order_cards = browser.driver.find_elements(By.CSS_SELECTOR, ".order-list-item-wrapper")
    orders = []

    for card in order_cards:
        order_data = {
            "order_id": None,
            "order_date": None,
            "order_summary": None,
            "items": []
        }

        try:
            order_data["order_id"] = card.get_attribute("data-ordernumber")
        except Exception:
            pass

        try:
            info_items = card.find_elements(By.CSS_SELECTOR, ".info-item")
            for item in info_items:
                title_el = item.find_element(By.CSS_SELECTOR, ".info-item-title")
                value_el = item.find_element(By.CSS_SELECTOR, ".info-item-value")

                if "Sipariş Tarihi" in title_el.text:
                    order_data["order_date"] = value_el.text.strip()
                elif "Sipariş Özeti" in title_el.text:
                    order_data["order_summary"] = value_el.text.strip()
        except Exception:
            pass

        product_links = card.find_elements(By.CSS_SELECTOR, ".image-list-container a")

        for link_el in product_links:
            href = link_el.get_attribute("href")

            product_id = None
            clean_title = None

            if href:
                try:
                    product_id = href.split("-p-")[1].split("?")[0]

                    path_part = href.split("?")[0].split("www.trendyol.com/")[-1]

                    if "-p-" in path_part:
                        slug_part = path_part.split("-p-")[0]
                        clean_title = slug_part.replace("/", "").replace("-", " ").strip()
                except IndexError:
                    product_id = None
                    clean_title = None
                order_data["items"].append({
                    "title": clean_title,
                    "url": href,
                    "product_id": product_id
                })
        if order_data["items"]:
            orders.append(order_data)
            insert_orders(orders)

    return orders

def orderDetails(browser:browserMgr, orderID):

    browser.navigate("https://www.trendyol.com/hesabim/siparislerim/" + orderID)
    wait = browser.wait

    container = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="shipments"]'))
    )

    shipments = []

    time.sleep(5)

    shipment_boxes = container.find_elements(By.CSS_SELECTOR, 'div[data-testid="shipment-card"]')

    for box in shipment_boxes:
        shipment_data = {
            "status_title": None,
            "status_detail": None,
            "items": []
        }

        try:
            status_block = box.find_element(By.CSS_SELECTOR, 'div[data-testid="status"]')

            try:
                title_el = status_block.find_element(By.CSS_SELECTOR, '[data-testid="status-text"]')
                shipment_data["status_title"] = title_el.text.strip()
            except Exception:
                pass

            try:
                detail_el = status_block.find_element(By.CSS_SELECTOR, '[data-testid="status-text"]')
                shipment_data["status_detail"] = detail_el.text.strip()
            except Exception:
                pass
        except Exception:

            pass

        try:
            items_block = box.find_element(By.CSS_SELECTOR, 'div[data-testid="product-list"]')
            title_blocks = items_block.find_elements(By.CSS_SELECTOR, "[data-testid='product-name']")

            for tb in title_blocks:
                try:
                    title = tb.text.strip()
                    shipment_data["items"].append({
                        "title": title,
                    })
                except Exception:
                    continue
        except Exception:
            pass

        shipments.append(shipment_data)

    return shipments
