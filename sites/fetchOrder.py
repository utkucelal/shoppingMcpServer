from browser.manager import browserMgr
from sites import amazon


def orders(refresh,browser:browserMgr=None,site:str=None):

    if(site=="Amazon"):
        if refresh in (False, "false", "False"):
            return amazon.fetchOrderDB()
        else:
            return amazon.fetchOrders(browser)

    else:
        return "this site is not supported use available_sites tool for see which sites are available"