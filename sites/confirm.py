from browser.manager import browserMgr
from sites import amazon


def purchase(browser:browserMgr, code:str, pin:str, site:str=None):

    if(site=="Amazon"):
        return amazon.purchase(browser, code, pin)

    else:
        return "this site is not supported use available_sites tool for see which sites are available"