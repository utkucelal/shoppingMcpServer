from browser.manager import browserMgr
from sites import amazon


def check(browser:browserMgr,orderID,site:str=None):

    if(site=="Amazon"):
        return amazon.orderDetails(browser,orderID)

    else:
        return "this site is not supported use available_sites tool for see which sites are available"