from browser.manager import browserMgr
from sites import amazon, trendyol


def check_cart(browser:browserMgr, site:str=None):

    if(site.lower()=="amazon"):
        return amazon.check_cart(browser)
    if(site.lower()=="trendyol"):
        return trendyol.check_cart(browser)

    else:
        return "this site is not supported use available_sites tool for see which sites are available"
