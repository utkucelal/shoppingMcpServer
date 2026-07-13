from browser.manager import browserMgr
from sites import amazon


def addItem(browser:browserMgr,productID,quantity ,site:str=None):

    if(site=="Amazon"):
        return amazon.addItem(browser,productID,quantity)

    else:
        return "this site is not supported use available_sites tool for see which sites are available"