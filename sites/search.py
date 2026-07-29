from browser.manager import browserMgr
from sites import amazon, trendyol


def search(browser:browserMgr,query,itemcount=5,site:str=None):

    if(site.lower()=="amazon"):
        return amazon.search(browser,query,itemcount)
    if(site.lower()=="trendyol"):
        return trendyol.search(browser,query,itemcount)

    else:
        return "this site is not supported use available_sites tool for see which sites are available"
