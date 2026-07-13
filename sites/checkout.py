from browser.manager import browserMgr
from sites import amazon


def checkout(browser:browserMgr, site:str=None):

    if(site=="Amazon"):
        return amazon.checkout_summary(browser)

    else:
        return "this site is not supported use available_sites tool for see which sites are available"