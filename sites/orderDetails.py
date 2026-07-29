from browser.manager import browserMgr
from sites import amazon, trendyol


def check(browser:browserMgr,orderID,site:str=None):

    if(site.lower()=="amazon"):
        return amazon.orderDetails(browser,orderID)
    if(site.lower()=="trendyol"):
        return trendyol.orderDetails(browser,orderID)

    else:
        return "this site is not supported use available_sites tool for see which sites are available"