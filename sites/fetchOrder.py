from browser.manager import browserMgr
from sites import amazon, trendyol


def orders(refresh,browser:browserMgr=None,site:str=None):

    if(site.lower()=="amazon"):
        if refresh in (False, "false", "False"):
            return amazon.fetchOrderDB()
        else:
            return amazon.fetchOrders(browser)
    if(site.lower()=="trendyol"):
        if refresh in (False, "false", "False"):
            return trendyol.fetchOrderDB()
        else:
            return trendyol.fetchOrders(browser)

    else:
        return "this site is not supported use available_sites tool for see which sites are available"