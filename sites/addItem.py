from browser.manager import browserMgr
from sites import amazon, trendyol


def addItem(browser:browserMgr,productID,quantity:int ,site:str=None):

    if(site.lower()=="amazon"):
        return amazon.addItem(browser,productID,quantity)
    if(site.lower()=="trendyol"):
        return trendyol.addItem(browser,productID,quantity)

    else:
        return "this site is not supported use available_sites tool for see which sites are available"